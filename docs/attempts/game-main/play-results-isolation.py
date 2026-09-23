"""Recreate the two source variants used by the result-wait TU probes."""
from pathlib import Path

root = Path(__file__).resolve().parents[3]
source = (root / 'docs/attempts/game-main/play-results-waits-base.c').read_text(encoding='cp1252')
out = root / 'build/tu-context/game-main/branch-isolation'
out.mkdir(parents=True, exist_ok=True)

f1_wait = '                    while (key[KEY_F1]) { }  /* 4727: wait for release at 13091..13105 */\n'
tab_wait = ('                    do {\n'
            '                        rest(2);                                                      /* 4734 */\n'
            '                    } while (cycle_count == 0);')
old_tab = ('                    rest(2);                                                          /* 4734 */\n'
           '                    if (cycle_count == 0)\n'
           '                        continue;')
assert source.count(f1_wait) == source.count(tab_wait) == 1
(out / 'f1-only.c').write_bytes(source.replace(tab_wait, old_tab).encode('cp1252'))
(out / 'tab-only.c').write_bytes(source.replace(f1_wait, '').encode('cp1252'))
