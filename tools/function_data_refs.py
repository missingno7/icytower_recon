"""Data references of one original function, resolved (diagnostic only; never a proof or a source input).

    python tools/function_data_refs.py <target> <function> [--json PATH]

For every absolute data address in the original instructions: the DWARF/ownership global name when
one exists, otherwise the read-only literal at that address (C string, or 4/8-byte float constant when
the instruction is an x87 load).  Historical strings and constants are shown so a reconstruction can
spell them as source literals; they are never copied into the build as bytes.
"""
import argparse, json, re, struct
from common import ROOT, read_json
from recovery_pipeline import original_slice
from binary import Binary


def global_names():
    names = {}
    for u in read_json(ROOT / 'src/units.json'):
        for g in u.get('globals', []):
            if g.get('address'): names[g['address']] = (g['name'], u['source'])
    for p in (ROOT / 'docs/current/objects').glob('*.json'):
        own = read_json(p)
        for o in own.get('accepted', []) + own.get('rejected', []):
            names.setdefault(o['original_va'], (o['name'], '/'.join(o['scope'])))
    return names


def literal_at(exe, va, insn):
    try: data = exe.at_va(va, 320)
    except Exception: return None
    if re.match(r'f(ld|add|sub|mul|div|com|ucom)[ls]?\s', insn) or 'movs' in insn:
        if 'fldl' in insn or re.search(r'f\w+l\s', insn): return {'kind': 'double', 'value': struct.unpack_from('<d', data, 0)[0]}
        if 'flds' in insn or re.search(r'f\w+s\s', insn): return {'kind': 'float', 'value': struct.unpack_from('<f', data, 0)[0]}
    end = data.find(b'\0')
    s = data[:end] if end >= 0 else data
    if len(s) >= 1 and all(32 <= c < 127 or c in (9, 10, 13) for c in s): return {'kind': 'string', 'value': s.decode('ascii')}
    return {'kind': 'bytes', 'value': data[:16].hex()}


def refs(target, fn):
    ledger = read_json(ROOT / 'src/recovery.json')
    for source, entry in ledger.items():
        if not entry.get('verified_report'): continue
        rep = read_json(ROOT / entry['verified_report'])
        if rep['build']['target'] == target: break
    f = next(x for x in rep['functions'] if x['name'] == fn)
    names = global_names(); exe = Binary(str(ROOT / 'assets/icytower15.exe'))
    out = {}
    for i in original_slice(f['va'], f['original_size']):
        a = i['assembly']
        if re.match(r'(call|j[a-z]+)\s', a): continue
        for m in re.finditer(r'0x(4[c-f][0-9a-f]{4}|5[0-1][0-9a-f]{4})', a):
            va = int(m.group(1), 16)
            row = out.setdefault(va, {'va': '%x' % va, 'count': 0, 'first_offset': i['address'] - f['va'], 'insn': a})
            row['count'] += 1
    for va, row in out.items():
        if va in names: row['global'] = names[va][0]; row['owner'] = names[va][1]
        else: row['literal'] = literal_at(exe, va, row['insn'])
    return [out[k] for k in sorted(out)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('function'); ap.add_argument('--json')
    a = ap.parse_args(); rows = refs(a.target, a.function)
    for r in rows:
        what = r.get('global') or (r['literal']['kind'] + ' ' + json.dumps(r['literal']['value']) if r.get('literal') else '?')
        print('%s %3d @%-6d %s' % (r['va'], r['count'], r['first_offset'], what))
    if a.json:
        with open(a.json, 'w') as fh: json.dump(rows, fh, indent=1)


if __name__ == '__main__':
    main()
