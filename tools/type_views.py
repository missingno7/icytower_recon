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
from interface_type_probe import interface_typedefs

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


def compatible_members(candidate,expected,source,canonical_pointers=(),pointer_repairs=None):
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
            if old['bitfield'] or old['offset']!=offset:
                raise ValueError('Member differs in offset/type/qualifiers: '+m['name'])
            if shape_key(old['layout'])!=shape_key(m['layout']):
                a=m['layout']; b=old['layout']; target=POINTER.fullmatch(b.get('type',''))
                placeholder=(pointer_repairs is not None and a['kind']==b['kind']=='pointer_type'
                    and a.get('size')==b.get('size')==4 and not a.get('qualifiers') and not b.get('qualifiers')
                    and re.fullmatch(r'void\s*\*',a.get('type','')) and target and target[1] in canonical_pointers)
                if not placeholder: raise ValueError('Member differs in offset/type/qualifiers: '+m['name'])
                pointer_repairs.append({'member':m['name'],'offset':offset,'size':4,
                    'candidate_type':a['type'],'historical_type':b['type'],
                    'reason':'DWARF identifies a single canonical pointee; replace void-pointer placeholder without changing field extent. Fresh emission preservation remains required.'})
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


def member_replacement(declaration, repair, newline):
    pointee=POINTER.fullmatch(repair['historical_type'])
    matches=list(re.finditer(r'\bvoid(?=\s*\*\s*'+re.escape(repair['member'])+r'\s*;)',sanitized(declaration)))
    if not pointee or len(matches)!=1: raise ValueError('Pointer member source spelling is ambiguous')
    match=matches[0]
    return '#include "recovered/'+pointee[1]+'.h"'+newline+declaration[:match.start()]+pointee[1]+declaration[match.end():]


