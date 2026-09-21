"""Bounded compound search for a translation-unit context repair (diagnostic; never a promotion).

Candidate edits come only from historical evidence: each edit places one definition island, or a
DWARF-contiguous block of islands, directly after its historical DWARF predecessor.  Combinations of up
to three edits are compiled once each (with any retained complete bodies enabled), and the final unit
state is recorded: matches, gains, losses, historical-predecessor count.  No permutations, no body
mutation.  Results: docs/attempts/tu-context/<target>/<label>.json (summary rows only).

    python tools/tu_context_repair_search.py game-main src/main.c --involved checkMenuFocus startGameMusic \\
        --block startMenuMusic:4 --body handle_player_input=docs/attempts/game-main/handle_player_input-reconstruction.c
"""
import argparse, itertools, json, sys
from common import ROOT, read_json, write_json
from tu_context_probe import islands, historical_order, build_text, evaluate, EVIDENCE


def anchored_edits(cur, hist, involved, blocks):
    hpos = {n: i for i, n in enumerate(hist)}
    pred = lambda n: hist[hpos[n] - 1] if hpos[n] else None
    edits = {}
    for n in involved:
        if n in hpos and pred(n): edits['after:%s>%s' % (pred(n), n)] = ([n], pred(n))
    for spec in blocks:
        first, k = spec.split(':'); block = hist[hpos[first]:hpos[first] + int(k)]
        if pred(first): edits['block:%s:%d' % (first, len(block))] = (block, pred(first))
    return edits


def apply(order, block, anchor):
    o = [x for x in order if x not in block]; i = o.index(anchor) + 1
    for k, n in enumerate(block): o.insert(i + k, n)
    return o


def search(target, source, involved, blocks, bodies, max_edits=3, label='bounded-repair-search'):
    text = (ROOT / source).read_bytes().decode('cp1252'); cur = [i['name'] for i in islands(text)]
    unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == source)
    hist, lines = historical_order(unit, source); hist = [n for n in hist if n in cur]
    edits = anchored_edits(cur, hist, involved, blocks)
    rows = []
    for r in range(1, max_edits + 1):
        for combo in itertools.combinations(list(edits), r):
            order = list(cur)
            for k in combo: order = apply(order, *edits[k])
            new, ed, headers = build_text(target, source, {'order': order, 'bodies': bodies})
            rec = evaluate(target, source, new, label + '-candidate', ed, dumps=False, headers=headers)
            row = {'edits': list(combo), 'order': order, 'compile': rec['compile'], 'errors': rec.get('errors'), 'matches': rec.get('matches_after'), 'gains': rec.get('gains'),
                   'losses': rec.get('losses'), 'new_implicit_declarations': rec.get('new_implicit_declarations'), 'same_historical_predecessor': (rec.get('same_historical_predecessor') or {}).get('after')}
            rows.append(row); print(json.dumps({k: row[k] for k in ('edits', 'compile', 'matches', 'gains', 'losses', 'same_historical_predecessor')}), flush=True)
    (EVIDENCE / target / (label + '-candidate.json')).unlink(missing_ok=True)
    record = {'scope': 'Bounded historical-anchor compound search on isolated overlays; diagnostic only, never a proof or a production edit.',
              'target': target, 'source': source, 'bodies': bodies, 'edits': {k: {'block': v[0], 'after_historical_predecessor': v[1], 'historical_lines': {n: lines.get(n) for n in v[0] + [v[1]]}} for k, v in edits.items()},
              'acceptable': [r['edits'] for r in rows if r['compile'] == 'OK' and not r['losses'] and not r['new_implicit_declarations']], 'results': rows}
    write_json(EVIDENCE / target / (label + '.json'), record)
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('source')
    ap.add_argument('--involved', nargs='*', default=[], help='functions whose island moves after its historical predecessor')
    ap.add_argument('--block', action='append', default=[], help='FIRST:K — K DWARF-consecutive islands starting at FIRST move after FIRST\'s predecessor')
    ap.add_argument('--body', action='append', default=[], help='name=path retained complete definition enabled in every candidate')
    ap.add_argument('--max-edits', type=int, default=3); ap.add_argument('--label', default='bounded-repair-search')
    a = ap.parse_args()
    rec = search(a.target, a.source, a.involved, a.block, dict(b.split('=', 1) for b in a.body), a.max_edits, a.label)
    print('acceptable:', json.dumps(rec['acceptable']))


if __name__ == '__main__':
    main()
