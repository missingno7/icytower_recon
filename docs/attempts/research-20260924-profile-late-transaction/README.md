# Late typed profile TU transaction

The generated `Tavailable_profile` header must become visible after
`profile_data_page_advanced`: the locked early-header control changes that
previously exact function, while the late-header control preserves it. The
historical DWARF type has one `handle[32]` member at offset zero. The old
`char *` selector declarations and `char **` rebuild declaration erased this
interface. The retained selector bodies use the typed member paths and restore
the observed switch, prompt drawing, post-loop notice, nonoverlapping lexical
buffers, and second `is_any(ctrl)` call.

`tools/tu_context_probe.py` now supports an explicit `late_declarations` block
after an unchanged definition, and `tools/tu_context_task.py` admits it only
when the anchor is a baseline `FUNCTION_MATCH`. The header must be an existing
generated `recovered/*.h`; inserted declarations must be prototypes; the
transaction rejects a diagnostic `research_base`. The source and header
identities, complete retained bodies, unchanged definitions, prior exact
functions, proven data owners, new implicit declarations, ordinary link and
acceptance tests are checked by the existing strict path.

The diagnostic `profile-late-typed-rebuild-diag-20260924` compiled under locked
GCC 4.4.1 and kept all 11/17 exact profile functions, including
`profile_data_page_advanced`. Both selectors remained `DIFFER`:
`draw_profile_selector` 1250/1268 and `select_profile` 3115/3070 bytes. The
production transaction `profile_late_typed_selectors_20260924` passed `check`
with no losses and passed `promote` with all 156 function acceptance tests and
ordinary diagnostic link. A subsequent fresh 25-CU verification retained the
same 11 exact profile functions and regenerated three `AGREE` interface cards:
`draw_profile_selector`, `select_profile`, and `rebuild_profile_list`. No
OBJECT_MATCH, CU_MATCH, or selector function match is claimed.

Inputs: `transaction.json`, `declarations.json`, `late-declarations.json`,
`draw_profile_selector.c`, and the retained
`../research-20260924-select-profile-ctrl-lifetime/any_gated_wait.body.c`.
Strict receipts are in `../tu-context/game-profile/` and
`../tu-context/transactions/`; full comparisons are in
`../../../build/tu-context/game-profile/` and
`../../../build/acceptance/game-profile/`.
