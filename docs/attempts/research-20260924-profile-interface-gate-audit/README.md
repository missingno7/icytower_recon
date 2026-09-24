# Profile selector interface gate audit

## Result

No current strict production gate can stage the source-backed late `Tavailable_profile` header plus the typed selector signatures/member expressions and candidate selector bodies as one transaction.

`interface_task.py` consumes one receipt-derived interface card, allows only generated declaration edits, and explicitly disallows body edits. The current cards for `draw_profile_selector`, `select_profile`, and `rebuild_profile_list` are `TYPE_LAYOUT_BLOCKED` / `SUPERVISOR`: candidate `char` views make the named candidate layout unavailable. The typed declaration/body experiment therefore cannot enter this gate.

`tu_context_task.py` accepts retained complete bodies and validates a freshly compiled whole CU, but `tu_context_probe.layout()` puts the non-function skeleton and generated prototypes before all function definitions. Its structured declaration edits cannot insert a header/prototype block between `profile_data_page_advanced` and later definitions. That position is required: an early header include changes `profile_data_page_advanced`; the late-header full-TU probe preserves all 11 baseline exact functions. The current retained typed selector candidate still has both selectors `DIFFER`.

`tu_context_probe.py` has a diagnostic `--research-base` path. It is documented as diagnostic-only, but `tu_context_task.plan()` calls the same builder and does not explicitly reject `research_base`. Do not use that as a production promotion route. A promotion-capable extension must reject arbitrary research bases and derive the planned edit from structured, receipt-bound inputs.

The rebuild follow-up independently shows that moving `rebuild_profile_list`'s caller declaration after the late include and spelling it `Tavailable_profile **` emits the expected aux declaration without changing code. It is a separate declaration repair from recovering either selector body.

## Smallest safe extension

Extend the existing TU-context transaction with one narrow interleaved declaration block, anchored to the unchanged `profile_data_page_advanced` definition. The block should be limited to the generated `Tavailable_profile.h` include and explicitly enumerated typed prototypes/declarations. Permit only explicit retained body files for `draw_profile_selector` and `select_profile` (plus any separately authorized caller body); keep every other definition byte-identical. Bind the anchor, header identity, declarations, body identities, source identity, and expected historical signatures in the plan and revalidate them at begin, apply, check, and promote. Production planning must reject `research_base`.

This extends the existing whole-CU acceptance boundary; it does not confer a selector function match. Keep the ordinary source-order and compiler inputs unchanged.

## Acceptance predicate

A fresh locked `game-profile` CU verification is acceptable only if all of these hold:

- Each of the baseline 11 exact functions remains `FUNCTION_MATCH`, including `profile_data_page_advanced`; there are no lost exact functions. The report still contains all 17 CU functions and reports initialized data, common/BSS ownership, and every relocation.
- Only explicitly named retained selector definitions differ from the baseline source islands. Every other definition is byte-identical. The late block is exactly at the anchor and all its declarations normalize to the historical DWARF signatures.
- No prior data owner, common allocation, initialized contribution, or relocation proof regresses; no new implicit declaration appears; ordinary link and existing acceptance checks pass.
- Selector function statuses remain the strict oracle's result. No `OBJECT_MATCH` or `CU_MATCH` claim is inferred from the exact-function set.

## Evidence

- `../research-luna-profile-interface/typed-late-header-summary.json`: late typed header and selector interfaces preserve 11/17 exact functions, including `profile_data_page_advanced`; both selectors remain `DIFFER`.
- `../research-luna-profile-interface/README.md`: early header inclusion loses the advanced witness; moving the include after it restores the exact set.
- `../research-luna-rebuild-profile-interface/result.json`: late typed `rebuild_profile_list` caller declaration emits no code change and preserves the same 11 exact functions.
- `../research-20260924-select-profile-ctrl-lifetime/results.json`: selector-local lifetime/CFG probes preserve the same exact neighbors; `select_profile` remains `DIFFER`.
