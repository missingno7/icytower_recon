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
        clean=sanitized(text)
        for left,right in zip(spans,spans[1:]):
            if clean[left['end']:right['start']].strip(): raise ValueError('Interleaved top-level declarations/directives require supervisor review')
        for slot,definition in zip(spans,ordered):
            before=text[slot['start']:slot['end']]; after=text[definition['start']:definition['end']]
            if before!=after: card['changes'].append({'file':source,'start':slot['start'],'end':slot['end'],'before':before,'after':after,
                'reason':'Move the complete unchanged definition to its original DWARF source-order slot'})
        card.update(difficulty='CHEAP',priority=300,reason='Unique original declaration lines; only complete definitions move; every body is preserved byte-for-byte.',
                    edit_scope='Generated complete-definition reorder only. Freshly preserve every exact function and prohibit new implicit declarations. No linker placement or target addresses.')
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def plans(ledger):
    return [plan_order(unit,ledger) for unit in read_json(ROOT/'src/units.json') if unit['classification'] in ('GAME','AMBIGUOUS')]


def publish_orders(ledger,check=False):
    emit=check_json if check else write_json; tasks=[]
    for card in plans(ledger):
        path=ROOT/'docs/current/source-order'/(card['target']+'.json'); emit(path,card)
        if card['state']=='NOT_QUEUED': continue
        tasks.append({k:card[k] for k in ('task_kind','function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')} | {'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    emit(ROOT/'docs/current/source-order-tasks.json',{'authority':'Original DWARF source file and declaration lines; executable addresses never determine source order','tasks':tasks})
    return tasks
