"""DWARF locals of an original function that a reconstruction never mentions (diagnostic only; never a proof).

The compiler allocated a stack slot or a register for every local the historical source declared, so a
local whose name appears nowhere in our reconstruction marks statements we have not recovered.  Unlike a
byte budget this does not depend on line attribution, cross-jumping or inlining, so it stays meaningful
while a body is still far from its original size -- in `play` it located a debug-timing block, an
achievements loop that our source had written as two string copies, and the target variables of an
easing block that two byte-budget passes had failed to find.

    python tools/unused_locals.py game-main play --body docs/attempts/game-main/play-merged.c
    python tools/unused_locals.py game-main draw_frame --body docs/attempts/game-main/draw_frame-merged.c

Each row gives the local's type, its DWARF lexical block, and that block's historical line span, which is
where the missing statements are.  A name absent here is evidence of a gap; a name present is no evidence
of anything, since our source may use it for something else entirely.
"""
import argparse, bisect, json, re
from common import ROOT, read_json

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

    seen, missing = set(), []
    for l in ev.get('locals', []):
        n = l['name']
        if n in seen: continue
        seen.add(n)
        if not re.search(r'\b' + re.escape(n) + r'\b', text):
            missing.append((l, where.get(l.get('scope'), '')))

    print('%s: %d DWARF locals, %d never mentioned in %s' % (a.function, len(seen), len(missing), a.body))
    if not missing: return
    print('%-22s %-14s %-10s %s' % ('local', 'type', 'block', 'historical lines'))
    for l, span in sorted(missing, key=lambda x: (x[1], x[0]['name'])):
        print('%-22s %-14s %-10s %s' % (l['name'], l.get('type'), l.get('scope'), span))


if __name__ == '__main__':
    main()
