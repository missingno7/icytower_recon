# `fldads_threadmain` context probes (2026-09-23)

Research only. No maintained source, generated current state, `src/recovery.json`, accepted body, or external repository was changed. Source overlays and full comparison reports are in this directory; object builds are under ignored `build/tu-context/game-fld-adspot/`.

## Current strict status and blockers

The current `fldads_threadmain` card remains `DIFFER` / `CODEGEN_SIMILAR`, 223 bytes vs 223, with 7 differing bytes beginning at `+46`. The function's own ABI is agreed (`void *(void *)`), and the `log2file` prototype is present in the current source. No missing direct call was found. The retained compound trial shows that adding the full `log2file(const char *, ...)` prototype to its older input changes 204-byte output to the current 223-byte code shape, but still does not establish literal target ownership.

The current disassembly aligns instruction shape through the function. Strict comparison is blocked by five `.rdata` literal references, whose contents match but resolved owner/placement remains unproven. Four target strings are at candidate `.rdata` offsets `0xbf`, `0xd8`, `0x100`, and `0x164`; `"Cached ads are up to date"` is at `0x185`. Their historical addresses put the cached string before the four download/log strings. The card classifies these references as `CONTENT_EQUAL_OWNER_UNPROVEN`; the body is therefore not editable. The `HTTPResponse` partial type-view task also records an `iNumHeaders` signedness conflict, but this function only reads `iStatusCode`, `pPayload`, and `iPayloadSize`; it is not the observed code-shape blocker.

## Strict target candidate found in isolated TU-order overlays

A full historical function-order overlay yields `FUNCTION_MATCH` for `fldads_threadmain` (223/223; 15 relocations and 3 direct transfers checked) but drops four previously exact neighbors, leaving 8/12 strict functions. The already-retained `docs/attempts/tu-context/game-fld-adspot/hist-order.json` records the losses.

I then tested smaller, body-identical definition-order changes with current source and no generated prototype block:

- Moving only `fldads_update_local_adimg` before `fldads_load_cache_from_csv` yields `FUNCTION_MATCH` for `fldads_threadmain`; all other functions retain baseline status except `fldads_get_random_ad`, which falls from `FUNCTION_MATCH` to `CODEGEN_SIMILAR`. The CU stays at 11/12 strict functions.
- Moving only `fldads_dump_local_cache` after `fldads_load_local_cache` yields the same target result and same single neighbor regression.
- Moving only `fldads_start` and `fldads_get_random_ad` to the front leaves the target `CODEGEN_SIMILAR` and all baseline matches intact.
- Combining either successful target movement with the front move does not restore `fldads_get_random_ad`.

The strict `fldads_threadmain` function bytes and resolved-target identity are identical across the four successful target overlays (`effective-outcome-hashes.json`, SHA-256 `05965bfec6ce05f7143ac7fd85ffe130fc94197c0f50ba5221c404c0c8c76e87`). They are candidate evidence only: each changes source definition order, each sacrifices `fldads_get_random_ad`, and every whole-object/CU comparison remains false. Do not promote this as a single-function task or alter the protected neighbor.

## Stop point

There is no CFG or target-call-interface mismatch left in the focused function. The remaining strict blocker is literal ownership and CU `.rdata` placement, while TU-order changes can make those five targets resolve exactly only alongside a compiler-context regression in `fldads_get_random_ad`. The two single-move overlays converge to the same effective target output; extra equivalent reordering is unlikely to add information. Resolving the supervisor-level TU transaction requires a context change that preserves both functions, or independent ownership evidence for the literal mapping.

## Artifacts

- `historical-order-current-summary.json`, source and full compare: exact target with four neighbor losses.
- `start-random-first-summary.json`, source and full compare: no target gain, neighbors preserved.
- `historical-string-peer-order-summary.json`: exact target, two additional peer losses.
- `adaptive-order-batch-summary.json`: the two single-move experiments.
- `context-combination-summary.json`: combinations with the start/random front move.
- `effective-outcome-hashes.json`: effective-output dedup for target and `fldads_get_random_ad`.
- Probe scripts: `probe_historical_order.py`, `probe_minimal_order.py`, `probe_string_peer_order.py`, `probe_order_components.py`, `probe_context_combinations.py`, `effective_hashes.py`.

