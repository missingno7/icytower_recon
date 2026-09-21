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


def normalize_alias_pointers(candidate,report):
    """Spell pointer members through proven explicit canonical aliases.

    Only aliases that type_aliases.canonical_aliases proves (compiled generated
    header, identical complete layout) are rewritten. This is declaration spelling
    normalization for layout comparison; it never asserts function or CU equality.
    """
    try:
        from type_aliases import canonical_aliases
        aliases=canonical_aliases(report)
    except (KeyError,TypeError,ValueError): aliases={}
    if not aliases or candidate.get('kind')!='structure_type': return candidate,[]
    node=json.loads(json.dumps(candidate)); normalized=[]
    for m in node.get('members',[]):
        a=m['layout']
        if a.get('kind')!='pointer_type' or a.get('qualifiers'): continue
        target=POINTER.fullmatch(a.get('type',''))
        if target and target[1] in aliases:
            normalized.append({'member':m['name'],'candidate_type':a['type'],'canonical_type':aliases[target[1]]+' *',
                'reason':'Explicit compiled alias with identical complete layout; spelling normalized for comparison only'})
            a['type']=aliases[target[1]]+' *'
    return node,normalized


def historical_cu_defines(source,name,g):
    """True when the historical CU compiled from `source` carries a complete DWARF definition of game type `name`.

    This is declaration evidence for restoring a complete include; it proves nothing about function bytes.
    """
    try:
        units={u['source']:u for u in read_json(ROOT/'src/units.json')}
    except (OSError,ValueError,KeyError): return False
    unit=units.get(source)
    if not unit: return False
    for d in g.game_types.get(name,[]):
        target=g.dies.get(d.get('type_ref'))
        if d.get('cu')==unit['cu_die'] and target and target['tag']=='DW_TAG_structure_type' and g.size(d['type_ref']): return True
    return False


def member_replacement(declaration, repairs, newline, canonical_pointers=()):
    """Retype each void-pointer placeholder member in place; include generated headers for game pointees only."""
    edits=[]
    for repair in repairs:
        pointee=POINTER.fullmatch(repair['historical_type'])
        matches=list(re.finditer(r'\bvoid(?=\s*\*\s*'+re.escape(repair['member'])+r'\s*;)',sanitized(declaration)))
        if not pointee or len(matches)!=1: raise ValueError('Pointer member source spelling is ambiguous')
        edits.append((matches[0].start(),matches[0].end(),pointee[1]))
    if len({e[0] for e in edits})!=len(edits): raise ValueError('Pointer member repairs overlap')
    text=declaration
    for start,end,name in sorted(edits,reverse=True): text=text[:start]+name+text[end:]
    headers=sorted({name for _,_,name in edits if name in canonical_pointers})
    return ''.join('#include "recovered/'+name+'.h"'+newline for name in headers)+text


def library_pointees(source,report,g):
    """Library typedefs whose complete historical layout in the owning CU equals the compiled CU's typedef.

    Evidence for retyping a void-pointer member placeholder to that library pointer. Game types
    with generated headers are handled separately; this never merges layouts by name alone.
    """
    try: units={u['source']:u for u in read_json(ROOT/'src/units.json')}
    except (OSError,ValueError): return set()
    unit=units.get(source)
    if not unit: return set()
    compiled=defaultdict(list)
    for t in interface_typedefs(report): compiled[t['name']].append(t)
    historical=defaultdict(list)
    for d in g.dies.values():
        if d['tag']=='DW_TAG_typedef' and d.get('name') and d.get('cu')==unit['cu_die'] and d['name'] not in g.game_types:
            historical[d['name']].append(d)
    proven=set()
    for name,rows in historical.items():
        if len(rows)!=1 or len(compiled.get(name,[]))!=1: continue
        expected=layout(g,rows[0]['type_ref'])
        if expected['kind']!='structure_type' or not expected.get('size'): continue
        if shape_key(compiled[name][0]['layout'])==shape_key(expected): proven.add(name)
    return proven


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
    for alias, observations in global_evidence(report,unit,g).items():
        found[alias].extend(observations)
    return found


