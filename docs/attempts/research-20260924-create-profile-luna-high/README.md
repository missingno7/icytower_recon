# `create_profile` canonical type spelling probe — 2026-09-24

Scope: isolated full-`game-profile` body overlays from the current `src/profile.c`, after the accepted `view_profile` context. No maintained source, current card, queue, or recovery ledger changed.

## Evidence and question

The focused current card is 823/823 bytes, `DIFFER`, with two differing bytes at offsets 69–70. At offset 68 the original reloads parameter `overwrite` from `[ebp+12]` into ESI, while the candidate reloads it into EDI; the next `test` uses the same respective register. Call order and relocation comparisons agree. Original DWARF records return/local pointer type `Tprofile *`; source spells these `Tprofile_create *`, defined in `src/profile.c` as `typedef Tprofile Tprofile_create`. The historical local declarations are function scope and in source order `file, p, i, now, my_time, year, month, day`; current source already follows that order.

Since the canonical type spelling is directly supported by the historical DIEs, a four-body batch tested a control, canonical local pointer only, canonical `sizeof` only, and canonical return/local/`sizeof` together.

## Result

All four full-TU probes collapse to effective identity `e9b312015907a283e73b3d8ad6448ff105e0aebd1ca229c0e1949769bfa8714c`. Each remains 823 bytes with the same two-byte EDI-versus-ESI mismatch at +69. The current TU retains all 11 exact peers, with no gains or losses. The type alias spelling is eliminated as a code-generation cause.

Prior retained research already tests four guard forms, local declaration order/grouping, current versus historical TU order, and an IRA dump-control compilation. Those batches also collapse to the same output. The candidate IRA shows `overwrite` entering the comparison directly from `[ebp+12]`; the register choice occurs during reload/code emission. Historical source evidence establishes no local alias or nested scope that could explain a different reload target.

## Disposition and artifacts

No strict candidate or source-backed next discriminator remains in this lane. Keep `create_profile` at `DIFFER`. A historical GCC IRA/reload dump or original profile object with build/pass context is required to distinguish the historical ESI selection from the current EDI choice.

- Body overlays and manifest: this directory (`type-batch.json`)
- Receipts: `docs/attempts/tu-context/game-profile/create-profile-type-luna-high-20260924-*.json`
- Full comparisons/objects: matching labels under `build/tu-context/game-profile/`
- Prior guard/declaration/order/IRA evidence: `docs/attempts/research-20260924-create-profile-batch/README.md`
