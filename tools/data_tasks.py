"""Repair one independently identified symbolic pointer initializer, never raw addresses."""
import re
from common import ROOT,identity,read_json,write_json,check_json,sha
from initializer_scope import field_span
from interface_tasks import contribution_fingerprint,affected_targets


def plan(source,report,item,ledger):
    name='pointer_'+source.rsplit('/',1)[-1].removesuffix('.c')+'_'+item['name']
    card={'schema':1,'task_kind':'DATA_POINTER','function':name,'source':source,'sources':[source],
          'object':item['name'],'diagnostic':item,'difficulty':'SUPERVISOR','priority':-30,
          'state':'DATA_POINTER_REPAIR','status':'INITIALIZER_DIFFER','difference_class':'STATIC_DATA_INITIALIZER',
          'body_edit_allowed':False,'changes':[],'source_identities':{source:identity(ROOT/source)},
          'affected_targets':[report['build']['target']],
          'begin_command':'python tools/interface_task.py begin '+name,'apply_command':'python tools/interface_task.py apply '+name,
          'verification_command':'python tools/interface_task.py check '+name,'promotion_command':'python tools/interface_task.py promote '+name}
    try:
        if item.get('errors'): raise ValueError('Initializer has unsupported or ambiguous relocations')
        if item.get('scope') not in (['GLOBAL'],('GLOBAL',)): raise ValueError('Only global initializer fields are mechanical')
        if affected_targets(ledger,[source])!=card['affected_targets']: raise ValueError('Initializer requires a broader source dependency closure')
        fields=item['fields']
        dependencies=[f['expected_reference']['root'] for f in fields if f.get('classification')=='OWNER_CONTENT_DEPENDENCY']
        if dependencies and not item['mismatch_byte_count']:
            card.update(state='WAITING_FOR_OWNER',difference_class='STATIC_DATA_OWNER_DEPENDENCY',depends_on=sorted(set(dependencies)))
            raise ValueError('Initializer already names the expected object; repair its owner dependency first')
        if len(fields)!=1: raise ValueError('Only one fully isolated pointer field is mechanical')
        field=fields[0]
        if field.get('classification')!='SYMBOLIC_POINTER_DIFFERENCE' or item['unresolved_byte_count']:
            raise ValueError('Pointer target difference is not independently established')
        if not field.get('candidate_target_path_agrees'): raise ValueError('Intended symbolic target has a different or ambiguous candidate type path')
        text=(ROOT/source).read_bytes().decode('cp1252'); a,b=field_span(text,item['name'],field['steps'])
        before=text[a:b]; expected='&'+field['expected_reference']['expression']; current='&'+field['candidate_reference']['expression']
        if re.sub(r'\s+','',before)!=current: raise ValueError('Source initializer is not the exact evidenced symbolic address expression')
        if not re.fullmatch(r'&[A-Za-z_]\w*(?:(?:\.[A-Za-z_]\w*)|(?:\[\d+\]))*',expected):
            raise ValueError('Intended reference is not a simple C object address')
        card.update(changes=[{'file':source,'start':a,'end':b,'before':before,'after':expected,
                             'reason':'Original typed pointer target and candidate member layout independently identify this symbolic address'}],
                    original_die=item['original_die'],field_offset=field['offset'],section_index=item['section_index'],
                    section_offset=item['candidate_offset']+field['offset'],field_size=4,
                    difficulty='CHEAP',priority=275,reason='One explicit symbolic pointer initializer differs; full ownership and every other allocated contribution must pass acceptance.',
                    edit_scope='Only the generated symbolic address expression. No address literals, body edits or other data changes.')
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def plans(ledger):
    cards=[]
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report'])
        for item in report.get('data_diagnostics',{}).get('objects',[]): cards.append(plan(source,report,item,ledger))
    return cards


def fingerprint(report,plan):
    """Candidate-to-candidate edit scope only; never used to establish a function match."""
    snapshot=report['data_snapshot']
    if snapshot['object']!=report['build']['object']: raise ValueError('Data gate snapshot object identity changed')
    result=contribution_fingerprint(report)
    sections={s['index']:s for s in report['object_sections']}; section=sections[plan['section_index']]
    offset=plan['section_offset']; size=plan['field_size']; content=bytearray.fromhex(snapshot['sections'][str(plan['section_index'])])
    if sha(content)!=section['sha256']: raise ValueError('Data snapshot differs from the verified section')
    if size!=4 or not 0<=offset<=len(content)-size: raise ValueError('Invalid authorized pointer field')
    content[offset:offset+size]=bytes(size)
    section_rows=[]
    for row in result['sections']:
        row=list(row)
        if row[0]==section['name']: row[-1]=sha(content)
        elif row[0]=='.text': row[-1]=next(s['sha256'] for s in report['object_sections'] if s['name']=='.text')
        section_rows.append(tuple(row))
    result['sections']=section_rows
    for relocation in result['relocations']:
        if relocation[0]==section['name'] and relocation[1]<offset+4 and relocation[1]+4>offset:
            if relocation[1]!=offset or relocation[2]!=6: raise ValueError('Unsupported relocation overlaps authorized pointer field')
    result['relocations']=[r for r in result['relocations'] if not (r[0]==section['name'] and r[1]==offset)]
    return result


def verify_owner(report,plan):
    owners=report.get('object_ownership',{}).get('accepted',[])
    matches=[o for o in owners if o['name']==plan['object'] and o['original_die']==plan['original_die']]
    if len(matches)!=1: raise ValueError('Repaired object lacks exact DWARF type and complete independently resolved initializer')
    owner=matches[0]
    if owner['candidate_offset']+plan['field_offset']!=plan['section_offset'] or owner['section_index']!=plan['section_index']:
        raise ValueError('Repaired object moved outside its authorized field')


def publish_data_tasks(ledger,check=False):
    emit=check_json if check else write_json; cards=plans(ledger); tasks=[]; active=set()
    for card in cards:
        path=ROOT/'docs/current/data-tasks'/(card['function']+'.json'); active.add(path); emit(path,card)
        tasks.append({k:card[k] for k in ('task_kind','function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')} | {'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    for path in (ROOT/'docs/current/data-tasks').glob('*.json'):
        if path not in active: emit(path,{'schema':1,'task_kind':'DATA_POINTER','function':path.stem,'state':'NOT_QUEUED','status':'NO_TYPED_INITIALIZER_DIFFERENCE','body_edit_allowed':False,'changes':[]})
    emit(ROOT/'docs/current/data-tasks.json',{'authority':'Typed initializer diagnostics; acceptance separately requires full independent object ownership','tasks':tasks})
