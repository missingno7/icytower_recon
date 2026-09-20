"""Bounded scalar-to-historical-aggregate COMMON migrations; never layout placement."""
import copy
import re
from pathlib import Path
from common import ROOT,read_json,write_json,check_json,identity,run
from storage_diagnostics import diagnose
from type_views import shape_key
from source_scope import sanitized,body_hash
from source_order import definition_spans
from interface_tasks import patch_text,contribution_fingerprint


def source_edits(text,source,old,new,report,header):
    name=old['name']; first=old['layout']['members'][0]
    if old['layout'].get('qualifiers') or first['offset']!=0 or first['bitfield'] or not first['name'] or shape_key(first['layout'])!=shape_key(new['layout']):
        raise ValueError('No unqualified offset-zero member preserving the entire old scalar type')
    clean=sanitized(text); lines=text.splitlines(keepends=True); line=new.get('declaration_line')
    if not isinstance(line,int) or not 1<=line<=len(lines): raise ValueError('Missing compiler declaration line')
    start=sum(map(len,lines[:line-1])); end=start+len(lines[line-1].rstrip('\r\n'))
    if not re.fullmatch(r'\s*'+re.escape(new['type'])+r'\s+'+re.escape(name)+r'\s*;',clean[start:end]):
        raise ValueError('Only one plain uninitialized scalar definition is supported')
    edits=[{'file':source,'start':start,'end':end,'before':text[start:end],'after':old['type']+' '+name+';','role':'global_declaration'},
           {'file':source,'start':0,'end':0,'before':'','after':'#include "'+header.removeprefix('include/')+'"\n','role':'canonical_header'}]
    spans=definition_spans(text); rows={f['name']:f for f in report['functions']}; adapted=set()
    for m in re.finditer(r'\b'+re.escape(name)+r'\b',clean):
        if start<=m.start()<end: continue
        prefix=clean[:m.start()].rstrip()
        # Preserve an unambiguous address-of-global initializer as an object pointer.
        if prefix.endswith('&') and (not prefix[:-1].rstrip() or prefix[:-1].rstrip()[-1] in '=([{,:?'): continue
        owners=[s for s in spans if s['start']<m.start()<s['end']]
        if len(owners)!=1: raise ValueError('Global use outside a uniquely identified function or address initializer')
        function=owners[0]['name']; row=rows[function]
        if row['workflow']['state']=='BODY_MATCH_LAYOUT_BLOCKED': raise ValueError('Layout-proven bodies cannot be adapted: '+function)
        if any(v['name']==name for v in report['candidate_debug']['functions'][function]['variables']): raise ValueError('Local shadow requires lexical binding evidence')
        if prefix.endswith(('.', '->')) or re.search(r'\b(?:sizeof|__typeof__|typeof)\s*\(?\s*$',prefix): raise ValueError('Member/size/type query is outside scalar-access adaptation')
        edits.append({'file':source,'start':m.start(),'end':m.end(),'before':name,'after':name+'.'+first['name'],
                      'role':'offset_zero_scalar_access','function':function})
        adapted.add(function)
    return edits,sorted(adapted)


