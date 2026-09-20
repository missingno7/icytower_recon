"""Bounded local declaration repairs from compiler locations and original DWARF."""
import re
from pathlib import Path
from common import ROOT,identity,read_json,write_json,check_json
from type_graph import graph
from source_scope import sanitized,function_span
from interfaces import normalize
from interface_tasks import contribution_fingerprint,affected_targets
from audit_signedness import type_differences

WORDS={'const','signed','unsigned','void','char','short','int','long','float','double'}
DECL=re.compile(r'^[ \t]*(?:register\s+)?(?P<declaration>(?P<type>(?:(?:const|volatile|signed|unsigned|void|char|short|int|long|float|double)\s+)+)(?P<pointers>(?:\*\s*(?:const\s*)?)*)?(?P<name>[A-Za-z_]\w*)(?P<arrays>(?:\s*\[\s*\d*\s*\])*)?)(?P<tail>\s*(?:=.*)?;[ \t\r]*)$')


def declaration_span(text,function,variable):
    line=variable.get('declaration_line')
    if not isinstance(line,int) or line<1: raise ValueError('Candidate DWARF has no declaration line')
    lines=text.splitlines(keepends=True)
    if line>len(lines): raise ValueError('Declaration line is outside source')
    clean=sanitized(text); start=sum(map(len,lines[:line-1])); end=start+len(lines[line-1].rstrip('\r\n'))
    a,b=function_span(text,function)
    if not a<start<end<b: raise ValueError('Declaration does not lie inside the target body')
    m=DECL.fullmatch(clean[start:end])
    if not m or m['name']!=variable['name']: raise ValueError('Only one simple compiler-located builtin declaration is mechanical')
    depth=0
    for c in m['tail']:
        depth+=(c in '([{')-(c in ')]}')
        if c==',' and depth==0: raise ValueError('Multiple declarators require separate scope evidence')
    if re.search(r'\[\s*\]',m['arrays'] or ''):
        raise ValueError('Inferred array extent may reflect initializer content; do not pad it with a declaration edit')
    written=(m['type'] or '')+(m['pointers'] or '')+(m['arrays'] or '')
    if normalize(written)!=normalize(variable['type']): raise ValueError('Source declaration and compiled type disagree')
    return start+m.start('declaration'),start+m.end('declaration')


def storage_shape(text):
    words=re.findall(r'[A-Za-z_]\w*',text)
    if set(words)-WORDS: return None
    if any(x in words for x in ('float','double')): family='floating'
    elif 'void' in words: family='void'
    else: family='integer'
    return family,text.count('*'),tuple(re.findall(r'\[\s*(\d*)\s*\]',text))


def plan(source,report,row,original,candidate,old_die,ledger):
    function=row['name']; variable=original['name']; name='decl_'+Path(source).stem+'_'+function+'_'+variable
    g=graph(); expected=g.declaration(old_die.get('type_ref'),variable)
    card={'schema':1,'task_kind':'LOCAL_DECLARATION','function':name,'target_function':function,'source':source,'sources':[source],
          'target':report['build']['target'],'variable':variable,'original_constant_value':old_die['resolved'].get('DW_AT_const_value'),'original':original,'candidate':candidate,'expected_declaration':expected,
          'status':'LOCAL_TYPE_DIFFERS','state':'LOCAL_DECLARATION_REPAIR','difference_class':'LOCAL_TYPE_DECLARATION',
          'difficulty':'SUPERVISOR','priority':-30,'body_edit_allowed':False,'changes':[],
          'source_identities':{source:identity(ROOT/source)},'function_status':row['status'],'first_difference':row.get('first_difference'),
          'function_card':'docs/current/functions/'+Path(source).stem+'/'+function+'.json',
          'begin_command':'python tools/interface_task.py begin '+name,'apply_command':'python tools/interface_task.py apply '+name,
          'verification_command':'python tools/interface_task.py check '+name,'promotion_command':'python tools/interface_task.py promote '+name,
          'acceptance':'Complete DWARF declaration equality plus unchanged emitted contributions, or strict exact target-function proof with preserved non-code contributions. No partial machine-code match claim.'}
    try:
        if old_die['tag']!='DW_TAG_variable' or candidate.get('role')!='DW_TAG_variable':
            card.update(state='INTERFACE_REQUIRED',difference_class='INTERFACE_DECLARATION')
            raise ValueError('Parameter differences belong to an interface task')
        if not row['workflow']['body_edit_allowed']:
            card['state']='BODY_PROTECTED'; raise ValueError('The function body is protected by its proof or supervisor routing')
        if g.dies[old_die['parent']]['tag']!='DW_TAG_subprogram' or not candidate.get('function_scope'):
            raise ValueError('Only unique function-scope locals are mechanical; lexical/inlined correspondence needs review')
        if candidate.get('address') is not None or old_die.get('address') is not None: raise ValueError('Static/global storage requires a data task')
        file=candidate.get('declaration_file')
        if not file or (ROOT/file).resolve()!=(ROOT/source).resolve(): raise ValueError('DWARF declaration belongs to a different or unknown source file')
        text=(ROOT/source).read_bytes().decode('cp1252')
        if re.search(r'^\s*#\s*(?:line\b|\d)',text,re.M): raise ValueError('Source line directives require explicit mapping')
        a,b=declaration_span(text,function,candidate)
        card['declaration_evidence']={'line':candidate['declaration_line'],'before':text[a:b],'after':expected}
        shape=storage_shape(original['type'])
        if not shape or shape!=storage_shape(candidate['type']) or g.size(old_die['type_ref'])!=candidate.get('byte_size'):
            raise ValueError('Storage width, pointer topology or array extent changes need supervisor source review')
        if shape[0]=='floating': raise ValueError('Floating-point type changes require x87 source-shape review')
        targets=affected_targets(ledger,[source])
        if targets!=[report['build']['target']]: raise ValueError('Local declaration affects a broader dependency closure')
        card.update(changes=[{'file':source,'start':a,'end':b,'before':text[a:b],'after':expected,
                             'reason':'Unique function-scope local has an independently recorded original builtin type and a compiler-located declaration'}],
                    affected_targets=targets,difficulty='CHEAP',priority=230,
                    reason='One same-storage builtin declaration; all other source is immutable and acceptance preserves emission or requires an exact function.',
                    edit_scope='Only the generated local declaration span. Do not edit initializers, expressions, other locals, parameters or flags.')
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def plans(ledger):
    g=graph(); units={u['source']:u for u in read_json(ROOT/'src/units.json')}; cards=[]
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report'])
        for row in report['functions']:
            if row['status']=='FUNCTION_MATCH': continue
            f=next(f for f in units[source]['functions'] if f['name']==row['name'])
            if not f.get('die'): continue
            old_dies=[v for v in g.descendants(f['die']) if v['tag'] in ('DW_TAG_variable','DW_TAG_formal_parameter')]
            original=[g.variable(v) for v in old_dies]
            candidate=report['candidate_debug']['functions'].get(row['name'],{}).get('variables',[])
            for diff in type_differences(original,candidate):
                old=next(v for v in original if v['die']==diff['original_die']); new=next(v for v in candidate if v['die']==diff['candidate_die'])
                cards.append(plan(source,report,row,old,new,g.dies[diff['original_die']],ledger))
    return cards