def global_evidence(report,unit,g):
    """Map a uniquely named file-scope object to its historical game type through its compiled layout.

    The candidate global's complete DWARF layout must equal exactly one compiled typedef's layout;
    that typedef is the alias. By-value objects and single pointers are accepted. This proposes a view
    only; members, uses and emission are still checked by the planner and the fresh gate.
    """
    found=defaultdict(list)
    candidates=defaultdict(list)
    for row in report.get('candidate_debug',{}).get('globals',[]) or []: candidates[row.get('name')].append(row)
    historical=defaultdict(list)
    for row in unit.get('globals',[]): historical[row.get('name')].append(row)
    typedefs=[t for t in interface_typedefs(report) if t.get('layout',{}).get('kind')=='structure_type']
    for name,rows in candidates.items():
        if not name or len(rows)!=1 or len(historical.get(name,[]))!=1: continue
        old=historical[name][0]; spelled=g.declaration(old.get('type_ref')) if old.get('type_ref') is not None else ''
        pointer=POINTER.fullmatch(spelled); base=pointer[1] if pointer else spelled
        if base not in g.game_types: continue
        layout_node=rows[0].get('layout') or {}
        if pointer:
            if layout_node.get('kind')!='pointer_type': continue
            key=None
        else:
            if layout_node.get('kind')!='structure_type': continue
            key=json.dumps(shape_key(layout_node),sort_keys=True)
        aliases=[t['name'] for t in typedefs if key is not None and json.dumps(shape_key(t['layout']),sort_keys=True)==key]
        if len(set(aliases))!=1: continue
        found[aliases[0]].append({'variable':name,'scope':'file','historical_type':base,'historical_die':old.get('die'),
                                  'candidate_die':rows[0].get('die'),'evidence_source':'GLOBAL_OBJECT_LAYOUT_AND_HISTORICAL_DWARF'})
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
        candidate,normalized=normalize_alias_pointers(candidate,report)
        complete=shape_key(candidate)==shape_key(expected)
        card.update(view_completeness='COMPLETE_LAYOUT' if complete else 'PARTIAL_LAYOUT',alias_normalized_members=normalized)
        pointer_repairs=[]
        pointees={name for name in g.game_types if (ROOT/'include/recovered'/(name+'.h')).exists()}
        library=library_pointees(source,report,g)
        retained,ignored=compatible_members(candidate,expected,outside,pointees|library,pointer_repairs)
        for repair in pointer_repairs:
            target=POINTER.fullmatch(repair['historical_type'])[1]
            repair['pointee_evidence']='GENERATED_HISTORICAL_HEADER' if target in pointees else 'OWNING_CU_LIBRARY_TYPEDEF_LAYOUT'
        member_only=bool(pointer_repairs) and not ignored and candidate['size']==expected['size'] and len(candidate['members'])==len(expected['members'])
        if not complete and not member_only:
            # Member-only repairs keep the struct's size and members, so by-value uses stay valid too.
            # A partial view removes filler, so by-value, array and sizeof uses could change layout.
            # A complete same-shape view is a pure renaming typedef; every use keeps its type.
            for use in re.finditer(r'\b'+re.escape(alias)+r'\b',outside):
                tail=outside[use.end():]; prefix=outside[max(0,use.start()-40):use.start()]
                if re.match(r'\s*\*',tail): continue
                if re.search(r'\bsizeof\s*\(\s*$',prefix) and re.match(r'\s*\)',tail) and candidate['size']==expected['size']: continue
                raise ValueError('Non-pointer or size-dependent view use requires supervisor review')
        targets=affected_targets(ledger,[source])
        if targets!=[report['build']['target']]: raise ValueError('View requires broader dependency closure')
        # A canonical parent can include child declarations that still exist locally.
        from type_tasks import generated_dependencies
        if pointer_repairs and (ignored or candidate['size']!=expected['size'] or len(candidate['members'])!=len(expected['members'])):
            raise ValueError('Member-only repair requires pointer placeholders in an otherwise complete layout')
        game_pointees=sorted({POINTER.fullmatch(r['historical_type'])[1] for r in pointer_repairs}&pointees)
        required=set().union(*({n}|generated_dependencies(n,ROOT) for n in game_pointees)) if pointer_repairs else generated_dependencies(canonical,ROOT)
        conflicts=[{'type':declaration[3],'source':path,'header':'include/recovered/'+declaration[3]+'.h'}
                   for path in maintained if not path.startswith('include/recovered/')
                   for declaration in STRUCT.finditer(sanitized(texts[path])) if declaration[3] in required]
        card['canonical_dependencies']=conflicts
        # Any other local typedef of a required name (opaque `typedef struct T T;`, `typedef void T;`)
        # also conflicts with the generated complete declaration and has no mechanical child task.
        forward=[{'type':name,'source':path,'declaration':m[0].strip(),'start':m.start(),'end':m.end()}
                 for path in maintained if not path.startswith('include/recovered/')
                 for name in sorted(required)
                 for m in re.finditer(r'\btypedef\b[^;{}]*\b'+re.escape(name)+r'\s*;',STRUCT.sub(lambda x:' '*len(x[0]),sanitized(texts[path])))]
        card['forward_declared_dependencies']=forward
        if conflicts:
            card['state']='WAITING_FOR_CANONICAL_DEPENDENCY'
            raise ValueError('Canonicalize included types first to avoid duplicate typedefs in this CU: '+', '.join(sorted({r['type'] for r in conflicts})))
        # A local opaque typedef of a required type conflicts with the generated complete declaration.
        # It may be replaced by the generated header only when it sits in this source file, is unique,
        # and the historical CU's own DWARF carries that complete layout (declaration evidence only).
        forward_repairs=[]
        for row in forward:
            if row['source']!=source: raise ValueError('Required canonical type is forward-declared in an included maintained file: '+row['type'])
            if sum(r['type']==row['type'] for r in forward)!=1: raise ValueError('Required canonical type is forward-declared more than once: '+row['type'])
            if not historical_cu_defines(source,row['type'],g):
                raise ValueError('Required canonical type is forward-declared locally and the historical CU lacks its complete layout: '+row['type'])
            forward_repairs.append(dict(row,header='include/recovered/'+row['type']+'.h',
                reason='Historical CU DWARF defines this type completely; the generated header restores the complete declaration. Fresh emission preservation remains required.'))
        card['forward_declaration_repairs']=forward_repairs
        newline='\r\n' if '\r\n' in texts[source] else '\n'
        after='#include "recovered/'+canonical+'.h"'
        if alias!=canonical: after+=newline+'typedef '+canonical+' '+alias+';'
        if pointer_repairs and forward_repairs: raise ValueError('Member-only repair cannot be combined with a forward-declaration repair')
        if pointer_repairs:
            original=texts[source][match.start():match.end()]
            after=member_replacement(original,pointer_repairs,newline,pointees)
            name='member_'+Path(source).stem+'_'+alias+'_'+'_'.join(r['member'] for r in pointer_repairs)
            card.update(function=name,repair_mode='POINTER_MEMBER_ONLY',
                compiled_headers=['include/recovered/'+n+'.h' for n in game_pointees],
                begin_command='python tools/interface_task.py begin '+name,
                apply_command='python tools/interface_task.py apply '+name,
                verification_command='python tools/interface_task.py check '+name,
                promotion_command='python tools/interface_task.py promote '+name)
        card.update(canonical=canonical,header=header.relative_to(ROOT).as_posix(),header_identity=identity(header),expected_layout=expected,
                    candidate_size=candidate['size'],historical_size=expected['size'],retained_members=retained,removed_fillers=ignored,pointer_member_repairs=pointer_repairs,
                    affected_targets=targets,difficulty='CHEAP',priority=238,
                    changes=[{'file':source,'start':match.start(),'end':match.end(),'before':texts[source][match.start():match.end()],
                              'after':after,'reason':'Unique historical pointer correspondence, compatible field extents and evidenced member types; use the generated canonical struct'}]
                            +[{'file':source,'start':r['start'],'end':r['end'],'before':texts[source][r['start']:r['end']],
                               'after':'#include "recovered/'+r['type']+'.h"','reason':r['reason']} for r in forward_repairs],
                    compiled_headers=[header.relative_to(ROOT).as_posix()]+[r['header'] for r in forward_repairs] if forward_repairs else card.get('compiled_headers',[header.relative_to(ROOT).as_posix()]),
                    reason='Canonical declaration preserves member extents and restores any evidenced void-pointer placeholders; fresh acceptance must preserve every emitted contribution and body.',
                    edit_scope='Replace only this typedef. Do not edit bodies, member expressions, flags, other declarations or initializers.')
    except ValueError as exc: card['reason']=str(exc)
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def plans(ledger):
    texts={p.relative_to(ROOT).as_posix():p.read_bytes().decode('cp1252') for folder in ('src','include') for p in (ROOT/folder).rglob('*.[ch]')}
    units={u['source']:u for u in read_json(ROOT/'src/units.json')}; cards=[]
    from type_tasks import tokens
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report'])
        if 'typedefs' not in report['candidate_debug']: raise ValueError('Reanalyze candidate DWARF before planning type views')
        observed=evidence(report,units[source]); clean=sanitized(texts[source]); matches=list(STRUCT.finditer(clean))
        # Only identified upstream vendored CUs keep their upstream declaration text; AMBIGUOUS CUs stay game-owned per the brief.
        vendored=str(units[source].get('classification') or units[source].get('ownership') or 'GAME').startswith('VENDORED')
        for match in matches:
            if match[3] not in observed: continue
            if sum(m[3]==match[3] for m in matches)!=1: continue
            if clean[:match.start()].count('{')!=clean[:match.start()].count('}'): continue
            card=plan(source,report,match,observed[match[3]],ledger,texts)
            # Exact member-token duplicates have the narrower CANONICAL_TYPE task; a same-name
            # declaration with different spelling but a complete layout stays a TYPE_VIEW.
            if card.get('canonical')==match[3] and exact_duplicate_tokens(match,card,tokens): continue
            if vendored and card['difficulty']=='CHEAP':
                card.update(difficulty='SUPERVISOR',priority=-25,changes=[],
                    reason='Vendored upstream declarations are not canonicalization targets; keep the upstream source text')
            cards.append(card)
    return cards


