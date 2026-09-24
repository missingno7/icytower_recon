# `draw_frame` historical-order context audit (2026-09-24)

Scope: inspect the maintained `src/main.c` body, latest generated `draw_frame` card, original executable instructions, and retained takeover trials. No source, current generated state, or recovery ledger was changed.

## One unresolved original CFG block

The current body merges the status-zero / `p_im == 1` reset route at `p_im_one_path` (`src/main.c:3236-3275`): one open-band test resets `frame`, the frame-cap test follows, then one `p_im = 1` assignment and one common frame-zero load.

The original machine code has three separate entries into the same visual state:

- At function offsets 1917-1952, the positive speed predecessor resets `ply->frame`, computes `1 - custom.frame[0]->h` (load at 1924), writes `1` to the live `p_im` register at 1952, and jumps into later sprite selection.
- At offsets 3384-3406, the negative speed predecessor has its own frame reset, height computation (load at 3391), and `p_im = 1` write at 3406.
- At offsets 6030-6066, `jle` skips the frame overflow reset and lands at 6051, where the third frame-zero height computation occurs; both legs reach the later `p_im = 1` write at 6066. This disproves a model that puts the frame-zero calculation only inside the overflow-reset branch.

The status-zero near-still shortcut is a fourth predecessor: offsets 2256-2329 reset the frame and load `custom.frame[0]` at 2315 before entering the edge-sprite block. The distinct predecessors and load sites are directly visible in the original disassembly; line-table/DWARF evidence ties these blocks to `main.c` lines 2590-2606 and the live `p_im`, `oy`, and `customFrame` values. The behavior is consistent with the retained body, but its common C join does not reproduce this physical CFG.

This is a control-flow topology discrepancy, not evidence for an extra visible operation. The repeated frame resets, base-height calculation, and `p_im = 1` assignments have the same values. The historical source statements that created those separate entries are not established. The obvious branch-local rewrites are already frozen as `takeover-draw-signed-speed-trial-20260923` and `takeover-draw-frame-cap-skip-trial-20260923`; both remained `DIFFER` and still produced four candidate frame-zero height loads where the original has five. Further duplicated C statements would be an unsupported source-shape guess, so no new variant was compiled.

## Fresh whole-TU baseline receipt

Ran `python tools/tu_context_probe.py game-main src/main.c research-drawframe-current-historical-audit-noproto-20260924 --order historical --no-prototypes --focus draw_frame --focus new_game --focus run_demo --no-dumps`.

Receipt: `docs/attempts/tu-context/game-main/research-drawframe-current-historical-audit-noproto-20260924.json`; strict function comparison: `build/tu-context/game-main/research-drawframe-current-historical-audit-noproto-20260924/comparison.json`.

- Outcome: `draw_frame` remains `DIFFER`, 8,203 / 8,518 bytes.
- Exact peers: 63 `FUNCTION_MATCH` before and after; no gains or losses. `new_game` and `run_demo` remain `FUNCTION_MATCH`.
- Historical predecessor positions: 79/82 before and after; `draw_frame` remains at position 41.
- This is a whole-TU diagnostic receipt, not an acceptance or object/CU match claim.

## Blocker

The original CFG proves separate speed-reset and fallback predecessors, but all retained source trials collapse them or fail to reproduce the extra frame-zero load. Without historical source or a new semantic distinction among those predecessor calculations, there is no evidence-backed C body edit to test. Keep `draw_frame` research-only at `DIFFER`; the current mismatch classification `STACK_FRAME_LAYOUT` records the first observed mismatch and does not establish a layout-only match.
