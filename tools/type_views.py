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

HTTPRESPONSE_HISTORICAL_SIGNATURE=(20,(
    ('iStatusCode',0,False,'base_type',4,'int','5\t(signed)',()),
    ('iNumHeaders',4,False,'base_type',4,'unsigned int','7\t(unsigned)',()),
    ('pHeaders',8,False,'pointer_type',4,'HTTPHeader *',None,()),
    ('pPayload',12,False,'pointer_type',4,'unsigned char *',None,()),
    ('iPayloadSize',16,False,'base_type',4,'unsigned int','7\t(unsigned)',()),
))
HTTPRESPONSE_FLD_ADSPOT_CANDIDATE_SIGNATURE=(20,(
    ('iStatusCode',0,False,'base_type',4,'int','5\t(signed)',()),
    ('iNumHeaders',4,False,'base_type',4,'int','5\t(signed)',()),
    ('pHeaders',8,False,'pointer_type',4,'void *',None,()),
    ('pPayload',12,False,'pointer_type',4,'unsigned char *',None,()),
    ('iPayloadSize',16,False,'base_type',4,'int','5\t(signed)',()),
))

FLDADSPOT_CONST_MEMBER_TYPES={
    'pRemoteImageURL':'const char *',
    'pLocalImagePath':'const char *',
    'pVisitURL':'const char *',
}
FLDADSPOT_HISTORICAL_MEMBER_TYPES={name:'char *' for name in FLDADSPOT_CONST_MEMBER_TYPES}


def fldadspot_const_member_replacement(source,alias,match,candidate,expected,text,canonical,g):
    """One complete, DWARF-proven FLDAdSpot declaration with three const pointees.

    This is deliberately narrower than general member type repair: the historical CU must
    define the complete aggregate, both historical DIEs must agree, all four members and
    offsets must match the generated header, and only these three exact pointer spellings
    may differ. The ordinary TYPE_VIEW gate still requires unchanged emitted contributions.
    """
    if (source!='src/main.c' or alias!='FLDAdSpot' or canonical!='FLDAdSpot'
            or match[1]!='FLDAdSpot' or not historical_cu_defines(source,canonical,g)):
        return None
    if not exact_fldadspot_layout(expected,FLDADSPOT_HISTORICAL_MEMBER_TYPES): return None
    candidate_expected=json.loads(json.dumps(expected))
    members={m['name']:m for m in candidate_expected['members']}
    for member,spelling in FLDADSPOT_CONST_MEMBER_TYPES.items():
        members[member]['layout']['type']=spelling
    if shape_key(candidate)!=shape_key(candidate_expected): return None
    declaration=text[match.start():match.end()]
    from type_tasks import tokens
    if tokens(sanitized(declaration))!=tokens(
            'typedef struct FLDAdSpot { '
            'const char * pRemoteImageURL ; const char * pLocalImagePath ; '
            'const char * pVisitURL ; float fFrequency ; } FLDAdSpot ;'):
        return None
    corrected=declaration
    for member in FLDADSPOT_CONST_MEMBER_TYPES:
        before='const char *'+member
        after='char *'+member
        if corrected.count(before)!=1: return None
        corrected=corrected.replace(before,after,1)
    repairs=[{'member':member,'offset':members[member]['offset'],'size':4,
              'candidate_type':FLDADSPOT_CONST_MEMBER_TYPES[member],
              'historical_type':FLDADSPOT_HISTORICAL_MEMBER_TYPES[member]}
             for member in FLDADSPOT_CONST_MEMBER_TYPES]
    return {'after':corrected,
            'member_type_repairs':repairs,
            'candidate_layout':candidate,
            'compiled_headers':[],
            'reason':'Restore the three FLDAdSpot member pointee types in place from the complete owning-CU DWARF layout; preserve declaration placement and every emitted contribution.'}


