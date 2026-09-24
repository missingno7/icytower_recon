from pathlib import Path
p=Path('docs/attempts/research-20260924-view-scores-next/view-scores-both-waits-nonpositive.c')
s=p.read_text(encoding='utf-8-sig')
old='while (is_any(get_controls()) || key[KEY_K])'
new='while (is_any(get_controls()) || key[KEY_SPACE])'
assert s.count(old)==1, s.count(old)
out=Path('docs/attempts/research-20260924-view-scores-next/view-scores-space-drain-key.c')
out.write_text(s.replace(old,new),encoding='utf-8')