def return_evidence(report, units, g):
    """Map explicit compiled pointer returns to uniquely owned historical functions.

    This identifies a proposed view, not a compatible layout or safe migration.
    The planner and fresh gate must still prove members and unchanged emission.
    """
    from interfaces import declarations
    originals=defaultdict(list); found=defaultdict(list)
    for unit in units:
        for function in unit['functions']:
            d=g.dies.get(function.get('die'))
            if d: originals[function['name']].append(d)
    for declaration in declarations(report.get('interfaces_aux','')):
        if not declaration['file'].startswith(('src/','include/')): continue
        if 'I' in declaration['kind']: continue
        old=originals[declaration['name']]
        if len(old)!=1: continue
        a=POINTER.fullmatch(declaration['return_type'])
        b=POINTER.fullmatch(g.declaration(old[0].get('type_ref')))
        if a and b and b[1] in g.game_types:
            found[a[1]].append({'function':declaration['name'],'position':'return',
                'historical_type':b[1],'historical_die':old[0]['offset'],
                'candidate_declaration':declaration,
                'evidence_source':'COMPILED_INTERFACE_AND_HISTORICAL_DWARF'})
    return found


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
    for alias, observations in return_evidence(report,read_json(ROOT/'src/units.json'),g).items():
        found[alias].extend(observations)
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
        expected=original[0]; typedefs=[t for t in interface_typedefs(report) if t['name']==alias]
        if len(typedefs)!=1: raise ValueError('Candidate typedef DWARF is absent or ambiguous')
        candidate=typedefs[0]['layout']
        card.update(canonical=canonical,header=header.relative_to(ROOT).as_posix(),header_identity=identity(header),expected_layout=expected,
                    candidate_size=candidate['size'],historical_size=expected['size'],
                    member_correspondence=[{'candidate_member':m['name'],'candidate_offset':m['offset'],'candidate_type':m['layout'].get('type'),
                                            'historical_field_at_offset':locate(expected,m['offset'],canonical) if m['offset'] is not None else None} for m in candidate.get('members',[])])
        clean=sanitized(texts[source]); outside=clean[:match.start()]+' '*(match.end()-match.start())+clean[match.end():]
        # Identical typedef spelling in an unrelated CU is not shared type identity.
        # Included maintained files can still contain uses outside this edit span.
        dependencies=report['build'].get('local_inputs')
        if dependencies is None or source not in dependencies:
            raise ValueError('Compiled dependency evidence is unavailable')
        maintained=[path for path in dependencies if path.startswith(('src/','include/')) and path.endswith(('.c','.h'))]
        if any(path not in texts for path in maintained):
            raise ValueError('Compiled maintained input is unavailable for scope inspection')
        card['type_scope']={'basis':'GCC_DEPFILE','maintained_input_count':len(maintained),
            'limit':'Typedef spellings in unrelated CUs are not shared identity; included uses and affected compile closure remain checked.'}
        if any(re.search(r'\b'+re.escape(alias)+r'\b',sanitized(texts[path])) for path in maintained if path!=source):
            raise ValueError('View has uses in another compiled input of its owning CU')
        if match[1] and re.search(r'\bstruct\s+'+re.escape(match[1])+r'\b',outside): raise ValueError('Struct tag has separate users')
        if alias!=canonical and re.search(r'\btypedef\b[^;]*\b'+re.escape(canonical)+r'\s*;',outside): raise ValueError('Canonical type is already locally defined')
        for use in re.finditer(r'\b'+re.escape(alias)+r'\b',outside):
            tail=outside[use.end():]; prefix=outside[max(0,use.start()-40):use.start()]
            if re.match(r'\s*\*',tail): continue
            if re.search(r'\bsizeof\s*\(\s*$',prefix) and re.match(r'\s*\)',tail) and candidate['size']==expected['size']: continue
            raise ValueError('Non-pointer or size-dependent view use requires supervisor review')
        pointer_repairs=[]
        pointees={name for name in g.game_types if (ROOT/'include/recovered'/(name+'.h')).exists()}
        retained,ignored=compatible_members(candidate,expected,outside,pointees,pointer_repairs)
        targets=affected_targets(ledger,[source])
        if targets!=[report['build']['target']]: raise ValueError('View requires broader dependency closure')
        # A canonical parent can include child declarations that still exist locally.
        from type_tasks import generated_dependencies
        if pointer_repairs and (len(pointer_repairs)!=1 or ignored or candidate['size']!=expected['size'] or len(candidate['members'])!=len(expected['members'])):
            raise ValueError('Member-only repair requires one pointer placeholder in an otherwise complete layout')
        pointee=POINTER.fullmatch(pointer_repairs[0]['historical_type'])[1] if pointer_repairs else None
        required=({pointee}|generated_dependencies(pointee,ROOT)) if pointee else generated_dependencies(canonical,ROOT)
        conflicts=[{'type':declaration[3],'source':path,'header':'include/recovered/'+declaration[3]+'.h'}
                   for path in maintained if not path.startswith('include/recovered/')
                   for declaration in STRUCT.finditer(sanitized(texts[path])) if declaration[3] in required]
        card['canonical_dependencies']=conflicts
        if conflicts:
            card['state']='WAITING_FOR_CANONICAL_DEPENDENCY'
            raise ValueError('Canonicalize included types first to avoid duplicate typedefs in this CU: '+', '.join(sorted({r['type'] for r in conflicts})))
        newline='\r\n' if '\r\n' in texts[source] else '\n'
        after='#include "recovered/'+canonical+'.h"'
        if alias!=canonical: after+=newline+'typedef '+canonical+' '+alias+';'
        if pointer_repairs:
            repair=pointer_repairs[0]
            original=texts[source][match.start():match.end()]
            after=member_replacement(original,repair,newline)
            name='member_'+Path(source).stem+'_'+alias+'_'+repair['member']
            card.update(function=name,repair_mode='POINTER_MEMBER_ONLY',
                compiled_headers=['include/recovered/'+pointee+'.h'],
                begin_command='python tools/interface_task.py begin '+name,
                apply_command='python tools/interface_task.py apply '+name,
                verification_command='python tools/interface_task.py check '+name,
                promotion_command='python tools/interface_task.py promote '+name)
        card.update(canonical=canonical,header=header.relative_to(ROOT).as_posix(),header_identity=identity(header),expected_layout=expected,
                    candidate_size=candidate['size'],historical_size=expected['size'],retained_members=retained,removed_fillers=ignored,pointer_member_repairs=pointer_repairs,
                    affected_targets=targets,difficulty='CHEAP',priority=238,
                    changes=[{'file':source,'start':match.start(),'end':match.end(),'before':texts[source][match.start():match.end()],
                              'after':after,'reason':'Unique historical pointer correspondence, compatible field extents and evidenced member types; use the generated canonical struct'}],
                    reason='Canonical declaration preserves member extents and restores any evidenced void-pointer placeholders; fresh acceptance must preserve every emitted contribution and body.',
                    edit_scope='Replace only this typedef. Do not edit bodies, member expressions, flags, other declarations or initializers.')
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def plans(ledger):
    texts={p.relative_to(ROOT).as_posix():p.read_bytes().decode('cp1252') for folder in ('src','include') for p in (ROOT/folder).rglob('*.[ch]')}
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
            if card['difficulty']=='CHEAP' and card.get('canonical')==match[3] and card.get('candidate_size')==card.get('historical_size') and not card.get('removed_fillers') and not card.get('pointer_member_repairs'):
                continue
            cards.append(card)
    return cards


