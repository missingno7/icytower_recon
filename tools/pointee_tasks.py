"""Bounded typed pointee migrations through the existing preservation gate."""
from pathlib import Path
from common import ROOT,identity,read_json,write_json,check_json
from pointee_migration import plan as recipe
from interface_type_probe import interface_typedefs
from type_graph import graph
from dwarf_layout import layout
from type_views import shape_key
from source_scope import body_hash
from type_tasks import generated_dependencies
from interface_tasks import text_identity


def plans(ledger,source_texts=None):
    cards=[];g=graph()
    for source,entry in ledger.items():
        if not entry.get('verified_report'):continue
        report=read_json(ROOT/entry['verified_report']);target=report['build']['target']
        text=(source_texts or {}).get(source)
        if text is None:text=(ROOT/source).read_bytes().decode('cp1252')
        for t in interface_typedefs(report):
            parent=t['name']
            if parent not in g.game_types:continue
            for m in t['layout'].get('members',[]):
                if m['layout']['kind']!='pointer_type':continue
                try:changed,details=recipe(report,text,parent,m['name'])
                except (ValueError,KeyError):continue
                # Do not offer token edits inside exact or layout-protected bodies.
                if any(r['workflow']['state'] in ('FUNCTION_MATCH','BODY_MATCH_LAYOUT_BLOCKED') and body_hash(text,r['name'])!=body_hash(changed,r['name']) for r in report['functions']):continue
                canonical=details['changes'][1]['after']
                name='pointee_'+Path(source).stem+'_'+parent+'_'+m['name']
                headers=['include/recovered/'+n+'.h' for n in sorted({canonical,*generated_dependencies(canonical,ROOT)})]
                card={'schema':1,'task_kind':'POINTEE_TYPE','function':name,'source':source,'sources':[source],
                    'parent':parent,'member':m['name'],'canonical':canonical,'recipe':details,
                    'changes':[dict(e,file=source) for e in details['changes']],
                    'source_identities':{source:text_identity(text)},'headers':{p:identity(ROOT/p) for p in headers},
                    'affected_targets':[target],'difficulty':'CHEAP','priority':246,'state':'POINTEE_MIGRATION',
                    'status':'RENAMED_POINTEE','difference_class':'CANONICAL_POINTEE_DECLARATION','body_edit_allowed':False,
                    'reason':'Only generated compiler-typed member token edits and declarations; full canonical layout and contribution preservation required.',
                    'begin_command':'python tools/interface_task.py begin '+name,'apply_command':'python tools/interface_task.py apply '+name,
                    'verification_command':'python tools/interface_task.py check '+name,'promotion_command':'python tools/interface_task.py promote '+name}
                blocks=ROOT/'docs/current/interface-blocks.json'
                if blocks.exists() and name in read_json(blocks):card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocks)[name])
                cards.append(card)
    return cards


def verify(report,card):
    from generate_types import outputs
    generated=outputs();g=graph();types=interface_typedefs(report)
    for path,expected in card['headers'].items():
        header=ROOT/path
        if identity(header)!=expected or report['build']['local_inputs'].get(path)!=expected or header.read_text(encoding='utf-8')!=generated[header]:raise ValueError('Canonical pointee header unverified: '+path)
    for name in (card['parent'],card['canonical']):
        candidates=[t for t in types if t['name']==name]
        expected=[layout(g,d['type_ref']) for d in g.game_types[name]]
        if len(candidates)!=1 or not expected or any(shape_key(candidates[0]['layout'])!=shape_key(e) for e in expected):raise ValueError('Complete compiled pointee/parent layout differs: '+name)


def publish(ledger,check=False):
    emit=check_json if check else write_json;cards=plans(ledger);tasks=[]
    for card in cards:
        path='docs/current/pointee-tasks/'+card['function']+'.json';emit(ROOT/path,card)
        tasks.append({k:card[k] for k in ('task_kind','function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')}|{'size':0,'candidate_card':path})
    active={c['function'] for c in cards}
    for path in (ROOT/'docs/current/pointee-tasks').glob('*.json'):
        if path.stem not in active:emit(path,{'function':path.stem,'state':'NOT_QUEUED','body_edit_allowed':False})
    emit(ROOT/'docs/current/pointee-tasks.json',{'tasks':tasks,'scope':'Generated typed token migration; fresh complete types and all contribution preservation remain mandatory.'})
