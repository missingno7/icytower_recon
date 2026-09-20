"""DWARF-evidenced canonicalization of partial struct views, with unchanged bodies."""
import json
import re
from collections import defaultdict
from pathlib import Path
from common import ROOT,identity,read_json,write_json,check_json
from type_graph import graph
from dwarf_layout import layout,locate
from source_scope import sanitized
from interface_tasks import affected_targets

STRUCT=re.compile(r'\btypedef\s+struct(?:\s+(\w+))?\s*\{([^{}]*)\}\s*(\w+)\s*;')
POINTER=re.compile(r'^(\w+)\s*\*$')


def shape_key(node):
    """Layout compatibility for this migration; not a type identity or match oracle."""
    kind=node['kind']; key=[kind,node.get('size'),node.get('qualifiers',[])]
    if kind=='structure_type':
        key.append([(m['name'],m['offset'],m['bitfield'],shape_key(m['layout'])) for m in node['members']])
    elif kind=='array_type': key.extend([node['dimensions'],shape_key(node['element'])])
    else: key.extend([node.get('type'),node.get('encoding')])
    return key


def compatible_members(candidate,expected,source):
    if candidate['kind']!='structure_type' or expected['kind']!='structure_type': raise ValueError('Only complete struct layouts are eligible')
    if not candidate.get('size') or not expected.get('size'): raise ValueError('Struct size is unknown')
    if candidate.get('qualifiers') or expected.get('qualifiers'): raise ValueError('Qualified aggregate requires supervisor review')
    old_members={m['name']:m for m in expected['members']}; retained=[]; ignored=[]; occupied=set()
    for m in candidate['members']:
        offset=m['offset']; size=m['layout'].get('size')
        if m['bitfield'] or offset is None or not size: raise ValueError('Unknown member extent or bitfield')
        extent=set(range(offset,offset+size))
        if occupied&extent or offset<0 or offset+size>candidate['size']: raise ValueError('Overlapping or invalid member extent')
        occupied.update(extent)
        old=old_members.get(m['name'])
        if old:
            if old['bitfield'] or old['offset']!=offset or shape_key(old['layout'])!=shape_key(m['layout']):
                raise ValueError('Member differs in offset/type/qualifiers: '+m['name'])
            retained.append({'member':m['name'],'offset':offset,'size':size,'type':m['layout'].get('type')})
        else:
            node=m['layout']; element=node.get('element',{})
            byte_array=node['kind']=='array_type' and element.get('kind')=='base_type' and element.get('size')==1 and element.get('type') in ('char','signed char','unsigned char')
            member_use=re.search(r'(?:->|\.)\s*'+re.escape(m['name'])+r'\b',source)
            expressions=STRUCT.sub(lambda x:' '*len(x[0]),source)
            if not byte_array or member_use or re.search(r'\b'+re.escape(m['name'])+r'\b',expressions):
                raise ValueError('Unmapped or referenced view member: '+str(m['name']))
            ignored.append({'member':m['name'],'offset':offset,'size':size,'reason':'Unreferenced byte-array filler; no canonical field identity assumed'})
    if not retained: raise ValueError('No canonical field correspondence')
    return retained,ignored


def evidence(report,unit):
    g=graph(); found=defaultdict(list)
    for f in unit['functions']:
        debug=report['candidate_debug']['functions'].get(f['name'])
        if not debug or not f.get('die'): continue
        current=defaultdict(list); old=defaultdict(list)
        for v in debug['variables']: current[v.get('name')].append(v)
        for d in g.descendants(f['die']):
            if d['tag'] in ('DW_TAG_variable','DW_TAG_formal_parameter') and d.get('name'):
                old[d['name']].append(d)
        for name,variables in current.items():
            if not name or len(variables)!=1 or len(old[name])!=1: continue
            a=POINTER.fullmatch(variables[0]['type']); b=POINTER.fullmatch(g.declaration(old[name][0].get('type_ref')))
            if a and b and b[1] in g.game_types:
                found[a[1]].append({'function':f['name'],'variable':name,'historical_type':b[1],
                                   'historical_die':old[name][0]['offset'],'candidate_die':variables[0]['die']})
    return found


