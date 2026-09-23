# draw_scroller causal probe

## Result

The current focused card remains `DIFFER`, 396/396 bytes, with six changed register-field bytes at offsets 93, 96, 100, 103, 107, and 110. They occur while preparing the first vertical `set_clip_rect` call. The original and candidate have equal function size and instruction count, equal callees and call locations, and all three neighboring functions remain exact.

The historical-order TU probe preserves all three exact neighbors and reports the target at position 2 in both historical and candidate emission order, after exact `restart_scroller`. It produces no target match or neighbor gain/loss. Existing context evidence says omitting `restart_scroller` changes other target bytes but leaves the six mismatch bytes unchanged.

## New isolated batch

`batch-manifest.json` records baseline plus three operand-commutation probes for x/width, y/height, and both in the vertical clipping call. The locked GCC produced one effective output identity for all four probes (`2ba90ce1e634ab85c713f3bf85af404a65804a2b41d52ac668bd8aa2c8a125f6`). All remained 396 bytes with first mismatch 93 and preserved the three exact neighbors. Local operand spelling therefore has no distinct effective output here.

## Stop condition

Current DWARF and declaration evidence agrees with the candidate parameters and local `i`; direct call targets resolve identically. Historical source order and predecessor also agree. No retained historical predecessor, line-table, declaration, or RTL fact distinguishes a new source probe. The old RTL context probe records changes beginning at `expand` when a peer is omitted, but those changes do not reach the mismatch and do not reveal the historical compiler state. Stop source probing until a historical RTL/cgraph trace or validated original CU object with pass context is available. Keep this as a compiler-context issue; no body or layout match is claimed.

## Artifacts

- Current focused card: `docs/current/functions/scroller/draw_scroller.json`
- Strict CU report: `docs/current/reports/game-scroller.json`
- Batch sources and manifest: this directory
- Historical-order TU receipt: `docs/attempts/tu-context/game-scroller/research-20260924-scroller-historical-order.json`
- Prior declaration/context analysis: `docs/attempts/research-luna-scroller-context-20260923/README.md`

No maintained source, ledger, generated state, or exact neighbor was edited.