## `fldads_get_random_ad` context investigation

The exact-neighbor regression is a section-relative relocation change, not a changed instruction sequence. The current-order control has `fldads_get_random_ad` at 192/192 with relocation addend `.rdata+416` (`0x1a0`), independently resolved to the historical target. In the two isolated source-order branches that make `fldads_threadmain` exact, the same relocation becomes `.rdata+412` (`0x19c`), and target ownership is no longer established. The only differing bytes are the three-byte immediate at function offsets 82–84. The little-endian float constant `00 fe ff 46` moves from `.rdata+0x1a0` to `.rdata+0x19c`; string pool packing ahead of it changes by four bytes.

The best paired context comparison is current order versus the single `fldads_update_local_adimg` movement. After normalizing temporary overlay paths and GCC tree pointer IDs, both `fldads_get_random_ad` and `fldads_threadmain` have identical `.181r.csa` and `.182r.peephole2` dumps between those branches. Thus peephole2 scratch history and a changed CFG are not responsible for this specific get-random regression; the function RTL stays the same and the strict result diverges at final section-relative constant placement. The dump-only and full-historical branches do alter normalized RTL/debug identities more broadly, but still produce the same observed relocation shift.

The small combination batch (front-move of `fldads_start`/`fldads_get_random_ad` combined with either useful target move) did not restore the pair: all branches that make `fldads_threadmain` exact leave `fldads_get_random_ad` at `CODEGEN_SIMILAR`. The front-random branch retains `fldads_get_random_ad` exact but leaves `fldads_threadmain` different. Effective-output dedup is in `effective-outcome-hashes.json`; target outputs from successful target branches converge, and the get-random relocation outcomes split into the two addends above.

`-fno-toplevel-reorder` is active for this compile, so object function order follows the overlay source order. The cgraph postorder helper is not the object emission order here. The concrete remaining blocker is a CU-level constant/string pool ownership and placement context that can satisfy both functions together; no strict paired candidate was found. Full evidence is in `fldads-get-random-ad-context-mechanism.json`.

## Historical literal order and branch-layout probes

The historical `function_lines.py` map places the cached-log call at source line 225 / function offsets 169–184 and the download-log call at line 231 / offsets 43–55. In the original image, the cached string begins at `.rdata` VA `0x4d43af`, before “Downloading ad listing” at `0x4d43c9`; the download URL, error string, and final summary follow at `0x4d43e0`, `0x4d4408`, and `0x4d446c`. This supports a historical cached-first source branch despite the download path being earlier in emitted `.text`. It does not specify the exact original C syntax.

Three semantics-preserving current-definition-order overlays tested the evidence-supported source idea: inverted cache-first if/else, separate cache/download guards, and a cache guard with an explicit jump to a download label. All keep `fldads_get_random_ad` at `FUNCTION_MATCH` with its current `.rdata+0x1a0` target, but all leave candidate `.rdata` at 420 bytes and preserve the current literal sequence: download at `0xbf`, URL at `0xd8`, error at `0x100`, summary at `0x164`, cached at `0x185`, float at `0x1a0`. None makes `fldads_threadmain` strict. The inverted and goto forms converge to the same 204-byte body; separate guards retain a 223-byte body but preserve the baseline seven literal relocation mismatches. Output hashes and all source overlays are in `branch-literal-order/branch-arrangement-outcomes.json` and sibling files.

The earlier source-definition-order branches that make `fldads_threadmain` exact still emit cached after download strings and reduce `.rdata` to 416 bytes; that four-byte shift moves `fldads_get_random_ad`'s relocation to `+0x19c`, losing independent target resolution. The original float bytes `00 fe ff 46` occur six times in the executable, so content alone cannot bind the shifted relocation. This stops the source/CFG hypothesis: historical line evidence supports cached-first lexical order, but these bounded semantic forms are canonicalized to the same candidate literal pool or damage function code shape. A supported way to preserve both strict functions remains unestablished.
