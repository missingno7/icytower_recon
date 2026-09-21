"""Locals of a reconstructed body that are read before they are written (diagnostic only).

A local that is read before any assignment makes its dependent code undefined, and GCC then deletes
whole blocks: a reconstruction can lose its entire main loop that way and still compile cleanly.  This
reports, for one retained body, every declared local with no write at all or whose first textual read
precedes its first write, so the missing historical initialization can be found.

    python tools/uninitialized_locals.py docs/attempts/game-main/play-merged.c

Textual analysis of one function body, not a compiler warning: a write inside a branch still counts,
and a read through a pointer or a macro is not seen.  Use it to find suspects, then check the
historical line table for where the initialization belongs.
"""
import argparse, re
from pathlib import Path

DECL = re.compile(r'^[ \t]+(?:const\s+)?(?:unsigned\s+|signed\s+|struct\s+|long\s+|short\s+)*[A-Za-z_]\w*\s*\**\s*(\w+)\s*(?:\[[^\]]*\])?\s*;[ \t]*$', re.M)
WRITE = r'\s*(?:=(?!=)|\+\+|--|\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<=|>>=)'


def report(path):
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    start = text.index('{')
    body = text[start:]
    rows = []
    for m in DECL.finditer(body):
        name = m.group(1)
        after = body[m.end():]
        writes = [w.start() for w in re.finditer(r'\b' + re.escape(name) + r'\b' + WRITE, after)]
        writes += [w.start() for w in re.finditer(r'(?:\+\+|--)\s*\b' + re.escape(name) + r'\b', after)]
        reads = [r.start() for r in re.finditer(r'\b' + re.escape(name) + r'\b', after)]
        if not writes: rows.append((name, 'never written', line_of(body, m.start())))
        elif reads and min(reads) < min(writes): rows.append((name, 'read before first write', line_of(body, m.start())))
    seen = set(); out = []
    for r in rows:
        if r[:2] in seen: continue
        seen.add(r[:2]); out.append(r)
    return out


def line_of(text, pos):
    return text.count(chr(10), 0, pos) + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('body', nargs='+')
    a = ap.parse_args()
    for path in a.body:
        rows = report(path)
        print('%s: %d locals read before written or never written' % (path, len(rows)))
        for name, why, line in rows: print('  %-22s %-24s near body line %d' % (name, why, line))


if __name__ == '__main__':
    main()
