"""Per-source-line byte budget of a reconstruction (diagnostic only; never a proof).

Compiles the translation unit once in an isolated overlay with debug line info, attributes every
candidate instruction of one function to the source line it came from, and compares that with the
historical bytes per line from the original DWARF line table.  The result says which source lines of
a reconstruction produce far fewer (or more) bytes than history, which is the fastest way to find the
statements a large body is still missing.

    python tools/line_budget.py game-main play --body play=docs/attempts/game-main/play-merged.c [--top 40]

With `--regions TAG=LO-HI ...` it reports one row per region of a merged body instead (the spans come
from the `.regions.json` sidecar written by tools/merge_regions.py), charging inlined code to the region
it was inlined into.

Limits: byte counts are a guide to where to look, never evidence that a line is right, and equal counts
can still be different code.  Per-region numbers are only meaningful while the reconstruction inlines
roughly what history inlined: a body far smaller than its original pulls whole callees into itself, and
GCC then attributes that code to the callee's own lines and reorders the blocks, so the caller's regions
can appear empty.  Compare `--focus`'s `inlined here` list before trusting a region row.
"""
import argparse, re, subprocess
from pathlib import Path
from collections import defaultdict
from common import ROOT, read_json
from tu_context_probe import build_text, compile_overlay


def historical_lines(target, fn):
    ledger = read_json(ROOT / 'src/recovery.json')
    for source, entry in ledger.items():
        if not entry.get('verified_report'): continue
        rep = read_json(ROOT / entry['verified_report'])
        if rep['build']['target'] == target: break
    f = next(x for x in rep['functions'] if x['name'] == fn)
    lo, hi = f['va'], f['va'] + f['original_size']
    rows = sorted((r for r in read_json(ROOT / 'evidence/census/line-mappings.json') if lo <= r['address'] < hi), key=lambda r: r['address'])
    out = defaultdict(int)
    for k, r in enumerate(rows):
        end = rows[k + 1]['address'] if k + 1 < len(rows) else hi
        out[(r['file'], r['line'])] += end - r['address']
    return source, f, out


def candidate_lines(out_dir, fn, report):
    """Candidate bytes per source line, from `objdump -dl` on the overlay object: this GCC's objdump
    has no --dwarf=decodedline, but -dl interleaves `file:line` markers with the disassembly."""
    from build import COMPILERS
    objdump = COMPILERS['tdm-2'] / 'bin' / 'objdump.exe'
    text = subprocess.run([str(objdump), '-dl', str(out_dir / 'unit.o')], capture_output=True, text=True).stdout
    f = next(x for x in report['functions'] if x['name'] == fn)
    start = f.get('candidate_offset'); size = f.get('candidate_size')
    if start is None or not size: return {}
    out = defaultdict(int); cur = None; prev = None
    for line in text.splitlines():
        m = re.match(r'^\s*([0-9a-f]+):\t', line)
        if m:
            addr = int(m.group(1), 16)
            if prev is not None and prev[0] is not None and start <= prev[1] < start + size: out[prev[0]] += addr - prev[1]
            prev = (cur, addr); continue
        m = re.match(r'^(?:.*[\\/])?([^\\/:]+):(\d+)$', line.strip())
        if m: cur = (m.group(1), int(m.group(2)))
    if prev is not None and prev[0] is not None and start <= prev[1] < start + size: out[prev[0]] += start + size - prev[1]
    return out


def region_map(new_text, own, body_path):
    """{region tag: (first, last) line number in the generated overlay}, from the `<body>.regions.json`
    sidecar that tools/merge_regions.py writes.  The candidate's line numbers are its own, not the
    historical ones, so per-line comparison across the two files is meaningless; per-region totals are not."""
    import json
    side = Path(str(body_path) + '.regions.json')
    if not side.exists(): return {}
    spans = json.loads(side.read_text(encoding='utf-8'))
    body = Path(body_path).read_text(encoding='utf-8', errors='replace').replace(chr(13) + chr(10), chr(10)).split(chr(10))
    sig = next((k for k, l in enumerate(body) if re.match(r'^[A-Za-z_].*\(.*\)\s*$', l)), 0)
    lines = new_text.replace(chr(13) + chr(10), chr(10)).split(chr(10))
    base = next((k for k, l in enumerate(lines) if l == body[sig]), None)
    if base is None: return {}
    shift = base - sig                          # both sides are 1-based line numbers of the same text
    return {tag: (lo + shift, hi + shift) for tag, (lo, hi) in spans.items()}