def exact_fldadspot_layout(node,member_types):
    expected=[('pRemoteImageURL',0,'pointer_type',4,member_types['pRemoteImageURL'],None),
              ('pLocalImagePath',4,'pointer_type',4,member_types['pLocalImagePath'],None),
              ('pVisitURL',8,'pointer_type',4,member_types['pVisitURL'],None),
              ('fFrequency',12,'base_type',4,'float','4\t(float)')]
    if node.get('kind')!='structure_type' or node.get('size')!=16 or node.get('qualifiers'): return False
    members=node.get('members',[])
    if len(members)!=len(expected): return False
    for actual,want in zip(members,expected):
        name,offset,kind,size,spelling,encoding=want; layout_node=actual.get('layout',{})
        if (actual.get('name')!=name or actual.get('offset')!=offset or actual.get('bitfield')
                or layout_node.get('kind')!=kind or layout_node.get('size')!=size
                or layout_node.get('type')!=spelling or layout_node.get('qualifiers')
                or layout_node.get('encoding')!=encoding): return False
    return True


def validate_fldadspot_member_plan(plan):
    """Recheck the exact source recipe and DWARF signature before accepting a task."""
    if (plan.get('source')!='src/main.c' or plan.get('alias')!='FLDAdSpot'
            or plan.get('canonical')!='FLDAdSpot' or plan.get('header')!='include/recovered/FLDAdSpot.h'
            or plan.get('repair_mode')!='HISTORICAL_MEMBER_QUALIFIERS'):
        raise ValueError('FLDAdSpot qualifier repair is outside its exact source/type scope')
    g=graph(); historical=[layout(g,d['type_ref']) for d in g.game_types.get('FLDAdSpot',[])]
    if (not historical or not historical_cu_defines('src/main.c','FLDAdSpot',g)
            or any(not exact_fldadspot_layout(node,FLDADSPOT_HISTORICAL_MEMBER_TYPES) for node in historical)
            or shape_key(plan.get('expected_layout',{}))!=shape_key(historical[0])):
        raise ValueError('FLDAdSpot historical member layout is absent, conflicting, or changed')
    candidate=plan.get('candidate_layout',{})
    if not exact_fldadspot_layout(candidate,FLDADSPOT_CONST_MEMBER_TYPES):
        raise ValueError('FLDAdSpot candidate does not have the exact three const-char pointer differences')
    expected_repairs=[{'member':member,'offset':offset,'size':4,
                       'candidate_type':FLDADSPOT_CONST_MEMBER_TYPES[member],
                       'historical_type':'char *'}
                      for member,offset in (('pRemoteImageURL',0),('pLocalImagePath',4),('pVisitURL',8))]
    if plan.get('member_type_repairs')!=expected_repairs:
        raise ValueError('FLDAdSpot member repair set differs from the three evidenced fields')
    if plan.get('compiled_headers')!=[]:
        raise ValueError('Inline FLDAdSpot repair must not add generated headers')
    changes=plan.get('changes',[])
    if (len(changes)!=1 or changes[0].get('file')!='src/main.c'
            or not changes[0].get('after')):
        raise ValueError('FLDAdSpot repair must edit only its local typedef')
    from type_tasks import tokens
    expected_before=('typedef struct FLDAdSpot { const char * pRemoteImageURL ; '
                     'const char * pLocalImagePath ; const char * pVisitURL ; '
                     'float fFrequency ; } FLDAdSpot ;')
    if tokens(sanitized(changes[0].get('before','')))!=tokens(expected_before):
        raise ValueError('FLDAdSpot repair source span differs from the exact local declaration')
    expected_after=expected_before.replace('const char *','char *')
    if tokens(sanitized(changes[0]['after']))!=tokens(expected_after):
        raise ValueError('FLDAdSpot repair must change only the three evidenced pointee qualifiers')


def verify_fldadspot_original_candidate(report,plan):
    validate_fldadspot_member_plan(plan)
    candidates=[t for t in interface_typedefs(report) if t.get('name')=='FLDAdSpot']
    if len(candidates)!=1 or shape_key(candidates[0]['layout'])!=shape_key(plan['candidate_layout']):
        raise ValueError('Baseline candidate DWARF does not prove the planned FLDAdSpot qualifier mismatch')


def shape_key(node):
    """Layout compatibility for this migration; not a type identity or match oracle."""
    kind=node['kind']; key=[kind,node.get('size'),node.get('qualifiers',[])]
    if kind=='structure_type':
        key.append([(m['name'],m['offset'],m['bitfield'],shape_key(m['layout'])) for m in node['members']])
    elif kind=='array_type': key.extend([node['dimensions'],shape_key(node['element'])])
    else: key.extend([node.get('type'),node.get('encoding')])
    return key


