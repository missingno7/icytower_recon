"""Historical source skeleton of one original function from DWARF (diagnostic only; never a proof).

    python tools/function_lines.py <target> <function> [--lines] [--blocks] [--calls-by-line] [--json PATH]

--lines          address-ordered line table rows inside the function: offset, file:line, and the direct
                 calls / tail jumps executed before the next row (the historical statement sequence).
--blocks         DW_TAG_lexical_block tree with the locals declared in each block (name, type, location).
--calls-by-line  every distinct historical source line with its calls, in line order (a call list per
                 source line is the most direct guide for reconstructing a region).
The line rows include lines of other files (inlined header functions) and of `inline` helpers defined
elsewhere in the same file; they are shown with their file name so the inline expansions are visible.
"""
import argparse, json, re, sys
from collections import defaultdict
from common import ROOT, read_json
from recovery_pipeline import original_slice
from tu_context_model import exe_functions


def rows_for(target, fn):
    ledger = read_json(ROOT / 'src/recovery.json')
    for source, entry in ledger.items():
        if not entry.get('verified_report'): continue
        rep = read_json(ROOT / entry['verified_report'])
        if rep['build']['target'] != target: continue
        f = next(x for x in rep['functions'] if x['name'] == fn)
        return source, f
    raise SystemExit('unknown target ' + target)


def line_rows(f):
    lo, hi = f['va'], f['va'] + f['original_size']
    rows = [r for r in read_json(ROOT / 'evidence/census/line-mappings.json') if lo <= r['address'] < hi]
    rows.sort(key=lambda r: r['address'])
    return rows


def calls(f, names):
    out = []
    for i in original_slice(f['va'], f['original_size']):
        m = re.match(r'(call|jmp)\s+([0-9a-f]+)', i['assembly'])
        if not m: continue
        va = int(m.group(2), 16)
        if f['va'] <= va < f['va'] + f['original_size']: continue
        out.append((i['address'] - f['va'], m.group(1), names.get(va, 'ext_%x' % va)))
    return out


def skeleton(target, fn):
    source, f = rows_for(target, fn); names = exe_functions()
    rows = line_rows(f); cs = calls(f, names)
    seq = []
    for k, r in enumerate(rows):
        nxt = rows[k + 1]['address'] if k + 1 < len(rows) else f['va'] + f['original_size']
        here = [c for c in cs if r['address'] - f['va'] <= c[0] < nxt - f['va']]
        seq.append({'offset': r['address'] - f['va'], 'end': nxt - f['va'], 'file': r['file'], 'line': r['line'], 'calls': [c[2] for c in here], 'tail_jumps': [c[2] for c in here if c[1] == 'jmp']})
    by_line = defaultdict(list); first = {}
    for s in seq:
        key = (s['file'], s['line']); by_line[key].extend(s['calls']); first.setdefault(key, s['offset'])
    evidence = ROOT / 'docs/current/function-evidence' / source.split('/')[-1].rsplit('.', 1)[0] / (fn + '.json')
    ev = read_json(evidence) if evidence.exists() else {}
    unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == source)
    return {'function': fn, 'va': f['va'], 'size': f['original_size'], 'cu_low_pc': unit.get('low_pc'), 'source_file_lines': sorted({s['line'] for s in seq if s['file'] == source.split('/')[-1]}),
            'sequence': seq, 'calls_by_line': [{'file': k[0], 'line': k[1], 'first_offset': first[k], 'calls': v} for k, v in sorted(by_line.items(), key=lambda kv: (kv[0][0] != source.split('/')[-1], kv[0][1]))],
            'lexical_blocks': ev.get('lexical_blocks', []), 'locals': ev.get('locals', [])}


