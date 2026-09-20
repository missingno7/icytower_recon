"""Move one misplaced file-static BSS declaration into its DWARF function scope."""
import re
import json
from pathlib import Path
from common import ROOT,identity,read_json,write_json,check_json
from source_scope import sanitized,function_span
from interface_tasks import affected_targets,contribution_fingerprint
from storage_diagnostics import diagnose


def edits(text,function,old,new,debug):
    name=old['name']; clean=sanitized(text)
    if re.search(r'^\s*#\s*(?:line\b|\d)',text,re.M): raise ValueError('Line directives require source mapping')
    lines=text.splitlines(keepends=True); line=new.get('declaration_line')
    if not isinstance(line,int) or not 1<=line<=len(lines): raise ValueError('Missing declaration location')
    a=sum(map(len,lines[:line-1])); b=a+len(lines[line-1])
    declaration=lines[line-1].strip()
    if not re.fullmatch(r'static\s+(?:(?:char|signed|unsigned|short|int|long)\s+)+'+re.escape(name)+r'(?:\s*\[\s*\d+\s*\])*\s*;',declaration):
        raise ValueError('Only a simple uninitialized builtin static is mechanical')
    if clean[:a].count('{')!=clean[:a].count('}'): raise ValueError('Declaration is not at file scope')
    start,end=function_span(text,function)
    if not (b<=start or a>=end): raise ValueError('Declaration is already inside target')
    remaining=list(clean)
    def hide(lo,hi): remaining[lo:hi]=' '*(hi-lo)
    hide(a,b); hide(start,end)
    shadowed=[]
    for other,info in debug['functions'].items():
        if other==function: continue
        hits=[v for v in info['variables'] if v.get('name')==name]
        if len(hits)!=1 or hits[0].get('address') is not None: continue
        v=hits[0]; n=v.get('declaration_line')
        if v.get('declaration_file')!=new.get('declaration_file'): continue
        if not isinstance(n,int) or not 1<=n<=len(lines): continue
        lo,hi=function_span(text,other); da=sum(map(len,lines[:n-1])); db=da+len(lines[n-1])
        if not lo<da<db<hi: continue
        from local_declarations import declaration_span
        try: declaration_span(text,other,v)
        except ValueError: continue
        # Establish the actual C block, including loop-local shadows. Nothing before
        # the declaration or outside its innermost braces is hidden from the use check.
        stack=[]
        for pos in range(lo,da):
            if clean[pos]=='{': stack.append(pos)
            elif clean[pos]=='}':
                if not stack: break
                stack.pop()
        if not stack: continue
        depth=1; close=stack[-1]+1
        while close<hi and depth:
            depth+=(clean[close]=='{')-(clean[close]=='}'); close+=1
        if depth or db>=close: continue
        if len(re.findall(r'\b'+re.escape(name)+r'\b',clean[da:db]))!=1: continue
        hide(da,close); shadowed.append(other)
    if re.search(r'\b'+re.escape(name)+r'\b',''.join(remaining)):
        raise ValueError('Identifier has uses outside target not proven to be local shadows')
    newline='\r\n' if '\r\n' in text else '\n'
    return [{'start':a,'end':b,'before':text[a:b],'after':''},
            {'start':start+1,'end':start+1,'before':'','after':newline+'    '+declaration}],shadowed