def region_bytes(out_dir, fn, report, regions):
    """Candidate bytes per region, attributing inlined code to the region it was inlined into: walk the
    function's instructions in address order and charge every instruction to the last region line seen.
    Our reconstruction inlines callees history did not inline, so their bytes belong to the caller region."""
    from build import COMPILERS
    objdump = COMPILERS['tdm-2'] / 'bin' / 'objdump.exe'
    text = subprocess.run([str(objdump), '-dl', str(out_dir / 'unit.o')], capture_output=True, text=True).stdout
    f = next(x for x in report['functions'] if x['name'] == fn)
    start, size = f.get('candidate_offset'), f.get('candidate_size')
    if start is None or not size: return {}
    spans = sorted(regions.items(), key=lambda kv: kv[1][0])
    def region_of(line):
        for tag, (lo, hi) in spans:
            if lo <= line <= hi: return tag
        return None
    out = defaultdict(int); cur = None; prev = None
    for line in text.splitlines():
        m = re.match(r'^\s*([0-9a-f]+):	', line)
        if m:
            addr = int(m.group(1), 16)
            if prev is not None and start <= prev[1] < start + size and prev[0]: out[prev[0]] += addr - prev[1]
            prev = (cur, addr); continue
        m = re.match(r'^(?:.*[\/])?([^\/:]+):(\d+)$', line.strip())
        if m:
            tag = region_of(int(m.group(2))) if m.group(1) == 'main.c' else None
            if tag: cur = tag                      # a callee's own lines keep the caller's region
    if prev is not None and start <= prev[1] < start + size and prev[0]: out[prev[0]] += start + size - prev[1]
    return out


def budget(target, source, fn, bodies, order='historical', top=40, no_inline=False):
    from experiment import compare
    from recovery_pipeline import OBJDUMP
    spec = {'order': order, 'bodies': bodies}
    new, edits, headers = build_text(target, source, spec)
    out, ref, build, r = compile_overlay(target, source, new, 'line-budget-' + fn, dumps=False, headers=headers, cgraph=False,
                                         extra_flags=('-fno-inline-functions-called-once', '-fno-inline') if no_inline else ())
    if r.returncode:
        raise SystemExit('overlay compile failed:\n' + '\n'.join(l for l in r.stderr.splitlines() if 'error' in l)[:2000])
    report = compare(out / 'unit.o', ref['historical_cu'], ROOT / 'assets/icytower15.exe', OBJDUMP)
    _, _, hist = historical_lines(target, fn)
    f = next(x for x in report['functions'] if x['name'] == fn)   # sizes and offsets of THIS overlay
    cand = candidate_lines(out, fn, report)
    own = source.split('/')[-1]
    keys = sorted(set(hist) | set(cand), key=lambda k: (k[0] != own, k[1]))
    rows = [(k[0], k[1], hist.get(k, 0), cand.get(k, 0)) for k in keys]
    regions = region_map(new, own, ROOT / bodies[fn]) if fn in bodies else {}
    per_region = region_bytes(out, fn, report, regions) if regions else {}
    return f, report, rows, regions, cand, own, per_region


def rows_dict(rows):
    return {(f, l): h for f, l, h, c in rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('function')
    ap.add_argument('--source', default='src/main.c'); ap.add_argument('--order', default='historical')
    ap.add_argument('--body', action='append', default=[], help='name=path retained body (repeatable)')
    ap.add_argument('--top', type=int, default=40, help='show the N largest deficits (0 = every line)')
    ap.add_argument('--lines', help='only lines in this inclusive range, e.g. 3700-3999')
    ap.add_argument('--no-inline', action='store_true', help='measure with inlining off (diagnostic only): makes a body far smaller than its original comparable with history, which inlined none of these callees')
    ap.add_argument('--regions', nargs='*', help='TAG=LO-HI per region of the retained body, e.g. W1a=3405-3530 W2=3700-3999')
    a = ap.parse_args()
    bodies = dict(b.split('=', 1) for b in a.body)
    f, report, rows, regions, cand, own, per_region = budget(a.target, a.source, a.function, bodies, a.order, no_inline=a.no_inline)
    if a.regions:
        ranges = dict(x.split('=', 1) for x in a.regions)
        print('%s: candidate %s of %s bytes' % (a.function, f.get('candidate_size'), f['original_size']))
        print('%-8s %-14s %10s %10s %8s' % ('region', 'historical lines', 'historical', 'candidate', 'delta'))
        for tag, (lo_c, hi_c) in regions.items():
            spec = ranges.get(tag)
            if not spec: continue
            lo, hi = (int(x) for x in spec.split('-'))
            h = sum(v for k, v in rows_dict(rows).items() if k[0] == own and lo <= k[1] <= hi)
            c = per_region.get(tag, 0)
            print('%-8s %-14s %10d %10d %8d' % (tag, spec, h, c, c - h))
        return
    if a.lines:
        lo, hi = (int(x) for x in a.lines.split('-'))
        rows = [r for r in rows if r[0] == a.source.split('/')[-1] and lo <= r[1] <= hi]
    hist_total = sum(r[2] for r in rows); cand_total = sum(r[3] for r in rows)
    print('%s: candidate %s of %s bytes; lines shown: historical %d, candidate %d, deficit %d'
          % (a.function, f.get('candidate_size'), f['original_size'], hist_total, cand_total, hist_total - cand_total))
    ordered = sorted(rows, key=lambda r: r[3] - r[2])
    if a.top: ordered = ordered[:a.top]
    else: ordered = sorted(rows, key=lambda r: (r[0], r[1]))
    print('%-14s %6s %10s %10s %8s' % ('file', 'line', 'historical', 'candidate', 'delta'))
    for file, line, h, c in ordered: print('%-14s %6d %10d %10d %8d' % (file, line, h, c, c - h))


if __name__ == '__main__':
    main()