def source_view(target, fn, lo, hi, data_names=True):
    """Instructions regrouped in SOURCE-LINE order for lines lo..hi of the function's own file: every
    fragment of the (block-reordered) machine code that the line table attributes to a line is printed
    under that line, in offset order.  This undoes -O2 block reordering for reading; it is not a proof."""
    source, f = rows_for(target, fn); sk = skeleton(target, fn); own = source.split('/')[-1]
    insns = {i['address'] - f['va']: i['assembly'] for i in original_slice(f['va'], f['original_size'])}
    offs = sorted(insns)
    names = {}
    if data_names:
        try:
            from function_data_refs import refs
            for r in refs(target, fn):
                names[r['va']] = r.get('global') or (repr(r['literal']['value']) if r.get('literal') and r['literal']['kind'] != 'bytes' else None)
        except Exception: pass
    frags = defaultdict(list)
    for s_ in sk['sequence']:
        if s_['file'] == own and lo <= s_['line'] <= hi: frags[s_['line']].append((s_['offset'], s_['end']))
        elif s_['file'] != own:
            # attribute inlined-header rows to the nearest preceding own-file line
            pass
    for line in sorted(frags):
        parts = sorted(frags[line])
        print('---- %s:%d   fragments %s' % (own, line, ' '.join('%d..%d' % p for p in parts)))
        for a, b in parts:
            for o in offs:
                if a <= o < b:
                    text = insns[o]
                    for va, nm in names.items():
                        if nm and va in text: text = text.replace(va, va + '<' + nm + '>')
                    print('%7d  %s' % (o, text))


def print_blocks(sk):
    blocks = {b['die']: b for b in sk['lexical_blocks']}; children = defaultdict(list)
    for b in sk['lexical_blocks']: children[b['parent']].append(b)
    locs = defaultdict(list)
    for l in sk['locals']: locs[l['scope']].append(l)
    root = [p for p in children if p not in blocks]
    rel = lambda a: a + (sk.get('cu_low_pc') or 0) - sk['va']   # range/location lists are CU-relative
    def rng(b):
        if b.get('low_pc') is not None: return '%d..%d' % (b['low_pc'] - sk['va'], b['high_pc'] - sk['va'])
        if b.get('range_list'): return ' '.join('%d..%d' % (rel(e['begin']), rel(e['end'])) for e in b['range_list']['entries'] if e.get('kind') == 'range')
        return '?'
    def where(l):
        ll = l.get('location_list')
        if ll: return 'ranges ' + ' '.join('%d..%d' % (rel(e['begin']), rel(e['end'])) for e in ll['entries'][:4] if e.get('kind') == 'range') + (' ...' if len(ll['entries']) > 4 else '')
        loc = l.get('location') or ''
        m = re.search(r'\((DW_OP_\w+)[^)]*?(-?\d+)\)', loc)
        return (m.group(1).replace('DW_OP_', '') + ' ' + m.group(2)) if m else loc[:50]
    def show(parent, depth):
        for l in locs.get(parent, []): print('  ' * depth + '  %-28s %-22s %s' % (l['type'], l['name'], where(l)))
        for b in sorted(children.get(parent, []), key=lambda b: (b.get('low_pc') or (b['range_list']['entries'][0]['begin'] if b.get('range_list') else 0))):
            print('  ' * depth + 'block %s [%s]' % (b['die'], rng(b))); show(b['die'], depth + 1)
    for r in root: show(r, 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('function')
    ap.add_argument('--lines', action='store_true'); ap.add_argument('--blocks', action='store_true'); ap.add_argument('--calls-by-line', action='store_true'); ap.add_argument('--json')
    ap.add_argument('--source-view', nargs=2, type=int, metavar=('LO', 'HI'), help='instructions regrouped in source-line order for lines LO..HI')
    a = ap.parse_args()
    if a.source_view: source_view(a.target, a.function, *a.source_view); return
    sk = skeleton(a.target, a.function)
    if a.lines:
        for s in sk['sequence']: print('%6d..%-6d %s:%-5d %s' % (s['offset'], s['end'], s['file'], s['line'], ' '.join(s['calls'])))
    if a.calls_by_line:
        for r in sk['calls_by_line']: print('%s:%-5d @%-6d %s' % (r['file'], r['line'], r['first_offset'], ' '.join(r['calls'])))
    if a.blocks: print_blocks(sk)
    if a.json:
        with open(a.json, 'w') as fh: json.dump(sk, fh, indent=1)
    if not (a.lines or a.blocks or a.calls_by_line or a.json or a.source_view):
        print(a.function, 'size', sk['size'], 'line rows', len(sk['sequence']), 'source lines', len(sk['source_file_lines']), 'range', sk['source_file_lines'][:1], sk['source_file_lines'][-1:])


if __name__ == '__main__':
    main()