BYTE_TYPES=('char','signed char','unsigned char')


def unreferenced_byte_array_signedness(candidate_member,expected_member,source):
    """A byte-array member spelled with a different char signedness and never referenced in the CU.

    The canonical declaration restores the historical spelling; because no expression uses
    the member, only DWARF can change. Fresh emission preservation is still required.
    """
    a=candidate_member['layout']; b=expected_member['layout']
    if a.get('kind')!='array_type' or b.get('kind')!='array_type' or a.get('dimensions')!=b.get('dimensions'): return False
    ea=a.get('element',{}); eb=b.get('element',{})
    if ea.get('kind')!='base_type' or eb.get('kind')!='base_type' or ea.get('size')!=1 or eb.get('size')!=1: return False
    if ea.get('type') not in BYTE_TYPES or eb.get('type') not in BYTE_TYPES or a.get('qualifiers') or b.get('qualifiers'): return False
    name=candidate_member['name']
    if re.search(r'(?:->|\.)\s*'+re.escape(name)+r'\b',source): return False
    expressions=STRUCT.sub(lambda x:' '*len(x[0]),source)
    return not re.search(r'\b'+re.escape(name)+r'\b',expressions)


def compatible_members(candidate,expected,source,canonical_pointers=(),pointer_repairs=None,signedness_repairs=None):
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
                if not placeholder and signedness_repairs is not None and unreferenced_byte_array_signedness(m,old,source):
                    signedness_repairs.append({'member':m['name'],'offset':offset,'size':size,'candidate_type':a.get('type'),'historical_type':b.get('type'),
                        'reason':'Unreferenced byte array spelled with a different char signedness; the canonical declaration restores the historical spelling. Fresh emission preservation remains required.'})
                    retained.append({'member':m['name'],'offset':offset,'size':size,'type':b.get('type')}); continue
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


def layout_signature(node):
    return (node.get('size'),tuple((m.get('name'),m.get('offset'),m.get('bitfield'),
        m.get('layout',{}).get('kind'),m.get('layout',{}).get('size'),
        m.get('layout',{}).get('type'),m.get('layout',{}).get('encoding'),
        tuple(m.get('layout',{}).get('qualifiers',[]))) for m in node.get('members',[])))


def exact_httpresponse_layout(node,signature):
    return (node.get('kind')=='structure_type' and not node.get('qualifiers')
            and layout_signature(node)==signature)


