"""Restore evidenced source definition order; never place functions at executable addresses."""
import re
from pathlib import Path
from common import ROOT,identity,read_json,write_json,check_json
from type_graph import graph,number
from source_scope import sanitized,function_span


def definition_spans(text):
    clean=sanitized(text)
    clean=re.sub(r'(?m)^[ \t]*#[^\n]*(?:\\\n[^\n]*)*',lambda m:' '*len(m[0]),clean)
    spans=[]
    for name in set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',clean)):
        try: a,b=function_span(text,name)
        except ValueError: continue
        name_pos=clean.rfind(name,0,a)
        start=max(clean.rfind(';',0,name_pos),clean.rfind('}',0,name_pos))+1
        first=re.search(r'\S',clean[start:name_pos])
        if not first: continue
        start+=first.start()
        spans.append({'name':name,'start':start,'end':b,'body_start':a})
    return sorted(spans,key=lambda s:s['start'])


def plan_order(unit,ledger):
    source=unit['source']; text=(ROOT/source).read_bytes().decode('cp1252'); spans=definition_spans(text)
    name='order_'+Path(source).stem.replace('-','_'); target=read_json(ROOT/ledger[source]['verified_report'])['build']['target']
    card={'schema':1,'task_kind':'SOURCE_ORDER','function':name,'source':source,'sources':[source],
          'target':target,'affected_targets':[target],'difficulty':'SUPERVISOR','priority':-30,'changes':[],
          'source_identities':{source:identity(ROOT/source)},'body_edit_allowed':False,'state':'SOURCE_ORDER_REPAIR',
          'status':'DEFINITION_ORDER_DIFFERS','difference_class':'HISTORICAL_DEFINITION_ORDER','definition_order':[],
          'begin_command':'python tools/interface_task.py begin '+name,'apply_command':'python tools/interface_task.py apply '+name,
          'verification_command':'python tools/interface_task.py check '+name,'promotion_command':'python tools/interface_task.py promote '+name}
    try:
        if len(spans)<2: raise ValueError('Fewer than two explicit source definitions')
        g=graph(); lines={}
        for d in g.dies.values():
            if d['tag']!='DW_TAG_subprogram' or d.get('cu')!=unit['cu_die']: continue
            path=(d.get('decl_file_path') or '').replace('\\','/')
            if path.rsplit('/',1)[-1]!=Path(source).name: continue
            line=number(d['resolved'].get('DW_AT_decl_line'))
            if line: lines.setdefault(d.get('name'),set()).add(line)
        for span in spans:
            positions=lines.get(span['name'],set())
            if len(positions)!=1: raise ValueError('Missing/ambiguous historical definition line: '+span['name'])
            span['historical_line']=next(iter(positions))
        ordered=sorted(spans,key=lambda s:s['historical_line'])
        if len({s['historical_line'] for s in ordered})!=len(ordered): raise ValueError('Overlapping historical declaration lines')
        card['definition_order']=[{'function':s['name'],'historical_line':s['historical_line']} for s in ordered]
        card['current_order']=[s['name'] for s in spans]
        if [s['name'] for s in ordered]==card['current_order']:
            card.update(state='NOT_QUEUED',status='DEFINITION_ORDER_AGREES',reason='Explicit function definitions already follow original DWARF lines')
            return card
        # A whole-unit reorder changes the emission order and the peephole scratch cursor of every later
        # function, so it is always a TU_CONTEXT transaction gated by a retained whole-unit probe, never a
        # blind slot-by-slot edit list (docs/tu-context-analysis.md).
        tu_context_order(card,unit,target,source,ordered)
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def tu_context_order(card,unit,target,source,ordered):
    """Whole-unit historical order for a unit whose definitions interleave with declarations: the source-order
    card becomes a TU_CONTEXT transaction (tools/tu_context_task.py) whose islands (definition plus leading
    comment) move while every other top-level text keeps its relative order.  It is queued only when the
    retained isolated probe of the same source and object (docs/attempts/tu-context/<target>/hist-order.json)
    compiled with no exact-function loss and no new implicit declaration; otherwise the probe's losses are the
    recorded reason.  Source order and emission order are different things: the probe reports both."""
    name='order_'+Path(source).stem.replace('-','_')
    card.update(task_kind='TU_CONTEXT',spec={'target':target,'source':source,'order':'historical'},
                begin_command='python tools/tu_context_task.py begin '+name,apply_command='python tools/tu_context_task.py apply '+name,
                verification_command='python tools/tu_context_task.py check '+name,promotion_command='python tools/tu_context_task.py promote '+name,
                plan_command='python tools/tu_context_task.py plan '+name+' docs/current/source-order/'+target+'-spec.json',
                edit_scope='Generated whole-unit definition reorder in historical DWARF line order with derived forward prototypes; every definition island is preserved byte-for-byte; no body, flag or linker edits. Accepted only on the final unit state.')
    evidence=ROOT/'docs/attempts/tu-context'/target/'hist-order.json'
    if not evidence.exists():
        card.update(reason='Interleaved top-level declarations: needs a retained whole-unit probe (python tools/tu_context_probe.py %s %s hist-order --order historical)'%(target,source)); return card
    record=read_json(evidence); card['probe_evidence']=evidence.relative_to(ROOT).as_posix()
    ledger_object=read_json(ROOT/read_json(ROOT/'src/recovery.json')[source]['verified_report'])['build'].get('object')
    if record.get('source_identity')!=identity(ROOT/source) or record.get('object_identity')!=ledger_object:
        card.update(reason='Retained whole-unit probe is stale for the current source/object; rerun tools/tu_context_probe.py'); return card
    if record.get('compile')!='OK':
        card.update(reason='Retained whole-unit probe failed to compile: '+'; '.join(record.get('errors') or [])[:300]); return card
    summary={'matches_before':record['matches_before'],'matches_after':record['matches_after'],'gains':record['gains'],'losses':record['losses'],
             'same_historical_predecessor':record['same_historical_predecessor'],'new_implicit_declarations':record['new_implicit_declarations']}
    card['probe_summary']=summary
    if record['losses'] or record['new_implicit_declarations']:
        card.update(difficulty='SUPERVISOR',priority=-30,status='HISTORICAL_ORDER_LOSES_CONTEXT_ACCIDENTAL_MATCHES',
                    reason='Historical definition order is right but the retained probe loses %s: these functions match today only through the current emission order/register-cursor context; recover their historical emission prefixes (bodies and call structure) and land everything as one TU_CONTEXT transaction.'%', '.join(record['losses']))
        return card
    card.update(difficulty='CHEAP',priority=300,reason='Retained whole-unit probe: historical definition order compiles with no exact-function loss (gains: %s; historical predecessors %s -> %s of %s). Fresh strict final-state acceptance remains mandatory.'%(', '.join(record['gains']) or 'none',summary['same_historical_predecessor']['before'],summary['same_historical_predecessor']['after'],summary['same_historical_predecessor']['total']))
    return card


def plans(ledger):
    from emission_order import move_plans
    units=[u for u in read_json(ROOT/'src/units.json') if u['classification'] in ('GAME','AMBIGUOUS')]
    return [plan_order(unit,ledger) for unit in units]+[card for unit in units for card in move_plans(unit,ledger)]


def publish_orders(ledger,check=False):
    emit=check_json if check else write_json; tasks=[]
    for card in plans(ledger):
        path=ROOT/'docs/current/source-order'/((card['target']+'-'+card['function'] if card.get('moved_function') else card['target'])+'.json'); emit(path,card)
        if card.get('task_kind')=='TU_CONTEXT': emit(ROOT/'docs/current/source-order'/(card['target']+'-spec.json'),card['spec'])
        if card['state']=='NOT_QUEUED': continue
        tasks.append({k:card[k] for k in ('task_kind','function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')} | {'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    emit(ROOT/'docs/current/source-order-tasks.json',{'authority':'Original DWARF source file and declaration lines; executable addresses never determine source order','tasks':tasks})
    return tasks
