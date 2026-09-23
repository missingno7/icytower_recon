# Historical-order `init_game` context check for `load_character`

Isolated whole-TU research only. Maintained sources, generated current state,
and `src/recovery.json` were not changed. The probes used locked TDM GCC 4.4.1,
the retained historical definition order, and `--no-prototypes`.

## Candidate and checkpoint

The candidate follows `docs/attempts/game-main/historical-order-spec.json`:
retained `play-merged.c` and `draw_frame-merged.c` bodies, with historical
definition order. The prior takeover checkpoint is
`docs/attempts/research-luna-init-game-context/README.md` and its `status.json`.
That checkpoint found the production-equivalent 63/82 baseline and identified
the immediate `init_game` predecessor plus the peephole2 scratch cursor as a
testable context hypothesis. It also found that the current and earlier
`init_game` bodies converge to one `load_character` output.

## Probe outcomes

| Label | Context | `load_character` result | Exact functions |
| --- | --- | --- | ---: |
| `research-historical-order-load-character-baseline-20260923` | Historical order plus retained `play` and `draw_frame` bodies | DIFFER, 330 B / 92 instructions, first mismatch +13 | 63/82 |
| `research-historical-order-load-character-init-snapshot-20260923` | Same context plus retained earlier full `init_game` candidate | DIFFER, 330 B / 92 instructions, same mismatch bytes | 63/82 |

Both reports retain the same target difference offsets: `+13, +16, +24, +41,
+53, +59, +67, +138, +178, +185, +202, +206, +248, +254, +258`. All 18
target relocations and its `log2file` direct target resolve equally. The
`effective_outcomes.py` identity for the two probes is the same as the prior
context baseline: `f896246c764546d6`.

The emitted order is unchanged across both probes and the production-equivalent
`luna-init-context-baseline-final-20260923` receipt: `init_game` at position
72 and `load_character` at 73. The extracted peephole2 scratch-find sequence
is also unchanged: `init_game` finds `si, di, ax, dx, cx, bx`; `load_character`
finds `di, ax`. Comparing the full extracted per-function scratch lists shows
no sequence changes in any emitted function across these contexts. The
previously noted target relocation-displacement changes remain same-CU layout
effects, not effective target instructions.

This rules out the tested historical-order candidate bodies and the retained
earlier `init_game` snapshot as sufficient causes for the register permutation.
The dumps expose scratch finds but not GCC's persistent internal
`search_ofs` value at the entry and exit of each function, so unchanged scratch
lists cannot prove that no hidden cursor state changed. No historically
grounded exact `init_game` body or state trace is available to discriminate that
remaining possibility. Further source spelling or artificial call controls
would add no historical evidence, so this probe set stops here.

Both comparisons retain 82 function records, 13 object sections, 428 COFF
symbols, 93 common allocations, and initialized `.data` / `.rdata` sections
of 6,664 / 6,648 bytes. The baseline inventories 4,424 relocations; the
retained `init_game` snapshot inventories 4,428. These remain diagnostic
inventories; the CU and object are not claimed as matches.

## Artifacts

- Probe receipts: `docs/attempts/tu-context/game-main/research-historical-order-load-character-*.json`.
- Full object comparisons, GCC cgraph and peephole2 dumps, and overlays:
  `build/tu-context/game-main/research-historical-order-load-character-*/`.
- Retained input bodies: `docs/attempts/game-main/play-merged.c`,
  `docs/attempts/game-main/draw_frame-merged.c`, and
  `docs/attempts/game-main/bodies/init_game.c`.
- Prior init context checkpoint: `docs/attempts/research-luna-init-game-context/`.
