# main_menu_callback face-wrap CFG probe (2026-09-24)

## Decision

Closed this local CFG branch. The historical bytes show the `new_rand() % 198 == 1` edge jumping directly to the `face++` and `face == 3` wrap block at function offset `+0x833`. Moving the wrap test outside that edge is not supported by the historical CFG. The experiment created a distinct effective output but did not improve the target residue or strict function count.

## Prediction before compilation

A source-shaped variant that moves `if (face == 3) face = 0;` outside the random increment branch should either converge to the current output (if GCC proves the distinction irrelevant) or create a distinct CFG. It would be useful only if the new CFG aligns with the target's branch and instruction order while preserving exact peers. The recorded original CFG predicts the nested form: the random-success jump enters the increment/wrap block.

## Probe

Both whole-TU probes used the same locked TDM-2 compiler, `game-main`, historical emission order, `--no-prototypes`, and the same canonical source/context. The control overlays the current callback unchanged. The single variant moves only the wrap test after the random branch. No maintained source or recovery ledger was edited.

- Control receipt: `docs/attempts/tu-context/game-main/main-menu-callback-control-20260924.json`
- Variant receipt: `docs/attempts/tu-context/game-main/main-menu-callback-face-wrap-20260924.json`
- Strict compiler comparisons: matching directories under `build/tu-context/game-main/`
- Retained source: `control.c`, `face-wrap-after-rng.c`

## Result

| Outcome | Control | Wrap after random branch |
|---|---:|---:|
| Exact functions | 64/82 | 64/82 |
| Callback candidate size | 2,903 | 2,915 |
| Effective outcome | `05d552d9de0cfc1e` | `b71b8514fc05158b` |
| Branches / calls | 53 / 63 | 54 / 63 |
| Callback differing bytes | 2,627 | 2,664 |
| Unequal relocations | 154/154 | 151/155 |
| Strict status | DIFFER | DIFFER |

The first historical mismatch remains offset `+8` (frame allocation: candidate byte `0x3c`, historical `0x6c`). The edit did not change exact peers, but it worsened callback instruction difference count and introduced a branch absent from the control. No recovery credit.

Original instructions at `+0x833..+0x851` load `face`, increment, compare with 3, conditionally clear the static, and jump to the common continuation. The initial random-remainder branch at `+0x22` targets `+0x833`; this is direct CFG evidence for the nested increment/wrap path. This result changes the next decision: do not pursue unconditional face wrapping as a recovery hypothesis. The callback remains blocked by broad code/data differences, missing historical `LoadCursorA`, `get_rank`, and `get_rank_id` edges in this source context, and unresolved `.rdata` relocation ownership. Continue via those source-backed CFG/presentation/interface and BSS-owner questions, not additional face spellings.