def plan(source,report,item):
    old,new=item['original'],item['candidate']; name='global_type_'+Path(source).stem+'_'+old['name']; target=report['build']['target']
    card={'schema':1,'task_kind':'GLOBAL_TYPE','function':name,'object':old['name'],'source':source,'sources':[source],
          'target':target,'affected_targets':[target],'difficulty':'SUPERVISOR','priority':-30,'changes':[],
          'state':'GLOBAL_TYPE_REPAIR','status':'GLOBAL_DECLARATION_DIFFERS','difference_class':'GLOBAL_DECLARATION_LAYOUT',
          'body_edit_allowed':False,'original_die':old['die'],'original':old,'candidate':new,
          'source_identities':{source:identity(ROOT/source)},'begin_command':'python tools/interface_task.py begin '+name,
          'apply_command':'python tools/interface_task.py apply '+name,'verification_command':'python tools/interface_task.py check '+name,
          'promotion_command':'python tools/interface_task.py promote '+name}
    try:
        if old['scope']!=['GLOBAL'] or new['scope']!=['GLOBAL'] or new.get('section')!='COMMON' or len(new['coff'])!=1: raise ValueError('Only uniquely declared global COMMON storage is supported')
        if new['layout']['kind']!='base_type' or old['layout']['kind']!='structure_type' or not old['layout'].get('members'): raise ValueError('Not a scalar-to-aggregate declaration')
        if not old['type'].isidentifier(): raise ValueError('Historical type has no named generated header')
        header='include/recovered/'+old['type']+'.h'
        if not (ROOT/header).is_file(): raise ValueError('Historical generated header is unavailable')
        for folder in ('src','include'):
            for path in (ROOT/folder).rglob('*'):
                if path.suffix not in ('.c','.h') or path.relative_to(ROOT).as_posix()==source: continue
                if re.search(r'\b'+re.escape(old['name'])+r'\b',sanitized(path.read_bytes().decode('cp1252'))): raise ValueError('Additional maintained source uses require a cross-CU plan')
        text=(ROOT/source).read_bytes().decode('cp1252'); changes,adapted=source_edits(text,source,old,new,report,header)
        card.update(header=header,expected_layout=old['layout'],changes=changes,adapted_functions=adapted,
                    difficulty='CHEAP',priority=280,reason='Generated aggregate plus evidenced offset-zero scalar access adaptation; strict allocated-contribution and exact-neighbor preservation required.',
                    edit_scope='Only generated declaration/header/member-access spans. Never adapt a BODY_MATCH_LAYOUT_BLOCKED function.')
    except ValueError as exc: card['reason']=str(exc)
    path=ROOT/'docs/current/interface-blocks.json'
    if path.exists() and name in read_json(path): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(path)[name])
    return card


def plans(ledger):
    result=[]
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report'])
        for item in diagnose(report)['objects']:
            old,new=item['original'],item['candidate']
            if not new or old['scope']!=['GLOBAL'] or old['layout']['kind']!='structure_type' or new['layout']['kind']!='base_type': continue
            result.append(plan(source,report,item))
    return result


def allocation_witness(report,plan):
    """Compile only the generated type/declaration under the same locked CU flags."""
    from binary import Binary
    from build import COMPILERS
    folder=Path(report['build']['command'][-1]).parent/'common-witness'; folder.mkdir(parents=True,exist_ok=True)
    source=folder/'declaration.c'; obj=folder/'declaration.o'; header=ROOT/plan['header']
    header_before=identity(header)
    source.write_text('#include "'+plan['header'].removeprefix('include/')+'"\n'+plan['original']['type']+' '+plan['object']+';\n',encoding='ascii')
    source_before=identity(source); args=list(report['build']['command'])
    for flag,value in [('-MF',folder/'unit.d'),('-aux-info',folder/'interfaces.aux'),('-c',source),('-o',obj)]: args[args.index(flag)+1]=str(value)
    run(args,toolchain=COMPILERS[report['build']['compiler']])
    binary=Binary(obj); rows=[s for s in binary.symbols if s['name']=='_'+plan['object']]
    if len(rows)!=1 or rows[0]['section']!=0 or rows[0]['storage_class']!=2 or rows[0]['value']<plan['original']['size']: raise ValueError('Standalone compiler witness lacks the expected COMMON declaration')
    if identity(header)!=header_before or identity(source)!=source_before: raise ValueError('Allocation witness inputs changed')
    result={'logical_dwarf_bytes':plan['original']['size'],'compiler_common_bytes':rows[0]['value'],
            'command':args,'object':identity(obj),'source':source_before,'header':header_before,
            'limit':'Locked-compiler allocation for this declaration only. No original COMMON order, BSS layout or object equality claim.'}
    write_json(folder/'witness.json',result)
    return result


