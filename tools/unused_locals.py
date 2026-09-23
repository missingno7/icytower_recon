"""DWARF local names unmentioned by reconstruction code (diagnostic only; never a proof).

Optimized DWARF may name a local with no surviving machine location or instructions. A missing
name is a lead to check scope, location lists, lifetime, and original instructions; it is not
proof of missing behavior. Comments and string literals in the candidate do not count as usage.

    python tools/unused_locals.py game-main play --body docs/attempts/game-main/play-merged.c
    python tools/unused_locals.py game-main draw_frame --body docs/attempts/game-main/draw_frame-merged.c

Each row gives the local's type, location attribute, lexical block, and historical line span.
The line span locates an investigation, not necessarily a missing statement.
"""
import argparse, bisect, json, re
from common import ROOT, read_json
from source_scope import sanitized

BASE_OF_CU = {}


def cu_base(path_fragment):
    """low_pc of the compilation unit, the base that its DWARF range lists are relative to."""
    if path_fragment not in BASE_OF_CU:
        for c in read_json(ROOT / 'evidence/census/compilation-units.json'):
            if path_fragment in c['path']:
                BASE_OF_CU[path_fragment] = c['low_pc']; break
        else:
            raise SystemExit('no compilation unit matching ' + path_fragment)
    return BASE_OF_CU[path_fragment]


def line_index(own):
    rows = [x for x in read_json(ROOT / 'evidence/census/line-mappings.json')
            if x.get('address') and x.get('file', '').endswith(own)]
    rows.sort(key=lambda r: r['address'])
    return [r['address'] for r in rows], rows


def spans(block, base, ranges):
    """Every (low, high) PC range of a lexical block, whether inline or in .debug_ranges."""
    if block.get('low_pc'):
        return [(block['low_pc'], block['high_pc'])]
    off = block.get('ranges')
    if off is None:
        return []
    table = ranges.get(off if isinstance(off, int) else int(str(off), 0))
    return [(base + e['begin'], base + e['end']) for e in (table or {}).get('entries', []) if e['kind'] == 'range']


def unmentioned(locals_, source):
    """Keep distinct DWARF locals, and search only C tokens outside comments/literals."""
    code = sanitized(source)
    seen, missing = set(), []
    for local in locals_:
        key = local.get('die', (local['name'], local.get('scope')))
        if key in seen: continue
        seen.add(key)
        if not re.search(r'\b' + re.escape(local['name']) + r'\b', code):
            missing.append(local)
    return len(seen), missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('function')
    ap.add_argument('--body', required=True, help='the reconstruction to check (a retained body or a merged one)')
    ap.add_argument('--source', default='src/main.c')
    a = ap.parse_args()

    own = a.source.split('/')[-1]
    stem = own.rsplit('.', 1)[0]
    ev = read_json(ROOT / 'docs/current/function-evidence' / stem / (a.function + '.json'))
    text = (ROOT / a.body).read_text(encoding='utf-8', errors='replace')

    base = cu_base(stem + '.c')
    ranges = {t['offset']: t for t in read_json(ROOT / 'evidence/census/range-lists.json')}
    addrs, rows = line_index(own)

    def at(pc):
        i = bisect.bisect_right(addrs, pc) - 1
        return rows[i]['line'] if i >= 0 else 0

    where = {}
    for b in ev.get('lexical_blocks', []):
        ls = [(at(lo), at(hi - 1)) for lo, hi in spans(b, base, ranges)]
        if ls: where[b['die']] = '%d..%d' % (min(x for x, _ in ls), max(y for _, y in ls))

    total, missing = unmentioned(ev.get('locals', []), text)

    print('%s: %d DWARF locals, %d unmentioned in code of %s' % (a.function, total, len(missing), a.body))
    if not missing: return
    print('%-22s %-14s %-10s %-22s %s' % ('local', 'type', 'block', 'location', 'historical lines'))
    for l in sorted(missing, key=lambda x: (where.get(x.get('scope'), ''), x['name'])):
        print('%-22s %-14s %-10s %-22s %s' % (l['name'], l.get('type'), l.get('scope'),
                                                 str(l.get('location') or 'none')[:22], where.get(l.get('scope'), '')))


if __name__ == '__main__':
    main()