def plan(source,report,item,ledger):
    old=item['original']; new=item['candidate']; variable=old['name']; function=old['scope'][1] if old['scope'][0]=='FUNCTION_STATIC' else None
    name='scope_'+Path(source).stem+'_'+variable
    card={'schema':1,'task_kind':'STATIC_SCOPE','function':name,'source':source,'sources':[source],
          'target':report['build']['target'],'target_function':function,'object':variable,'original_die':old['die'],
          'original':old,'candidate':new,'difficulty':'SUPERVISOR','priority':-30,'changes':[],
          'state':'STORAGE_SCOPE_REPAIR','status':'SOURCE_SCOPE_DIFFERS','difference_class':'STATIC_DECLARATION_SCOPE',
          'body_edit_allowed':False,'source_identities':{source:identity(ROOT/source)},
          'begin_command':'python tools/interface_task.py begin '+name,'apply_command':'python tools/interface_task.py apply '+name,
          'verification_command':'python tools/interface_task.py check '+name,'promotion_command':'python tools/interface_task.py promote '+name,
          'acceptance':'Exact scope/type/COFF BSS owner; raw machine text, all allocated contributions and previous owners preserved. No expression edits.'}
    try:
        if not function or new['scope']!=['GLOBAL']: raise ValueError('Only file-static to unique function-static scope is mechanical')
        if old['layout']!=new['layout'] or old.get('section')!='.bss' or new.get('section')!='.bss': raise ValueError('Type/section changes require a separate task')
        if len(old['coff'])!=1 or len(new['coff'])!=1 or old['coff'][0]['storage_class']!=3 or new['coff'][0]['storage_class']!=3: raise ValueError('Both sides require unique static COFF BSS owners')
        row=next(r for r in report['functions'] if r['name']==function)
        if row['status']=='FUNCTION_MATCH': raise ValueError('Already proven function body is immutable')
        if not row['workflow']['body_edit_allowed'] and row['status']!='CODEGEN_SIMILAR': raise ValueError('Supervisor context protects this body')
        if not new.get('declaration_file') or (ROOT/new['declaration_file']).resolve()!=(ROOT/source).resolve(): raise ValueError('Declaration source is unknown or different')
        text=(ROOT/source).read_bytes().decode('cp1252')
        changes,shadows=edits(text,function,old,new,report['candidate_debug'])
        targets=affected_targets(ledger,[source])
        if targets!=[report['build']['target']]: raise ValueError('Storage scope affects a broader dependency closure')
        card.update(changes=[{**e,'file':source,'reason':'Restore independently recorded DWARF declaration scope; retain declaration text and all expressions'} for e in changes],
                    affected_targets=targets,shadowed_local_functions=shadows,difficulty='CHEAP',priority=235,
                    reason='One misplaced static BSS declaration; other same-name references are proven local shadows.',
                    edit_scope='Only move the generated declaration. No function expression, initializer, type or object placement edits.')
    except (ValueError,StopIteration) as exc: card['reason']=str(exc) or 'Historical owning function is missing'
    blocks=ROOT/'docs/current/interface-blocks.json'
    if blocks.exists() and name in read_json(blocks): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocks)[name])
    return card


def plans(ledger):
    cards=[]
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report']); items=diagnose(report)['objects']
        for item in items:
            if item['state']=='SOURCE_SCOPE_DIFFERS':
                card=plan(source,report,item,ledger)
                if sum(v['name']==item['name'] for v in items)!=1:
                    card.update(difficulty='SUPERVISOR',reason='Historical name has multiple scopes',changes=[])
                cards.append(card)
    return cards


def verify_scope(before,after,plan):
    a,b=contribution_fingerprint(before),contribution_fingerprint(after)
    if a!=b:
        differences={key:{'before_only':[x for x in a[key] if x not in b[key]][:4],'after_only':[x for x in b[key] if x not in a[key]][:4]} for key in a if a[key]!=b[key]}
        raise ValueError('Static scope repair changed emitted contributions: '+json.dumps(differences,sort_keys=True))
    old_text=next(s['sha256'] for s in before['object_sections'] if s['name']=='.text')
    new_text=next(s['sha256'] for s in after['object_sections'] if s['name']=='.text')
    if old_text!=new_text: raise ValueError('Static scope repair changed raw machine text')
    owners=after.get('object_ownership',{}).get('accepted',[])
    matched=[o for o in owners if o['original_die']==plan['original_die'] and o['name']==plan['object'] and tuple(o['scope'])==('FUNCTION_STATIC',plan['target_function'])]
    if len(matched)!=1: raise ValueError('Static declaration lacks fresh complete DWARF/COFF ownership proof')
    def keys(report): return {(o['original_die'],o['original_va'],o['size']) for o in report.get('object_ownership',{}).get('accepted',[])}
    if keys(before)-keys(after): raise ValueError('Static scope repair regressed an existing owner')


def publish_scopes(ledger,check=False):
    emit=check_json if check else write_json; active=set(); tasks=[]
    for card in plans(ledger):
        path=ROOT/'docs/current/static-scope-tasks'/(card['function']+'.json'); emit(path,card); active.add(path)
        tasks.append({k:card[k] for k in ('task_kind','function','target_function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')}|{'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    for path in (ROOT/'docs/current/static-scope-tasks').glob('*.json'):
        if path not in active: emit(path,{'schema':1,'task_kind':'STATIC_SCOPE','function':path.stem,'state':'NOT_QUEUED','status':'NO_SCOPE_DIFFERENCE','changes':[],'body_edit_allowed':False})
    emit(ROOT/'docs/current/static-scope-tasks.json',{'authority':'DWARF storage scope; unchanged emission and fresh owner proof required','tasks':tasks})
