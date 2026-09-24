# `draw_frame` continuation checkpoint (2026-09-24)

Scope: isolated historical-order whole-`main.c` check. No maintained source, generated current state, or recovery ledger was changed.

## Fresh pinned control

Ran the locked TDM-2 / GCC 4.4.1 whole-TU probe from current `src/main.c` with historical definition order and no generated prototypes:

`python tools/tu_context_probe.py game-main src/main.c research-20260924-draw-frame-cont-baseline --order historical --no-prototypes --focus draw_frame --focus new_game --focus run_demo --no-dumps`

Receipt: `docs/attempts/tu-context/game-main/research-20260924-draw-frame-cont-baseline.json`.

- Strict functions: 64/82 before and after; no gains or losses.
- `draw_frame`: DIFFER, 8,203/8,518 bytes, historical/candidate emission position 41.
- `new_game` and `run_demo` remain exact.
- Current source SHA-256: `2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044`.

This pins the live requested context and supersedes older 63/82 controls for this checkpoint.

## Bounded hypothesis review

No new compile batch was run. Current original CFG, DWARF, call census, and retained experiments do not specify a new causal source distinction:

- Original disassembly establishes distinct positive/negative speed-reset and cap predecessors, with five direct `custom.frame[0]` height reads. The status-zero sign/threshold path reaches one accepted-path read. The current body has already tested branch-local speed calculations, status-zero spellings, and cap-read ordering; the latter either collapses to the retained 8,203-byte outcome or changes broader topology/call counts.
- Candidate pass dumps carry five height loads through `179r.dse2`; the first saved four-load snapshot is `181r.csa`, where the candidate's duplicated positive status-zero arm is factored into the common accepted path. That is consistent with the original one-read accepted path and does not identify the missing predecessor distinction.
- DWARF establishes `p_im` at the speed-reset and cap sequences, but gives no location covering the status-zero read at `0x409ba7`. Existing line/DWARF rows do not show an arm-specific live value there.
- The current source's evidenced lexical locals/scopes were reviewed; no untested misplaced historical local or type surfaced. Historical direct call edges are fully represented. Source-level extra Allegro calls are inlined under the locked candidate, so they do not establish missing original call behavior.

Predicted result for another cosmetic C spelling of the accepted-path reset/height expression: same `181r.csa` factoring or a topology-changing output, with no basis to expect a new historical residue class. Such a probe would not distinguish explanations and is not justified.

## Decision and blocker

This control changes the peer baseline used for comparison from older retained 63/82 receipts to the current 64/82 state; it does not change the next recovery decision. Keep `draw_frame` research-only at DIFFER and preserve the exact peers.

The next discriminating input must establish an original semantic distinction at the status-zero accepted join (especially `p_im` state around `0x409ba7`), recover source/CFG evidence for how reset predecessors were expressed, or provide a compiler snapshot inside the `179r.dse2`–`181r.csa` boundary. Without one of those, close this local source-spelling branch. No recovery credit is claimed.