def plan(source,report,match,observations,ledger,texts):
    g=graph(); alias=match[3]; name='view_'+Path(source).stem+'_'+alias
    card={'schema':1,'task_kind':'TYPE_VIEW','function':name,'source':source,'sources':[source],
          'alias':alias,'observations':observations,'difficulty':'SUPERVISOR','priority':-25,'changes':[],
          'state':'TYPE_VIEW_REPAIR','status':'PARTIAL_STRUCT_VIEW','difference_class':'CANONICAL_TYPE_VIEW',
          'body_edit_allowed':False,'source_identities':{source:identity(ROOT/source)},
          'begin_command':'python tools/interface_task.py begin '+name,'apply_command':'python tools/interface_task.py apply '+name,
          'verification_command':'python tools/interface_task.py check '+name,'promotion_command':'python tools/interface_task.py promote '+name}
    try:
        roots={o['historical_type'] for o in observations}
        if len(roots)!=1: raise ValueError('Same candidate view corresponds to conflicting historical types')
        canonical=next(iter(roots)); header=ROOT/'include/recovered'/(canonical+'.h')
        if not header.exists(): raise ValueError('Canonical historical header is not generated')
        original=[layout(g,d['type_ref']) for d in g.game_types[canonical]]
        if len({json.dumps(shape_key(s),sort_keys=True) for s in original})!=1: raise ValueError('Historical type layouts conflict')
        expected=original[0]; typedefs=[t for t in report['candidate_debug']['typedefs'] if t['name']==alias]
        if len(typedefs)!=1: raise ValueError('Candidate typedef DWARF is absent or ambiguous')
        candidate=typedefs[0]['layout']
        card.update(canonical=canonical,header=header.relative_to(ROOT).as_posix(),header_identity=identity(header),expected_layout=expected,
                    candidate_size=candidate['size'],historical_size=expected['size'],
                    member_correspondence=[{'candidate_member':m['name'],'candidate_offset':m['offset'],'candidate_type':m['layout'].get('type'),
                                            'historical_field_at_offset':locate(expected,m['offset'],canonical) if m['offset'] is not None else None} for m in candidate.get('members',[])])
        clean=sanitized(texts[source]); outside=clean[:match.start()]+' '*(match.end()-match.start())+clean[match.end():]
        # Do not replace a view with external or shadowed uses that the owning CU cannot check.
        if any(re.search(r'\b'+re.escape(alias)+r'\b',sanitized(text)) for path,text in texts.items() if path!=source):
            raise ValueError('View has uses outside its owning source')
        if match[1] and re.search(r'\bstruct\s+'+re.escape(match[1])+r'\b',outside): raise ValueError('Struct tag has separate users')
        if alias!=canonical and re.search(r'\btypedef\b[^;]*\b'+re.escape(canonical)+r'\s*;',outside): raise ValueError('Canonical type is already locally defined')
        for use in re.finditer(r'\b'+re.escape(alias)+r'\b',outside):
            tail=outside[use.end():]; prefix=outside[max(0,use.start()-40):use.start()]
            if re.match(r'\s*\*',tail): continue
            if re.search(r'\bsizeof\s*\(\s*$',prefix) and re.match(r'\s*\)',tail) and candidate['size']==expected['size']: continue
            raise ValueError('Non-pointer or size-dependent view use requires supervisor review')
        retained,ignored=compatible_members(candidate,expected,outside)
        targets=affected_targets(ledger,[source])
        if targets!=[report['build']['target']]: raise ValueError('View requires broader dependency closure')
        newline='\r\n' if '\r\n' in texts[source] else '\n'
        after='#include "recovered/'+canonical+'.h"'
        if alias!=canonical: after+=newline+'typedef '+canonical+' '+alias+';'
        card.update(canonical=canonical,header=header.relative_to(ROOT).as_posix(),header_identity=identity(header),expected_layout=expected,
                    candidate_size=candidate['size'],historical_size=expected['size'],retained_members=retained,removed_fillers=ignored,
                    affected_targets=targets,difficulty='CHEAP',priority=238,
                    changes=[{'file':source,'start':match.start(),'end':match.end(),'before':texts[source][match.start():match.end()],
                              'after':after,'reason':'Unique original pointer-variable correspondence and compatible member layouts; use the generated struct via a source alias'}],
                    reason='Canonical alias preserves named member offsets/types; fresh acceptance must preserve every emitted contribution and body.',
                    edit_scope='Replace only this typedef. Do not edit bodies, member expressions, flags, other declarations or initializers.')
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def plans(ledger):
    texts={p.relative_to(ROOT).as_posix():p.read_bytes().decode('cp1252') for folder in ('src','include') for p in (ROOT/folder).glob('*.[ch]')}
    units={u['source']:u for u in read_json(ROOT/'src/units.json')}; cards=[]
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report'])
        if 'typedefs' not in report['candidate_debug']: raise ValueError('Reanalyze candidate DWARF before planning type views')
        observed=evidence(report,units[source]); clean=sanitized(texts[source]); matches=list(STRUCT.finditer(clean))
        for match in matches:
            if match[3] not in observed: continue
            if sum(m[3]==match[3] for m in matches)!=1: continue
            if clean[:match.start()].count('{')!=clean[:match.start()].count('}'): continue
            card=plan(source,report,match,observed[match[3]],ledger,texts)
            # Exact duplicates have a narrower existing CANONICAL_TYPE task.
            if card['difficulty']=='CHEAP' and card.get('canonical')==match[3] and card.get('candidate_size')==card.get('historical_size') and not card.get('removed_fillers'):
                continue
            cards.append(card)
    return cards