def fingerprint(report,plan,allocation):
    result=copy.deepcopy(contribution_fingerprint(report)); symbol='_'+plan['object']
    matches=[r for r in result['common'] if r[0]==symbol]
    if len(matches)!=1 or matches[0][1]!=allocation: raise ValueError('Unexpected common allocation identity/size')
    for r in result['relocations']:
        if r[3]==symbol and r[4]==0 and r[5]!=allocation: raise ValueError('COMMON relocation metadata disagrees with the allocation')
    result['common']=[(n,0 if n==symbol else v,c) for n,v,c in result['common']]
    result['relocations']=[(*r[:5],0) if r[3]==symbol and r[4]==0 else r for r in result['relocations']]
    return result


def verify(before,after,plan,original_text,current_text):
    item=next((r for r in diagnose(before)['objects'] if r['original']['die']==plan['original_die']),None)
    if not item or item['original']!=plan['original'] or item['candidate']!=plan['candidate']: raise ValueError('Global type plan is not the original/current declaration evidence')
    expected_header='include/recovered/'+item['original']['type']+'.h'
    if (plan['object']!=item['original']['name'] or plan['expected_layout']!=item['original']['layout'] or
        plan['header']!=expected_header or plan['source']!=before['build']['config']['source'] or
        plan['source']!=after['build']['config']['source'] or plan['target']!=before['build']['target'] or
        plan['target']!=after['build']['target']):
        raise ValueError('Global type plan redirected its independently evidenced owner, layout, header or CU')
    changes,adapted=source_edits(original_text,plan['source'],item['original'],item['candidate'],before,plan['header'])
    if changes!=plan['changes'] or adapted!=plan['adapted_functions'] or patch_text(original_text,changes)!=current_text: raise ValueError('Source exceeds regenerated global-type recipe')
    from generate_types import outputs
    header=ROOT/plan['header']
    if header.read_text(encoding='utf8')!=outputs()[header] or plan['header'] not in after['build']['local_inputs']: raise ValueError('Canonical header is not the compiled historical declaration')
    new=[r for r in after['candidate_debug']['storage'] if r['name']==plan['object'] and r['scope']==['GLOBAL']]
    if len(new)!=1 or shape_key(new[0]['layout'])!=shape_key(plan['expected_layout']) or new[0].get('section')!='COMMON' or len(new[0]['coff'])!=1: raise ValueError('Fresh global type/common allocation does not match DWARF')
    witness=allocation_witness(after,plan)
    old_allocation=plan['candidate']['coff'][0]['value']
    if fingerprint(before,plan,old_allocation)!=fingerprint(after,plan,witness['compiler_common_bytes']): raise ValueError('Global type repair changed code/data/relocations/other storage beyond the established candidate clear-order projection')
    old_owners={(tuple(o['scope']),o['name'],o['original_va'],o['size']) for o in before.get('object_ownership',{}).get('accepted',[])}
    new_owners={(tuple(o['scope']),o['name'],o['original_va'],o['size']) for o in after.get('object_ownership',{}).get('accepted',[])}
    if old_owners-new_owners: raise ValueError('Previously proven data owner regressed')
    return {name:(body_hash(original_text.replace('\r\n','\n'),name),body_hash(current_text.replace('\r\n','\n'),name)) for name in adapted}


def publish(ledger,check=False):
    emit=check_json if check else write_json; tasks=[]; active=set()
    for card in plans(ledger):
        path=ROOT/'docs/current/global-types'/(card['function']+'.json'); active.add(path); emit(path,card)
        tasks.append({k:card.get(k) for k in ('task_kind','function','source','sources','target','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')}|{'size':card['original']['size'],'candidate_card':path.relative_to(ROOT).as_posix()})
    for path in (ROOT/'docs/current/global-types').glob('*.json'):
        if path not in active: emit(path,{'state':'NOT_QUEUED','status':'NO_SCALAR_AGGREGATE_TASK','body_edit_allowed':False,'changes':[]})
    emit(ROOT/'docs/current/global-type-tasks.json',{'authority':'Original/current DWARF, generated declarations, scoped source adaptation and fresh strict acceptance','tasks':tasks})
