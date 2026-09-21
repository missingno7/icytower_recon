"""Supplement missing interface layouts with a separate emission-preserving debug build.

Never use the probe's function bytes, locations or globals in reconstruction proof.
"""
import json
import re
from common import ROOT, identity
from binary import Binary
from build import compile_target
from dwarf_locations import candidate_debug

FLAG = '-fno-eliminate-unused-debug-types'


def fingerprint(sections, symbols, relocations):
    names = {s['index']:s['name'] for s in sections}
    allocated = {i for i,name in names.items() if not name.startswith('.debug')}
    def symbol(s):
        return (s['name'], names.get(s['section'],s['section']), s['value'], s['type'], s['storage_class'])
    by_index = {s['index']:s for s in symbols}
    return json.loads(json.dumps({
        'sections': sorted((s['name'],s['virtual_size'],s['raw_size'],s['characteristics'],s['sha256']) for s in sections if s['index'] in allocated),
        'symbols': sorted((symbol(s) for s in symbols if s['storage_class'] != 103 and (s['section'] in allocated or s['section'] in (0,-1))),key=str),
        'relocations': sorted(((names[r['section']],r['offset'],r['type'],symbol(by_index[r['symbol_index']])) for r in relocations if r['section'] in allocated),key=str)}))


def report_fingerprint(report):
    return fingerprint(report['object_sections'],report['object_symbols'],report['object_relocations'])


def validate(report):
    probe=report.get('interface_type_probe')
    if not probe: return
    a,b=report['build'],probe['build']
    for key in ('target','compiler','config','local_inputs','toolchain_lock','candidate_toolchain_lock'):
        if a.get(key)!=b.get(key): raise ValueError('Interface type probe input differs: '+key)
    if not b.get('inputs_verified_around_compile'): raise ValueError('Interface type probe lacks dependency race checks')
    extra=a['config'].get('flags',[])
    flags=a['flags'][:-len(extra)] if extra else a['flags']
    if b['flags']!=[*flags,FLAG,*extra]: raise ValueError('Unexpected interface type probe flags')
    if probe['fingerprint']!=report_fingerprint(report): raise ValueError('Interface type probe changed emitted contributions')
    if probe['object']!=b['object']: raise ValueError('Interface type probe object identity differs')


def requested_types(report, source_names, historical_names):
    """Request typedef evidence for historical names and compiled interface spellings.

    Spelling only selects probe output; it never establishes type correspondence.
    Missing or ambiguous typedefs remain missing or ambiguous after compilation.
    """
    from interfaces import declarations
    names=set(source_names) & set(historical_names)
    keywords=set('void char short int long float double signed unsigned const volatile restrict struct union enum extern static inline __attribute__'.split())
    for declaration in declarations(report.get('interfaces_aux','')):
        if not declaration['file'].startswith(('src/','include/')): continue
        for spelling in [declaration['return_type'],*declaration['parameter_types']]:
            names.update(set(re.findall(r'\b[A-Za-z_]\w*\b',spelling))-keywords)
    present={t['name'] for t in report['candidate_debug']['typedefs']}
    return names-present


def member_pointee_names(g, type_names):
    """Typedef names of pointer members inside the named historical game aggregates.

    A source that spells a historical aggregate with void-pointer member placeholders
    does not use the pointee type, so optimized DWARF omits it. Requesting the name only
    selects probe output; it never establishes correspondence or replaces primary types.
    """
    names=set()
    for type_name in type_names:
        for d in g.game_types.get(type_name,[]):
            struct=g.dies.get(d.get('type_ref'))
            if not struct or struct['tag']!='DW_TAG_structure_type': continue
            for member in g.children.get(struct['offset'],[]):
                if member['tag']!='DW_TAG_member': continue
                pointer=g.dies.get(member.get('type_ref'))
                if not pointer or pointer['tag']!='DW_TAG_pointer_type': continue
                target=g.dies.get(pointer.get('type_ref'))
                if target and target['tag']=='DW_TAG_typedef' and target.get('name'): names.add(target['name'])
    return names


def interface_pointee_names(g, function_names):
    """Typedef names behind pointer parameters/returns of the named historical functions.

    A CU that spells a function through a void-pointer placeholder never uses the historical
    pointee type, so optimized DWARF omits it; requesting the name only selects probe output.
    """
    names=set()
    for d in g.dies.values():
        if d['tag']!='DW_TAG_subprogram' or d.get('name') not in function_names: continue
        refs=[d.get('type_ref')]+[c.get('type_ref') for c in g.children.get(d['offset'],[]) if c['tag']=='DW_TAG_formal_parameter']
        for ref in refs:
            node=g.dies.get(ref)
            while node and node['tag'] in ('DW_TAG_const_type','DW_TAG_volatile_type','DW_TAG_pointer_type'): node=g.dies.get(node.get('type_ref'))
            if node and node['tag']=='DW_TAG_typedef' and node.get('name'): names.add(node['name'])
    return names


def supplement(report,dest,objdump):
    from type_graph import graph
    g=graph(); names=set()
    for source in report['build']['local_inputs']:
        if source.startswith(('src/','include/')):
            names.update(re.findall(r'\b[A-Za-z_]\w*\b',(ROOT/source).read_bytes().decode('cp1252')))
    missing=requested_types(report,names,g.game_types)
    present={t['name'] for t in report['candidate_debug']['typedefs']}
    missing|=member_pointee_names(g,names&set(g.game_types))-present
    missing|=interface_pointee_names(g,names)-present
    if not missing: return
    build=report['build'];extra=build['config'].get('flags',[])
    flags=build['flags'][:-len(extra)] if extra else build['flags']
    obj,probe_build=compile_target(build['target'],flags=[*flags,FLAG],dest=dest/'interface-types',compiler=build['compiler'])
    binary=Binary(obj)
    debug=candidate_debug(probe_build,objdump,extra_names=missing)
    if identity(obj)!=probe_build['object']: raise ValueError('Interface type probe changed during extraction')
    report['interface_type_probe']={
        'build':probe_build,'object':debug['object'],
        'fingerprint':fingerprint(binary.sections,binary.symbols,binary.relocations),
        'typedefs':[t for t in debug['typedefs'] if t['name'] in missing],
        'requested_types':sorted(missing),
        'scope':'Missing interface typedef layouts only. Separate debug-retention build; exact non-debug bytes/symbols/relocations and input identities must match. No replacement of baseline typedefs or reconstruction proof.'}
    validate(report)


def interface_typedefs(report):
    primary=list(report.get('candidate_debug',{}).get('typedefs',[]))
    probe=report.get('interface_type_probe')
    if not probe: return primary
    validate(report)
    present={t['name'] for t in primary}
    return primary+[dict(t,evidence_source='EMISSION_PRESERVING_DEBUG_PROBE') for t in probe['typedefs'] if t['name'] not in present]