def verify_view(report,plan):
    typedefs=[t for t in report['candidate_debug']['typedefs'] if t['name']==plan['alias']]
    if len(typedefs)!=1 or shape_key(typedefs[0]['layout'])!=shape_key(plan['expected_layout']):
        raise ValueError('Canonical alias lacks the complete expected historical layout')
    from generate_types import outputs
    header=ROOT/plan['header']
    if header.read_text(encoding='utf-8')!=outputs()[header]: raise ValueError('Canonical header differs from DWARF generation')
    if plan['header'] not in report['build']['local_inputs']: raise ValueError('Generated canonical header is not a compiled dependency')


def publish_views(ledger,check=False):
    emit=check_json if check else write_json; cards=plans(ledger); active=set(); tasks=[]
    for card in cards:
        path=ROOT/'docs/current/type-views'/(card['function']+'.json'); active.add(path)
        detail=ROOT/'docs/current/type-view-evidence'/path.name; emit(detail,card)
        compact={k:v for k,v in card.items() if k!='expected_layout'}
        compact['detailed_evidence']=detail.relative_to(ROOT).as_posix()
        compact['observation_count']=len(card['observations']); compact['observations']=card['observations'][:4]
        compact['member_correspondence']=[{**m,'historical_field_at_offset':({k:m['historical_field_at_offset'][k] for k in ('expression','offset','size','type')} if m['historical_field_at_offset'] else None)} for m in card.get('member_correspondence',[])]
        emit(path,compact)
        tasks.append({k:card.get(k) for k in ('task_kind','function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')} | {'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    for path in (ROOT/'docs/current/type-views').glob('*.json'):
        if path not in active:
            closed={'schema':1,'task_kind':'TYPE_VIEW','function':path.stem,'state':'NOT_QUEUED','status':'NO_PARTIAL_VIEW_TASK','body_edit_allowed':False,'changes':[]}
            emit(path,closed); emit(ROOT/'docs/current/type-view-evidence'/path.name,closed)
    emit(ROOT/'docs/current/type-view-tasks.json',{'authority':'Original/candidate DWARF member evidence; complete fresh canonical layout plus unchanged contributions required for acceptance','tasks':tasks})
