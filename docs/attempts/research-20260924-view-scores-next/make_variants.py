import pathlib

base = pathlib.Path('docs/attempts/research-luna-view-scores-20260924/view-scores-key-call-and-constants.c').read_text(encoding='utf-8-sig')
needle = 'while (!cycle_count)'
assert base.count(needle) == 2, base.count(needle)
out = pathlib.Path('docs/attempts/research-20260924-view-scores-next')
labels = {
    'view-scores-first-wait-nonpositive.c': [0],
    'view-scores-second-wait-nonpositive.c': [1],
    'view-scores-both-waits-nonpositive.c': [0, 1],
}
for name, changed in labels.items():
    lines = base.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if needle in line]
    for index in changed:
        lines[hits[index]] = lines[hits[index]].replace(needle, 'while (cycle_count <= 0)')
    (out / name).write_text(''.join(lines), encoding='utf-8')
