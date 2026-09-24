# `fldads_threadmain` historical-order retest (2026-09-24)

## Question and prediction

The focused card places the only unresolved raw mismatch at function offset
+46, where `fldads_threadmain` loads the address of `"Downloading ad listing"`.
Candidate and historical literal contents agree; the owning `.rdata` placement
is unresolved. Function size is 223 bytes on both sides, branch count and
direct callee sets agree. The current TU places `fldads_start` before
`fldads_get_random_ad` and `fldads_threadmain`; historical DWARF order places
`fldads_get_random_ad`, `fldads_threadmain`, then `fldads_start`.

Prediction before compiling: if function definition order controls the literal
placement, replaying the DWARF definition order should remove the +46 operand
mismatch and produce a strict `FUNCTION_MATCH` for the target. The acceptance
condition for continuing this branch was preservation of the current 11 exact
peers; an order that repairs the target but loses exact peers would be
diagnostic only and should end the branch.

## Probe

Replayed the source-backed historical definition order on the current maintained
source with the locked whole-TU context probe:

```powershell
python tools/tu_context_probe.py game-fld-adspot src/fld_adspot.c research-20260924-threadmain-order-typed --order historical --focus fldads_threadmain --no-dumps
```

Source: 6,985 bytes, SHA-256
`9116d56f22599dfa2e7eb197a067039f693b858948946530f2dd225cbb1f5016`.
The prior historical-order transaction in
`docs/attempts/interfaces/order_fld_adspot.jsonl` used a different source
identity (6,930 bytes, SHA-256
`dd2093d4e922a9b8b871f6c5a9c3f82587fbfb442ef7babcfb89f46e51bf0ae6`) and
failed after losing `fldads_load_cache_from_csv`; this retest includes the
current inline historical `HTTPResponse` types.

## Strict result and decision

The focused comparison now reports `fldads_threadmain` as an exact 223-byte
`FUNCTION_MATCH`, so the +46 literal relocation residue disappears under the
historical order. However, total exact functions fell from 11/12 to 8/12.
Four exact peers regressed: `fldads_dump_local_cache`,
`fldads_get_local_filename_from_url`, `fldads_get_random_ad`, and
`fldads_update_local_adimg`. `fldads_get_random_ad` became
`CODEGEN_SIMILAR`; the other three became `DIFFER`. Whole text contribution
equality remains false.

The result confirms a TU-order dependency for the target's emitted bytes, but
the complete historical order is not a viable recovery decision because it
does not preserve the exact peers. Stop this branch here; no narrower order
variant is justified by this result, and the diagnostic target match earns no
production recovery credit.

Receipts:

- Probe summary: `docs/attempts/tu-context/game-fld-adspot/research-20260924-threadmain-order-typed.json`
- Strict whole-CU comparison: `build/tu-context/game-fld-adspot/research-20260924-threadmain-order-typed/comparison.json`
- Current strict baseline: `build/experiments/tdm-2/game-fld-adspot/O2/comparison.json`
- Prior aggregate/type context study: `docs/attempts/research-20260924-httpresponse-type/README.md`

Compiled object SHA-256:
`c86b33a50164d7a6338ee3c0695ec01545ca1c6cecc803c3a86610d48f37ce66`.
No maintained source, generated current state, or recovery ledger was changed.
