"""Merge per-region reconstructions of one function into a single retained body (diagnostic only).

Every region file is a copy of one skeleton in which exactly one `/* REGION <tag> ... */` marker was
replaced by code.  Each file is line-diffed against the skeleton; the changed lines must all fall in
one contiguous span that covers exactly that file's own marker, so the regions cannot overlap.  The
merge then rebuilds the skeleton with every span substituted.  The result is one complete definition.

    python tools/merge_regions.py BASE.c REGION.c [REGION.c ...] --out MERGED.c
"""
import argparse, difflib, re
from pathlib import Path

MARKER = re.compile(r'^[ \t]*/\* REGION (\w+)\b')


def read(path):
    return Path(path).read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n').split('\n')


def chunks(lines, tags):
    """{tag: lines following that marker up to the next BASE marker}. Markers not in `tags`
    (sub-markers a region introduced inside its own text) do not delimit."""
    positions = [(k, MARKER.match(l).group(1)) for k, l in enumerate(lines) if MARKER.match(l) and MARKER.match(l).group(1) in tags]
    out = {}
    for n, (k, tag) in enumerate(positions):
        end = positions[n + 1][0] if n + 1 < len(positions) else len(lines)
        out[tag] = lines[k + 1:end]
    return out


def merge(base_path, region_paths):
    """Base tags in order; each file either kept its marker and appended its code after it, or replaced
    the marker outright (then its code appears at the tail of the preceding chunk)."""
    base = read(base_path)
    tags = [MARKER.match(l).group(1) for l in base if MARKER.match(l)]
    base_chunks = chunks(base, tags)
    head = base[:next(k for k, l in enumerate(base) if MARKER.match(l))]
    filled = {}
    def claim(tag, body, p):
        if tag in filled: raise ValueError('Two files fill region ' + tag + ': ' + str(p) + ' and ' + str(filled[tag][1]))
        filled[tag] = (body, p)
    for p in region_paths:
        lines = read(p); present = {MARKER.match(l).group(1) for l in lines if MARKER.match(l)}
        cur = chunks(lines, tags)
        bodies = {}; host_of = {}
        first = next((k for k, l in enumerate(lines) if MARKER.match(l)), len(lines))
        bodies[None] = lines[:first]; base_chunks[None] = head
        host = None
        for tag in tags:
            if tag in present: bodies[tag] = cur[tag]; host = tag; continue
            prev = bodies[host]; base_prev = base_chunks[host]      # marker replaced: split the host chunk
            k = 0
            while k < min(len(prev), len(base_prev)) and prev[k] == base_prev[k]: k += 1
            bodies[host] = prev[:k]; bodies[tag] = prev[k:]; host = tag
            base_chunks[tag] = base_chunks.get(tag, [])
        for tag in tags:
            if [l for l in bodies.get(tag, []) if l.strip()] != [l for l in base_chunks[tag] if l.strip()]: claim(tag, bodies[tag], p)
    out = []; pos = 0; used = []; spans = {}
    positions = [(k, MARKER.match(l).group(1)) for k, l in enumerate(base) if MARKER.match(l)]
    for n, (k, tag) in enumerate(positions):
        end = positions[n + 1][0] if n + 1 < len(positions) else len(base)
        out.extend(base[pos:k])
        first = len(out) + 1                      # 1-based line number in the merged file
        if tag in filled: out.extend(filled[tag][0]); used.append(tag)
        else: out.extend(base[k:end])
        spans[tag] = [first, len(out)]
        pos = end
    out.extend(base[pos:])
    return chr(10).join(out), used, spans


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('base'); ap.add_argument('regions', nargs='+'); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    text, used, spans = merge(a.base, a.regions)
    Path(a.out).write_text(text, encoding='utf-8', newline='')
    import json
    Path(a.out + '.regions.json').write_text(json.dumps(spans, indent=1), encoding='utf-8')
    print('merged regions', ' '.join(used), '->', a.out, len(text.split(chr(10))), 'lines; spans in', a.out + '.regions.json')


if __name__ == '__main__':
    main()