def exact_duplicate_tokens(match,card,tokens):
    header=ROOT/card['header'] if card.get('header') else None
    if not header or not header.exists(): return False
    expected=re.search(r'typedef struct\s*\{([^{}]*)\}\s*'+re.escape(card['canonical'])+r'\s*;',header.read_text())
    return bool(expected) and tokens(match[2])==tokens(expected[1])


def verify_member_pointees(report, plan):
    if plan.get('repair_mode')!='POINTER_MEMBER_ONLY': return
    repairs=plan.get('pointer_member_repairs',[])
    if not repairs: raise ValueError('Member repair must identify at least one historical pointee')
    g=graph(); game=[]
    library=library_pointees(plan['source'],report,g)
    for repair in repairs:
        pointer=POINTER.fullmatch(repair.get('historical_type',''))
        if not pointer: raise ValueError('Member repair has an unsupported pointer type')
        name=pointer[1]
        if name in g.game_types:
            expected=[layout(g,d['type_ref']) for d in g.game_types[name]]
            if len({json.dumps(shape_key(node),sort_keys=True) for node in expected})!=1:
                raise ValueError('Historical member pointee layouts conflict')
            candidates=[t for t in interface_typedefs(report) if t['name']==name]
            if len(candidates)!=1 or shape_key(candidates[0]['layout'])!=shape_key(expected[0]):
                raise ValueError('Compiled member pointee lacks the complete historical layout: '+name)
            game.append(name)
        elif name not in library:
            raise ValueError('Compiled library pointee lacks the owning CU historical layout: '+name)
    if plan.get('compiled_headers')!=['include/recovered/'+name+'.h' for name in sorted(set(game))]:
        raise ValueError('Member repair compiled-header scope differs from its historical pointees')


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
