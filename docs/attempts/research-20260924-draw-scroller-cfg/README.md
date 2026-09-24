# `draw_scroller` CFG and argument-liveness research

Isolated research only. The maintained source, current cards, and recovery ledger were not edited.

## Baseline facts

The focused card is `DIFFER`, 396/396 bytes, with six changed register fields at offsets 93, 96, 100, 103, 107, and 110. Original and candidate each decode to 127 instructions and 12 branches; the CU retains the three exact neighbors. The differences are the register assignment while preparing arguments for the first vertical `set_clip_rect`. The stack argument slots, call target, and call offset agree. All direct function relocations match. DWARF reports the same five parameter types and local `i`; no type mismatch is recorded.

Prior evidence under `docs/attempts/research-20260923-scroller-context/` already tests peer omissions, prototype order, and compiler RTL changes. Omitting `restart_scroller` changes other bytes but not the six target mismatch fields. The focused current card prohibits body edits; this lane uses complete body overlays only for diagnostics.

## New hypothesis

Equivalent ordered local assignments may constrain the lifetime/order of the four clip-coordinate values enough to select the historical temporary registers. The batch compares the baseline with three ordered-materialization forms. These are source-shape probes, not candidate fixes.

## Outcome

The baseline plus all three local-materialization variants collapsed to one effective output identity (`2ba90ce1e634ab85c713f3bf85af404a65804a2b41d52ac668bd8aa2c8a125f6`). Each remains 396/396 bytes with first mismatch at offset 93; each CU report retains all three exact neighbors and reports no gains or losses. GCC eliminated the local assignment spelling before it affected the target instructions. The hypothesis is eliminated for these forms; further local-temp variants would be cosmetic retries.

No strict candidate was found. The strict status remains `DIFFER` / `SOURCE_DIFFER` under the workflow's compiler-context routing. Existing evidence still establishes a compiler-context effect from changing `restart_scroller`, but does not identify a historical internal-state cause. The smallest useful missing artifact remains a validated original `scroller.c` object with relocations or a historical compiler RTL/cgraph trace. No source-level CFG mismatch, parameter/type mismatch, call target difference, or data relocation at the six bytes is evidenced.

## Artifacts

- `batch-manifest.json` and four complete body overlays in this directory.
- Receipts and strict CU comparisons are saved by `batch_tu_probe.py` under the matching labels.
