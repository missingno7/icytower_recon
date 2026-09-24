# handle_menu entry liveness discriminator

Date: 2026-09-24. Isolated `game-menu` whole-TU experiment, locked TDM-GCC 4.4.1 (`-O2`, i386, x87); no maintained source or ledger edits.

## Evidence and prediction (recorded before compile)

Focused card and the prior IRA/DWARF comparison show first mismatch at +13: historical entry loads `mp` into EDI; candidate loads `ctrl` into ESI and `bmp` into EDI. Historical DWARF keeps `mp` in EDI for most of the first 593 bytes and puts `ctrl` briefly in EAX, then at EBP-16. Current IRA spills entry `mp` allocno `r95`, while assigning `ctrl` `r96` to ESI and `bmp` `r97` to EDI. The current source first reads `mp->pos` as an argument to `reset_menu`.

One source-backed, semantics-preserving discriminator: evaluate `mp->pos` into a short-lived local immediately before `reset_menu`, then pass that value. C already evaluates argument values before entering the callee, so this preserves the call's input even if `reset_menu` mutates `mp`. It isolates whether making the first pointee read an explicit scalar SSA value changes GCC's entry load/allocno placement. Prediction: if the distinction matters before IRA, the first entry load or IRA live-range/cost for `r95` changes; if output and effective function bytes remain unchanged, this source shape is canonicalized and the local liveness explanation is not supported. In either case, peer exactness must remain 7/10 with no losses.

## Outcome

The fresh current-order, no-prototype control and the materialized-position variant both compiled under TDM-2. Both are `DIFFER`, 1066/1120, first mismatch +13, and retain 7/10 exact functions with no peer gains or losses. `effective_outcomes.py` grouped both labels under one effective `handle_menu` identity (`1806630c6a86af27...`): 995 differing offsets, 35 unequal relocation sites, frame `0x14c`, 46 conditional branches, 22 calls. The body spelling is therefore eliminated for this current whole-TU context; it does not alter the next recovery decision.

The available candidate pass trace establishes the current compiler-side boundary: the first mp read is lowered from argument memory in early RTL, and at IRA (`.172r.ira`) GCC spills entry allocno `r95`; it assigns `ctrl` `r96` to ESI and `bmp` `r97` to EDI. Postreload `.174r.postreload` shows the resulting argument loads. Historical DWARF reports `mp` in EDI over the long function range and `ctrl` briefly in EAX, but there is no historical RTL/IRA trace. We cannot attribute the original allocator choice to a specific GCC pass or infer its interference/cost graph from DWARF alone.

## Artifacts

- `materialized-position.c`, SHA-256 `10a223a9feef1269dceb60ddbf17b544c9852b3901bb4f8bb5cc96e044b48f4c`
- Control receipt: `docs/attempts/tu-context/game-menu/liveness-control.json`; source `src/menu.c` SHA-256 `4cdb39a001e2413b206a702941af52c40616e490960bac25da8513e9558cf044`.
- Variant receipt: `docs/attempts/tu-context/game-menu/liveness-materialized-position.json`; compiled object SHA-256 `4c9af2dca8430f34693e5662ef4dcb57e9cf0e8593e0a19baaf24fb8d8fbe3a7`.
- Effective response command: `python tools/effective_outcomes.py game-menu handle_menu --pattern 'liveness-*.json' --response --baseline liveness-control`.
- Candidate IRA/postreload traces: `build/compiler-evidence/game-menu/handle_menu/baseline/focus/probe.c.172r.ira` and `.174r.postreload` (hashes in `entry-live-ranges.json`).
