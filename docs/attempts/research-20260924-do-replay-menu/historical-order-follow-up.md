# `do_replay_menu`: historical-order and GCC pass follow-up — 2026-09-24

## Scope

Diagnostic only. No maintained source, generated current state, recovery ledger, or status was changed. Both probes compiled the complete `game-main` translation unit with TDM-2 and `--no-prototypes`, using the retained DWARF-scoped/play-again-exit body at `docs/attempts/research-luna-do-replay-menu/play-again-exit.c`.

## Probe outcomes

| Label | Definition order | Additional context | Exact functions | `new_game` | `run_demo` | `do_replay_menu` |
|---|---|---|---:|---|---|---|
| `drm-historical-order-scoped-exit-20260924` | historical DWARF | none | 63/82; no gains/losses | FUNCTION_MATCH, 1139 B | FUNCTION_MATCH, 159 B | DIFFER, 2643/2661 B, first mismatch +364 |
| `drm-historical-order-rank-predecessor-20260924` | historical DWARF | retained `main_menu_callback-rank-candidate.c` and its declaration/include evidence | 63/82; no gains/losses | FUNCTION_MATCH, 1139 B | FUNCTION_MATCH, 159 B | DIFFER, 2643/2661 B, first mismatch +364 |

The base historical-order target has effective identity `9c5e2914f8b97f6e`, equal to the earlier current-order scoped-exit control. The rank-predecessor historical-order target has identity `2cfea875896db232`, equal to the earlier current-order rank-predecessor result. Thus historical definition ordering adds no new target outcome and does not change the first mismatch. Both `new_game` and `run_demo` remain strict FUNCTION_MATCHes in each full-TU build.

## GCC pass evidence

Saved `main.c.181r.csa` and `main.c.182r.peephole2` dumps for the historical-order base probe and a fresh current-order control. At source line 6262 (the first `fname` fill in the retained overlay), both dumps show the same RTL chain before and after peephole2:

```text
(insn 78 ... (set (reg:SI 2 cx [105]) (const_int 511 [0x1ff])))
(insn 789 ... (set (reg:QI 0 ax [104]) (const_int 32 [0x20])))
```

The second fill at line 6268 has the same count-then-byte chain. Therefore the tested current-versus-historical TU definition order and predecessor context do not cause the first fill's final `ECX`/`AL` order: the retained GCC dump already has count before byte at the earlier `csa` snapshot. The original executable has byte before count only for the first fill and count before byte for the later fill. This localizes the remaining difference to an earlier GCC lowering/order decision or a historical source/compiler-context difference not reproduced by these overlays. The snapshots do not identify which earlier compiler pass or historical source distinction caused it.

No source-level sequencing change is supported by the line/DWARF evidence, and the `memset` spelling variants already collapse. Do not promote either candidate or claim a layout-only match.

## Artifacts

- Full-TU receipts: `docs/attempts/tu-context/game-main/drm-historical-order-scoped-exit-20260924.json` and `docs/attempts/tu-context/game-main/drm-historical-order-rank-predecessor-20260924.json`.
- Full comparisons and dumps: `build/tu-context/game-main/drm-historical-order-scoped-exit-20260924/` and `build/tu-context/game-main/drm-historical-order-rank-predecessor-20260924/`.
- Fresh current-order dump control: `build/tu-context/game-main/drm-current-order-dump-control-20260924/`.
- Outcome grouping: `python tools/effective_outcomes.py game-main do_replay_menu --pattern 'drm-historical-order-*-20260924.json' --compact`.

## Blocker

`do_replay_menu` remains DIFFER. The +364 setup sequence is stable under historical/current definition order and the tested predecessor context; the available TDM-2 `csa` and `peephole2` snapshots both already order the two constants count-first. Further progress needs historical compiler lowering evidence or a distinct, independently supported source-context difference upstream of that snapshot. Another equivalent `memset` spelling or definition-order replay is not informative.