def verify_local(report,plan):
    variables=report['candidate_debug']['functions'][plan['target_function']]['variables']
    found=[v for v in variables if v.get('name')==plan['variable']]
    if len(found)!=1 or found[0].get('role')!='DW_TAG_variable' or not found[0].get('function_scope') or normalize(found[0]['type'])!=normalize(plan['original']['type']):
        raise ValueError('Fresh local declaration does not equal the original DWARF type')
    file=found[0].get('declaration_file')
    if not file or (ROOT/file).resolve()!=(ROOT/plan['source']).resolve(): raise ValueError('Fresh local comes from an unexpected source')


def emission_effect(before,after,plan):
    old=contribution_fingerprint(before); new=contribution_fingerprint(after)
    if old==new: return 'EMISSION_PRESERVED'
    row=next(r for r in after['functions'] if r['name']==plan['target_function'])
    if row['status']!='FUNCTION_MATCH':
        raise ValueError('Local declaration changed emitted code; target remains '+row['status']+'; first difference '+str(row.get('first_difference')))
    from promote_function import eligible
    if row['workflow']['state'] not in ('FUNCTION_MATCH','BODY_MATCH_LAYOUT_BLOCKED'): raise ValueError('Exact local repair has an invalid workflow claim')
    eligible(after,plan['target_function'],row['workflow']['state'])
    def noncode(fp):
        return {'sections':[r for r in fp['sections'] if r[0]!='.text'],
                'relocations':[r for r in fp['relocations'] if r[0]!='.text'],
                'defined':[r for r in fp['defined'] if r[1]!='.text'],'common':fp['common']}
    if noncode(old)!=noncode(new): raise ValueError('Exact local repair changed non-code contributions or their relocations')
    def owners(report): return {(tuple(o['scope']),o['name'],o['original_va'],o['size']) for o in report.get('object_ownership',{}).get('accepted',[])}
    if owners(before)-owners(after): raise ValueError('Previously proven data ownership regressed')
    return 'EXACT_FUNCTION'


def publish_locals(ledger,check=False):
    emit=check_json if check else write_json; tasks=[]; routed=[]; active=set()
    for card in plans(ledger):
        path=ROOT/'docs/current/local-declarations'/(card['function']+'.json'); active.add(path); emit(path,card)
        if card['state'] in ('INTERFACE_REQUIRED','BODY_PROTECTED'):
            redirect='docs/current/interfaces/'+card['target_function']+'.json' if card['state']=='INTERFACE_REQUIRED' else card['function_card']
            routed.append({'function':card['function'],'target_function':card['target_function'],'source':card['source'],'reason':card['reason'],'candidate_card':path.relative_to(ROOT).as_posix(),'redirect':redirect})
            continue
        tasks.append({k:card.get(k) for k in ('task_kind','function','target_function','source','sources','target','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')} | {'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    for path in (ROOT/'docs/current/local-declarations').glob('*.json'):
        if path not in active: emit(path,{'schema':1,'task_kind':'LOCAL_DECLARATION','function':path.stem,'state':'NOT_QUEUED','status':'NO_BUILTIN_LOCAL_TYPE_DIFFERENCE','body_edit_allowed':False,'changes':[]})
    emit(ROOT/'docs/current/local-declaration-tasks.json',{'authority':'Original DWARF types and candidate compiler source locations; exact byte proofs remain separate','tasks':tasks,'routed_evidence':routed})
