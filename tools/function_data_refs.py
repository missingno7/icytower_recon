"""Data references of one original function, resolved (diagnostic only; never a proof or a source input).

    python tools/function_data_refs.py <target> <function> [--json PATH]

For every absolute data address in the original instructions: the DWARF/ownership global name when
one exists, otherwise the read-only literal at that address (C string, or 4/8-byte float constant when
the instruction is an x87 load).  Historical strings and constants are shown so a reconstruction can
spell them as source literals; they are never copied into the build as bytes.
"""
import argparse, bisect, json, re, struct
from common import ROOT, read_json
from recovery_pipeline import original_slice
from binary import Binary


def global_names():
    """{va: (name, owner, size)} for every addressed DWARF global and every proven data owner."""
    from type_graph import graph
    g = graph(); names = {}
    for u in read_json(ROOT / 'src/units.json'):
        for v in u.get('globals', []):
            if v.get('address'): names[v['address']] = (v['name'], u['source'], g.size(v.get('type_ref')), v.get('type_ref'))
    for r in read_json(ROOT / 'evidence/census/globals.json'):
        if r.get('address'): names.setdefault(r['address'], (r['name'], (r.get('cu') or '').replace(chr(92), '/').rsplit('/', 1)[-1], g.size(r.get('type_ref'))))
    for p in (ROOT / 'docs/current/objects').glob('*.json'):
        own = read_json(p)
        for o in own.get('accepted', []) + own.get('rejected', []):
            names.setdefault(o['original_va'], (o['name'], '/'.join(o['scope']), o.get('size'), o.get('original_die')))
    return names


def scancode_names():
    """Allegro scancode constants (KEY_*) from the vendored header, for `key[KEY_x]` indices."""
    header = ROOT / 'third_party/allegro-4.4.1/include/allegro/keyboard.h'
    if not header.exists(): return {}
    text = header.read_text(errors='replace'); out = {}
    for m in re.finditer(r'__allegro_(KEY_\w+)\s*=\s*(\d+)', text): out[int(m.group(2))] = m.group(1)
    last = None
    for m in re.finditer(r'__allegro_(KEY_\w+)\s*(?:=\s*(\d+))?', text):
        last = int(m.group(2)) if m.group(2) else (last + 1 if last is not None else None)
        if last is not None: out.setdefault(last, m.group(1))
    return out


def access(name, type_ref, delta, g, scancodes=None):
    if name == 'key' and scancodes and delta in scancodes: return 'key[%s]' % scancodes[delta]
    """A C access expression for byte `delta` inside the global `name` (array index / member path)."""
    if not delta: return name
    try:
        from dwarf_layout import layout, reference
        hit = reference(layout(g, type_ref), delta, name)
        if hit and hit.get('expression'): return hit['expression']
    except Exception: pass
    return '%s + %d' % (name, delta)


def resolve(va, names, bases=None):
    """Exact global, or `name + N` when `va` falls inside an addressed global of known size."""
    if va in names: return names[va][0], names[va][1], 0
    bases = bases if bases is not None else sorted(names)
    i = bisect.bisect_right(bases, va) - 1
    while i >= 0:
        base = bases[i]; name, owner, size = names[base][:3]
        if size and base + size > va: return name, owner, va - base
        if size and base + size <= va: break
        i -= 1
    return None, None, None


def data_section(exe, va):
    """Use the PE's actual virtual ranges; never guess an address prefix."""
    for section in exe.sections:
        start = exe.image_base + section['rva']
        if start <= va < start + section['virtual_size']:
            return section
    return None


def literal_at(exe, va, insn, section=None):
    section = section or data_section(exe, va)
    if not section or section['name'] not in ('.data', '.rdata'):
        return {'kind': 'unknown', 'value': None}
    available = section['raw_size'] - (va - exe.image_base - section['rva'])
    if available <= 0:
        return {'kind': 'unknown', 'value': None}
    try: data = exe.at_va(va, min(320, available))
    except Exception: return {'kind': 'unknown', 'value': None}
    x87 = re.match(r'f(?:ld|add|subr?|mul|divr?|comp?)([sl])\s', insn)
    if x87:
        if x87.group(1) == 'l' and len(data) >= 8: return {'kind': 'double', 'value': struct.unpack_from('<d', data, 0)[0]}
        if x87.group(1) == 's' and len(data) >= 4: return {'kind': 'float', 'value': struct.unpack_from('<f', data, 0)[0]}
    end = data.find(b'\0')
    if end == 0: return {'kind': 'empty_string', 'value': ''}
    s = data[:end] if end >= 0 else data
    if len(s) >= 1 and all(32 <= c < 127 or c in (9, 10, 13) for c in s): return {'kind': 'string', 'value': s.decode('ascii')}
    return {'kind': 'unknown', 'value': data[:16].hex()}


def reference(exe, va, insn, names, bases, g, scancodes):
    """Classify even unresolved references so a caller cannot silently drop one."""
    if va == 0:
        return {'kind': 'null_pointer', 'value': None}
    section = data_section(exe, va)
    if not section:
        return {'kind': 'unknown', 'value': None, 'section': None}
    name, owner, delta = resolve(va, names, bases)
    if name:
        base = va - delta
        type_ref = names[base][3] if len(names[base]) > 3 else None
        return {'kind': 'data_object', 'global': access(name, type_ref, delta, g, scancodes),
                'owner': owner, 'base_offset': delta, 'section': section['name']}
    return {'kind': 'literal', 'literal': literal_at(exe, va, insn, section), 'section': section['name']}


def refs(target, fn):
    ledger = read_json(ROOT / 'src/recovery.json')
    rep = None
    for source, entry in ledger.items():
        if not entry.get('verified_report'): continue
        rep = read_json(ROOT / entry['verified_report'])
        if rep['build']['target'] == target: break
    else: raise ValueError('No verified report for ' + target)
    f = next(x for x in rep['functions'] if x['name'] == fn)
    names = global_names(); bases = sorted(names); exe = Binary(str(ROOT / 'assets/icytower15.exe'))
    out = {}
    for i in original_slice(f['va'], f['original_size']):
        a = i['assembly']
        if re.match(r'(call|j[a-z]+)\s', a): continue
        for m in re.finditer(r'(?<![\w])0x([0-9a-fA-F]+)\b', a):
            va = int(m.group(1), 16)
            if not exe.image_base <= va < exe.image_base + exe.optional['size_of_image']:
                continue
            section = data_section(exe, va)
            if section and (section['name'] == '.text' or section['name'].startswith('.debug')):
                continue
            row = out.setdefault(va, {'va': '%x' % va, 'count': 0, 'first_offset': i['address'] - f['va'], 'insn': a})
            row['count'] += 1
    from type_graph import graph
    g = graph(); scancodes = scancode_names()
    for va, row in out.items():
        row.update(reference(exe, va, row['insn'], names, bases, g, scancodes))
    return [out[k] for k in sorted(out)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('function'); ap.add_argument('--json')
    a = ap.parse_args(); rows = refs(a.target, a.function)
    for r in rows:
        what = r.get('global') or (r['literal']['kind'] + ' ' + json.dumps(r['literal']['value']) if r.get('literal') else r['kind'])
        print('%s %3d @%-6d %s' % (r['va'], r['count'], r['first_offset'], what))
    if a.json:
        with open(a.json, 'w') as fh: json.dump(rows, fh, indent=1)


if __name__ == '__main__':
    main()
