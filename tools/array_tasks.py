"""Bounded builtin-array extent repairs from named-object DWARF evidence."""
import re
from common import ROOT,identity,read_json,write_json,check_json
from source_scope import sanitized
from interface_tasks import affected_targets

ARRAY=re.compile(r'^(char \*|const char \*|int |unsigned int |short int |unsigned short int |float |double )\[(\d+)\]$')


def plan_array(source,owner,ledger):
    name=owner['name']; key='array_'+source.rsplit('/',1)[-1].removesuffix('.c')+'_'+name
    card={'schema':1,'task_kind':'ARRAY_EXTENT','function':key,'object':name,'source':source,'sources':[source],
          'difficulty':'SUPERVISOR','priority':-25,'state':'ARRAY_EXTENT_REPAIR','status':'ARRAY_EXTENT_DIFFERS',
          'difference_class':'DWARF_ARRAY_EXTENT','body_edit_allowed':False,'changes':[],
          'historical_owner':owner,'source_identities':{source:identity(ROOT/source)},
          'begin_command':'python tools/interface_task.py begin '+key,'apply_command':'python tools/interface_task.py apply '+key,
          'verification_command':'python tools/interface_task.py check '+key,'promotion_command':'python tools/interface_task.py promote '+key}
    try:
        old=ARRAY.fullmatch(owner.get('dwarf_type','')); new=ARRAY.fullmatch(owner.get('candidate_type',''))
        if not old or not new or old[1]!=new[1] or old[2]==new[2]: raise ValueError('Not a simple builtin array-bound-only difference')
        if owner.get('scope') not in (['GLOBAL'],('GLOBAL',)): raise ValueError('Non-global array identity requires review')
        expected=int(old[2]); current=int(new[2])
        if not 0<expected<current: raise ValueError('Only an evidenced reduction with a complete initializer is mechanical')
        text=(ROOT/source).read_bytes().decode('cp1252'); clean=sanitized(text)
        prefix=r'\s*'.join(re.escape(t) for t in re.findall(r'\w+|\*',new[1]))
        pattern=re.compile(r'(?m)^[ \t]*(?:static\s+)?'+prefix+r'\s+'+re.escape(name)+r'\s*\[\s*(\d+)\s*\]\s*=\s*\{')
        # A pointer star may abut its identifier; accept that spelling too.
        if new[1].rstrip().endswith('*'):
            pattern=re.compile(r'(?m)^[ \t]*(?:static\s+)?'+prefix+r'\s*'+re.escape(name)+r'\s*\[\s*(\d+)\s*\]\s*=\s*\{')
        sites=[m for m in pattern.finditer(clean) if clean[:m.start()].count('{')==clean[:m.start()].count('}')]
        if len(sites)!=1 or int(sites[0][1])!=current: raise ValueError('Unique compiled array declaration not isolated')
        site=sites[0]; end=clean.find('}',site.end())
        if end<0 or '{' in clean[site.end():end]: raise ValueError('Nested initializer requires review')
        initializer=text[site.end():end].strip().rstrip(',')
        # Preserve initializers exactly. Count top-level elements with string-aware
        # tokenization; no macros, designators or compound expressions are guessed.
        elements=re.findall(r'"(?:\\.|[^"\\])*"|[-+]?\d+(?:[uUlL]*)|[,\s]+|.',initializer,re.S)
        values=[]; expect_value=True
        for token in elements:
            if token.isspace(): continue
            if token.strip()==',':
                if expect_value: raise ValueError('Initializer element is missing')
                expect_value=True
            elif re.fullmatch(r'"(?:\\.|[^"\\])*"|[-+]?\d+[uUlL]*',token):
                if not expect_value: raise ValueError('Compound initializer requires review')
                values.append(token); expect_value=False
            else: raise ValueError('Nonliteral initializer requires review')
        if len(values)>expected: raise ValueError('Extent change would discard explicit initializer elements')
        for path in [*sorted((ROOT/'src').glob('*.c')),*sorted((ROOT/'include').glob('*.h'))]:
            if path==ROOT/source: continue
            other=sanitized(path.read_bytes().decode('cp1252'))
            if re.search(r'\b'+re.escape(name)+r'\s*\[[^\]]*\]\s*(?:=|;)',other):
                raise ValueError('Other array declaration needs a shared-interface repair: '+path.relative_to(ROOT).as_posix())
        a,b=site.span(1)
        card.update(changes=[{'file':source,'start':a,'end':b,'before':text[a:b],'after':str(expected),
                             'reason':'Use the unique original DWARF array extent; preserve every initializer and body'}],
                    expected_count=expected,current_count=current,affected_targets=affected_targets(ledger,[source]),
                    difficulty='CHEAP',priority=260,reason='One builtin array extent differs; original DWARF and exact object initializer are acceptance requirements.',
                    edit_scope='Only generated bound digits. Require complete original type/initializer ownership and unchanged emitted contributions.')
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and key in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[key])
    return card


def plans(ledger):
    cards=[]
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report'])
        for owner in report.get('object_ownership',{}).get('rejected',[]):
            old=ARRAY.fullmatch(owner.get('dwarf_type','')); new=ARRAY.fullmatch(owner.get('candidate_type',''))
            if old and new and old[1]==new[1] and old[2]!=new[2]: cards.append(plan_array(source,owner,ledger))
    return cards


def publish_arrays(ledger,check=False):
    emit=check_json if check else write_json; cards=plans(ledger); tasks=[]; active=set()
    for card in cards:
        path=ROOT/'docs/current/arrays'/(card['function']+'.json'); active.add(path); emit(path,card)
        tasks.append({k:card[k] for k in ('task_kind','function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')} | {'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    for path in (ROOT/'docs/current/arrays').glob('*.json'):
        if path not in active:
            emit(path,{'schema':1,'task_kind':'ARRAY_EXTENT','function':path.stem,'state':'NOT_QUEUED','status':'NO_BOUND_ONLY_CONFLICT','body_edit_allowed':False,'changes':[]})
    emit(ROOT/'docs/current/array-tasks.json',{'authority':'Unique named DWARF type plus independently resolved initializer; never inferred from tested code operands','tasks':tasks})