def httpresponse_inline_replacement(source,alias,match,candidate,expected,text,newline):
    """The single source-proven HTTPResponse repair that preserves fld_adspot emission.

    Keep the aggregate at its original declaration site: including HTTPResponse.h
    changes an exact peer's instruction order in this TU. The evidence permits
    this narrowly-scoped edit only for the known fld_adspot declaration and exact
    current/historical member graphs; the normal strict interface transaction
    still proves unchanged emission before promotion.
    """
    if source!='src/fld_adspot.c' or alias!='HTTPResponse' or match[1]!='HTTPResponse': return None
    if not exact_httpresponse_layout(expected,HTTPRESPONSE_HISTORICAL_SIGNATURE): return None
    if not exact_httpresponse_layout(candidate,HTTPRESPONSE_FLD_ADSPOT_CANDIDATE_SIGNATURE): return None
    declaration=text[match.start():match.end()]
    normalized=sanitized(declaration)
    if declaration!=normalized: return None
    expected_source=re.compile(
        r'typedef\s+struct\s+HTTPResponse\s*\{\s*'
        r'int\s+iStatusCode\s*;\s*int\s+iNumHeaders\s*;\s*void\s*\*\s*pHeaders\s*;\s*'
        r'unsigned\s+char\s*\*\s*pPayload\s*;\s*int\s+iPayloadSize\s*;\s*'
        r'\}\s*HTTPResponse\s*;')
    if not expected_source.fullmatch(normalized): return None
    if re.search(r'^\s*#\s*include\s*[<"](?:recovered/)?HTTPHeader\.h[>"]',text[:match.start()],re.M): return None
    replacements=(('int iNumHeaders;','unsigned int iNumHeaders;'),
                  ('void *pHeaders;','HTTPHeader *pHeaders;'),
                  ('int iPayloadSize;','unsigned int iPayloadSize;'))
    fixed=declaration
    for before,after in replacements:
        if fixed.count(before)!=1: return None
        fixed=fixed.replace(before,after,1)
    return {'after':'#include "recovered/HTTPHeader.h"'+newline+fixed,
        'pointer_member_repairs':[{'member':'pHeaders','offset':8,'size':4,
                                   'candidate_type':'void *','historical_type':'HTTPHeader *'}],
        'member_type_repairs':[{'member':'iNumHeaders','offset':4,'size':4,
                                'candidate_type':'int','historical_type':'unsigned int'},
                               {'member':'pHeaders','offset':8,'size':4,
                                'candidate_type':'void *','historical_type':'HTTPHeader *'},
                               {'member':'iPayloadSize','offset':16,'size':4,
                                'candidate_type':'int','historical_type':'unsigned int'}],
        'compiled_headers':['include/recovered/HTTPHeader.h'],
        'reason':'Restore the exact historical HTTPResponse member types in place; preserve the source-local declaration order and prove full-CU emission preservation.'}


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
    if source=='src/main.c' and alias=='FLDAdSpot' and match[1]=='FLDAdSpot':
        # The local same-name declaration is itself anchored by the complete FLDAdSpot
        # definition in this CU's historical DWARF; unrelated equal-shaped view uses
        # cannot redirect this narrowly-scoped declaration repair to another type.
        units={u['source']:u for u in read_json(ROOT/'src/units.json')}
        owning=units.get(source,{}).get('cu_die')
        historical=[d for d in g.game_types.get(alias,[]) if d.get('cu')==owning]
        candidates=[t for t in interface_typedefs(report) if t.get('name')==alias]
        if owning is not None and len(historical)==1 and len(candidates)==1:
            observations=[{'historical_type':alias,'historical_die':historical[0]['offset'],
                           'candidate_die':candidates[0]['die'],
                           'evidence_source':'SAME_NAME_COMPLETE_OWNING_CU_DWARF'}]
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
        newline='\r\n' if '\r\n' in texts[source] else '\n'
        member_qualifier_repair=fldadspot_const_member_replacement(
            source,alias,match,candidate,expected,texts[source],canonical,g)
        inline_repair=httpresponse_inline_replacement(source,alias,match,candidate,expected,texts[source],newline)
        pointer_repairs=[]; signedness_repairs=[]
        pointees={name for name in g.game_types if (ROOT/'include/recovered'/(name+'.h')).exists()}
        library=library_pointees(source,report,g)
        if member_qualifier_repair:
            retained=[{'member':m['name'],'offset':m['offset'],'size':m['layout']['size'],'type':m['layout'].get('type')}
                      for m in expected['members']]
            ignored=[]
        elif inline_repair:
            pointer_repairs=inline_repair['pointer_member_repairs']
            retained=[{'member':m['name'],'offset':m['offset'],'size':m['layout']['size'],'type':m['layout'].get('type')}
                      for m in expected['members']]
            ignored=[]
        else:
            retained,ignored=compatible_members(candidate,expected,outside,pointees|library,pointer_repairs,signedness_repairs)
        card['signedness_repairs']=signedness_repairs
        if signedness_repairs and pointer_repairs: raise ValueError('Signedness spelling repairs require the whole canonical declaration, not a member-only repair')
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
                   for declaration in STRUCT.finditer(sanitized(texts[path]))
                   if declaration[3] in required
                   and not (member_qualifier_repair and path==source and declaration.start()==match.start())]
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
        after='#include "recovered/'+canonical+'.h"'
        if alias!=canonical: after+=newline+'typedef '+canonical+' '+alias+';'
        if pointer_repairs and forward_repairs: raise ValueError('Member-only repair cannot be combined with a forward-declaration repair')
        if member_qualifier_repair:
            after=member_qualifier_repair['after']
            card.update(function='view_fld_adspot_FLDAdSpot',repair_mode='HISTORICAL_MEMBER_QUALIFIERS',
                begin_command='python tools/interface_task.py begin view_fld_adspot_FLDAdSpot',
                apply_command='python tools/interface_task.py apply view_fld_adspot_FLDAdSpot',
                verification_command='python tools/interface_task.py check view_fld_adspot_FLDAdSpot',
                promotion_command='python tools/interface_task.py promote view_fld_adspot_FLDAdSpot',
                candidate_layout=member_qualifier_repair['candidate_layout'],
                member_type_repairs=member_qualifier_repair['member_type_repairs'],
                compiled_headers=member_qualifier_repair['compiled_headers'],
                reason=member_qualifier_repair['reason'])
            validate_fldadspot_member_plan(card | {'changes':[{'file':source,'start':match.start(),'end':match.end(),
                'before':texts[source][match.start():match.end()],'after':after}]})
        elif inline_repair:
            after=inline_repair['after']
            card.update(repair_mode='INLINE_MEMBER_TYPES',member_type_repairs=inline_repair['member_type_repairs'],
                compiled_headers=inline_repair['compiled_headers'])
        elif pointer_repairs:
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
                              'after':after,'reason':(member_qualifier_repair['reason'] if member_qualifier_repair else inline_repair['reason'] if inline_repair else 'Unique historical pointer correspondence, compatible field extents and evidenced member types; use the generated canonical struct')}]
                            +[{'file':source,'start':r['start'],'end':r['end'],'before':texts[source][r['start']:r['end']],
                               'after':'#include "recovered/'+r['type']+'.h"','reason':r['reason']} for r in forward_repairs],
                    compiled_headers=[header.relative_to(ROOT).as_posix()]+[r['header'] for r in forward_repairs] if forward_repairs else card.get('compiled_headers',[header.relative_to(ROOT).as_posix()]),
                    reason=(member_qualifier_repair['reason'] if member_qualifier_repair else inline_repair['reason'] if inline_repair else 'Canonical declaration preserves member extents and restores any evidenced void-pointer placeholders; fresh acceptance must preserve every emitted contribution and body.'),
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
            if match[3] not in observed and not (source=='src/main.c' and match[1]=='FLDAdSpot' and match[3]=='FLDAdSpot'): continue
            if sum(m[3]==match[3] for m in matches)!=1: continue
            if clean[:match.start()].count('{')!=clean[:match.start()].count('}'): continue
            card=plan(source,report,match,observed.get(match[3],[]),ledger,texts)
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
    if plan.get('repair_mode') not in ('POINTER_MEMBER_ONLY','INLINE_MEMBER_TYPES'): return
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
    if plan.get('repair_mode')=='INLINE_MEMBER_TYPES':
        verify_httpresponse_inline_plan(plan)
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


