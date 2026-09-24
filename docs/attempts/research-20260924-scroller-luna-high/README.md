# `draw_scroller` independent context audit — 2026-09-24

Scope: isolated full-CU `game-scroller` overlays only. No maintained source, current cards, queue, or recovery ledger was changed.

## Current evidence

`draw_scroller` is 396 bytes in both original and candidate, with 127 instructions and six changed register fields at offsets 93, 96, 100, 103, 107, and 110. The first mismatch is the first vertical `set_clip_rect` argument setup: original uses ECX/EAX/EDX for `y`/`x`/`bmp`; candidate uses EAX/EDX/ECX. Stack argument slots, call target, calls, and CFG agree. The only DWARF local is `i`; parameter types and `Tscroller` layout agree. All three peer functions match, and the target is the historical emission frontier after exact `restart_scroller`.

## Overlay outcome and deduplication

Two full-TU overlays were run for historical and current definition order. Both compile; each retains 3/3 `FUNCTION_MATCH` peers with no gains/losses. Both produce the same resolved instruction-byte digest, `c1e600bd2b3046c5882b48e4518977297b01172ea34c98d411f34499f9859b13`, and the same six offsets. The output also collapses exactly to the earlier baseline, historical-order, and CFG-baseline overlays. This order hypothesis is eliminated.

Receipts: `docs/attempts/tu-context/game-scroller/scroller-draw-order-current-20260924.json` and `scroller-draw-order-historical-20260924.json`. Comparisons and overlays: matching directories under `build/tu-context/game-scroller/`.

## Disposition

Prior isolated research already tested peer omissions, prototype order, schedule/unit-at-a-time flags, local materialization, and operand commutation. Current/historical order adds no new output. No source-level CFG/type/relocation discrepancy is evidenced, and `body_edit_allowed` remains false because this is routed as a compiler-context issue. The historical register allocation cannot be explained from available source, DWARF, or candidate RTL; a validated original `scroller.c` object with relocations plus compiler pass/cgraph context, or historical GCC RTL/cgraph dumps, is needed for a discriminating next step. Keep status `DIFFER` and avoid further register-spelling or local-temp variants.
