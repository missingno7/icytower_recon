# Recovery continuation, 2026-09-24

Production result: the locked `TU_CONTEXT` transaction
`replay_load_draw_historical_20260924` made `load_replay` a strict
`FUNCTION_MATCH` (1136/1136 bytes, 39/39 relocations). The replay CU rose from
6/15 to 7/15 exact functions without losing an exact neighbor. A fresh 25-CU
verification and `tools/audit.py` passed. Overall exact functions rose from 209
to 210, matched game-function bytes from 35,299 to 36,435. The accepted draw
source follows observed selected-row call order and DWARF buffer scopes, but
`draw_replay_selector` remains `DIFFER`; the TU and executable do not match.

The decisive mechanism was whole-TU context: typing `load_replay`'s `pf` local
as historical `PACKFILE *` was insufficient under the maintained draw body.
Restoring the observed selected-row draw path alongside it made load strict.
The transaction and negative variants are archived in
`research-20260924-draw-selector-residual/` and
`research-20260924-load-replay-min-context/`.

A second accepted TU transaction, `profile_late_typed_selectors_20260924`,
restored the historical typed profile selector interfaces and the source-backed
switch/UI/control path while preserving all 11 exact profile functions. The
generated `draw_profile_selector`, `select_profile`, and
`rebuild_profile_list` interface cards now report `AGREE`. Both selector
bodies remain `DIFFER`; the transaction adds no exact function or byte credit.
Its late generated-header placement follows the locked GCC witness experiment
and is handled by the bounded `late_declarations` TU gate.

Other information-bearing results, with no recovery credit:

| Function/front | New evidence | Remaining blocker |
| --- | --- | --- |
| `select_profile` | The omitted second `is_any(ctrl)` call makes the entry `ctrl` capture into ESI match through +63; two C forms collapse. | At +64, `bgbmp` uses the wrong scalar stack slot despite matching frame size and DWARF buffer scopes. See `research-20260924-select-profile-ctrl-lifetime/`. |
| `create_replay` | Uppercase historical header owner preserves source identity but shifts `.rdata` relocation targets in unchanged exact neighbors; current/top/historical order collapse. | Literal/data placement, not a safe property-body repair. See `research-20260924-create-replay-context/`. |
| `replay_selector` | Removing a nonexistent explicit padding member changes bare output at GCC VRP2; typed-load/draw context collapses the difference. Dump flags leave `.text` unchanged. | Causal VRP input and historical aggregate migration gate remain unresolved. See `research-replay-padding-causality-20260924/`. |
| `do_replay_menu` | Original save path fills `pname` with 511 spaces and terminates `fname`/`comment` at index zero. | Combined historical-order source is still DIFFER; see `research-20260924-do-replay-menu-save-init/`. |
| `play` / `draw_frame` | A path-local collision guard gives a distinct play output while GCC reuses a bounds-load; the draw cap height read is a distinct original CFG route. | No strict large-function result; see `research-20260924-play-collision-predecessors/` and `research-20260923-draw-next/`. |
| `calc_replay_checksum` / `extractHTTPResponse` | Candidate hard-register/stack-home choices first become concrete at IRA; a tested source form did not alter them. | Historical RTL is unavailable, so allocator cause remains unproven. See `research-20260924-checksum-rtl-cause/` and `research-20260924-httpget-output-index/`. |
| `load_character_bmp` | A byte-neutral GCC BBRO trace puts the candidate cold fopen-error block at the tail, while original CFG places it before the datafile parser. | The historical source or pre-BBRO trace needed to explain block placement is missing. See `research-20260924-load-character-bbro/`. |
| `add_floor` / `draw_scroller` | Locked TU controls preserve all exact peers; their first differences are register choices at +297 and six call-argument bytes at +93 respectively. | Historical allocation cause remains unknown; definition/predecessor order and tested operand commuting do not explain it. See `research-20260924-add-floor/` and `research-20260924-scroller-context-causal/`. |

All unresolved outcomes above remain research evidence. No original-code
fallback, byte patch, layout padding, relaxed relocation check, or manual
recovery-status edit was used.