def verify_httpresponse_inline_plan(plan):
    """Keep the special inline correction bound to its complete historical evidence."""
    if plan.get('source')!='src/fld_adspot.c' or plan.get('alias')!='HTTPResponse':
        raise ValueError('Inline member correction is restricted to fld_adspot HTTPResponse')
    if not exact_httpresponse_layout(plan.get('expected_layout',{}),HTTPRESPONSE_HISTORICAL_SIGNATURE):
        raise ValueError('Inline HTTPResponse plan differs from its historical member graph')
    expected=[{'member':'iNumHeaders','offset':4,'size':4,'candidate_type':'int','historical_type':'unsigned int'},
              {'member':'pHeaders','offset':8,'size':4,'candidate_type':'void *','historical_type':'HTTPHeader *'},
              {'member':'iPayloadSize','offset':16,'size':4,'candidate_type':'int','historical_type':'unsigned int'}]
    if plan.get('member_type_repairs')!=expected:
        raise ValueError('Inline HTTPResponse member repair set is incomplete or ambiguous')
    pointer={**expected[1],'pointee_evidence':'GENERATED_HISTORICAL_HEADER'}
    if plan.get('pointer_member_repairs')!=[pointer]:
        raise ValueError('Inline HTTPResponse pointer repair differs from its historical pointee')
    if plan.get('compiled_headers')!=['include/recovered/HTTPHeader.h']:
        raise ValueError('Inline HTTPResponse repair has an unexpected header scope')


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
