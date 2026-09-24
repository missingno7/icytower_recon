# extractHTTPResponse bounded follow-up disposition (2026-09-24)

## Decision

No new source probe was compiled. The current evidence does not support a discriminating source hypothesis outside already tested families. The branch is locally converged at the source-tree and declaration/lifetime levels; a fresh compile of another cosmetic form would not add information. Keep the function `DIFFER` and preserve the current exact CU peers.

## Pinned state

- Target: `game-httpget / extractHTTPResponse`; current strict card is `docs/current/function-evidence/httpget/extractHTTPResponse.json`.
- Current source: `src/httpget.c`, SHA-256 `410d68918baff159faa2c35215724353af937fe62574129746c3082f0ac04999`.
- Current body hash: `2242f69c2acb5256f827d611245e43968fbf7327e8139271f1dd591736edd188` (also recorded as attempt 12).
- Strict result: 924 candidate bytes vs 923 historical; first mismatch +14. Historical regparm argument stores are EAX -> EBP-0x834 and EDX -> EBP-0x82c; current stores are EAX -> EBP-0x838 and EDX -> EBP-0x834. Both allocate 0x84c. Current best control preserves 9/10 exact functions in this CU.
- Current whole-TU context and candidate GCC dumps: `docs/attempts/research-20260924-http-extract-context/`.

## Tested families ruled out

- First-reader pointer/index forms, index locals, capacity forms, declaration order, and exit-store placement: `docs/attempts/research-20260924-http-extract-inline-index/README.md`. Several forms collapse to the 922-byte pointer result; explicit-index variants diverge earlier and do not improve historical spill ownership. The current outer-`i` body is already attempt 12, so recompiling it would repeat an existing output.
- Routing the first reader through `extractLine`: `docs/attempts/research-20260924-http-extract-next-dwarf-helper/README.md`. It collapses to a known 918-byte output and loses exact `HTTPFetchInternal` and `dumpHTTPResponse`.
- GCC candidate pass boundary: IRA assigns the current argument homes at -0x838/-0x834 and the stores persist through postreload. The known source forms do not expose a distinct upstream cause.
- Historical DIEs put `i` and `pResponse` in function scope, with two inline reader `last`/`c` scope families. The inlined helper `bytesRead` is optimized out. The current source already uses the evidence-backed first-reader lifetime and unsigned-byte state; adding a caller `bytesRead` local contradicts the DIE evidence.

## Next useful discriminator

Additional historical source, declaration-order/DWARF evidence for the missing live ranges, or a compiler-side explanation of why the historical and current IRA homes differ is needed before another source compile. The next decision should be a focused allocator/source-lifetime probe only after such evidence identifies a candidate variable or live-range boundary. Do not expand a declaration-count or spelling sweep.

No recovery credit is claimed. No maintained source, generated state, or recovery ledger was changed.