def verify_member_pointees(report, plan):
    if plan.get('repair_mode')!='POINTER_MEMBER_ONLY': return
    repairs=plan.get('pointer_member_repairs',[])
    if len(repairs)!=1: raise ValueError('Member repair must identify one historical pointee')
    pointer=POINTER.fullmatch(repairs[0].get('historical_type',''))
    if not pointer: raise ValueError('Member repair has an unsupported pointer type')
    name=pointer[1];g=graph()
    if name not in g.game_types: raise ValueError('Member pointee lacks historical type evidence')
    expected=[layout(g,d['type_ref']) for d in g.game_types[name]]
    if len({json.dumps(shape_key(node),sort_keys=True) for node in expected})!=1:
        raise ValueError('Historical member pointee layouts conflict')
    candidates=[t for t in interface_typedefs(report) if t['name']==name]
    if len(candidates)!=1 or shape_key(candidates[0]['layout'])!=shape_key(expected[0]):
        raise ValueError('Compiled member pointee lacks the complete historical layout: '+name)
    if plan.get('compiled_headers')!=['include/recovered/'+name+'.h']:
        raise ValueError('Member repair compiled-header scope differs from its historical pointee')


def verify_view(report,plan):
    verify_member_pointees(report,plan)
    typedefs=[t for t in interface_typedefs(report) if t['name']==plan['alias']]
    if len(typedefs)!=1 or shape_key(typedefs[0]['layout'])!=shape_key(plan['expected_layout']):
        raise ValueError('Canonical alias lacks the complete expected historical layout')
    from generate_types import outputs
    header=ROOT/plan['header']
    if header.read_text(encoding='utf-8')!=outputs()[header]: raise ValueError('Canonical header differs from DWARF generation')
    for required in plan.get('compiled_headers',[plan['header']]):
        dependency=ROOT/required
        if dependency.read_text(encoding='utf-8')!=outputs()[dependency]: raise ValueError('Compiled type header differs from DWARF generation')
        if required not in report['build']['local_inputs']: raise ValueError('Generated canonical header is not a compiled dependency')


def publish_views(ledger,check=False):
    emit=check_json if check else write_json; cards=plans(ledger); active=set(); tasks=[]
    for card in cards:
        from type_trial_context import summaries
        card['compiler_trials']=summaries(card)
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
