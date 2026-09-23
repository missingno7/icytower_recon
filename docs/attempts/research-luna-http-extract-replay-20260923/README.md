# `extractHTTPResponse` isolated replay (2026-09-23)

## Current boundary and evidence

The focused function card remains `DIFFER`: 924 candidate bytes vs 923 historical, first mismatch +14, with 9/10 strict `game-httpget` functions. The current interface card is `AGREE` for `HTTPResponse *(const unsigned char *, int)`; interface spellings were already shown instruction-neutral in the prior research. Current-order no-prototype control was recompiled and retained all 9 exact neighbors.

Original DWARF has two `extractLine` inline instances in `extractHTTPResponse` (source lines 97 and 107). Their inline locals include `bytesRead`, unsigned `last` and `c`; the output pointer formal `pOutBuffer` is observed in EDX in both instances. The maintained body reproduces the first status-line parser manually, using shared function-level `i` as the byte count and a local `pOut` pointer. It calls `extractLine` for the header loop, producing one inline instance. This is a source-backed CFG/declaration gap worth a bounded trial; it does not prove the exact original source text.

The existing pass work explains the risk: the direct first-line helper-call candidate creates an extra line-buffer pointer spill at `-0x84c` in the IRA-era pass output, grows the frame from `0x84c` to `0x85c`, and shifts `dumpHTTPResponse`'s peephole scratch from CX to DX, losing it and `HTTPFetchInternal`. The interface, `j` scope, header-loop and helper-call variants already recorded in earlier research were not repeated.

## Adaptive current-order probes

The two new inline-expansion variants copied the actual `extractLine` body and used an independent `bytesRead`, a scoped unsigned `last`/`c`, an output-pointer local, and a top-tested bound loop. They differ only in whether the helper formals (`pOutBuffer`, `iOutSize`) or helper locals (`bytesRead`, `last`) appear first in the C declaration order. Both were compiled as complete current-order `game-httpget` TUs with `--no-prototypes`.

| Variant | Target / historical | First difference | Frame | Exact functions | Outcome |
|---|---:|---:|---:|---:|---|
| Current body control | 924 / 923 | +14 | `0x84c` | 9/10 | `77dea10a…` function hash; no neighbor changes |
| Inline helper body; locals declared before output formals | 930 / 923 | +8 | `0x85c` | 7/10 | `0ac7beb5…` function hash; loses `dumpHTTPResponse` and `HTTPFetchInternal` |
| Same inline body; output formals declared before locals | 930 / 923 | +8 | `0x85c` | 7/10 | `79335d45…` function hash; same two losses |

The two inline variants are distinct effective function and whole-`.text` outputs despite matching size, first mismatch, frame size, and exact-neighbor result. They each materialize the line-buffer pointer in the extra `-0x84c` slot; the RTL dump shows the inline output-pointer pseudo assigned to DX. This reproduces the pointer-lifetime/spill boundary identified in the earlier helper-call pass study, but neither declaration order eliminates it. No candidate meets the 9/10 neighbor constraint or matches the function. Stop local declaration variants here; the remaining issue is register/spill allocation around the inlined output pointer and the TU peephole scratch cursor, not an interface mismatch.

## Artifacts

- Current card and full evidence: `docs/current/functions/httpget/extractHTTPResponse.json`, `docs/current/function-evidence/httpget/extractHTTPResponse.json`
- Interface card: `docs/current/interfaces/extractHTTPResponse.json`
- Prior inline/CFG and IRA/peephole research: `docs/attempts/research-20260923-httpget-context/README.md`, `docs/attempts/research-20260923-httpget-context/lexical_cfg_batch/README.md`, `docs/attempts/research-20260923-httpget-pass-luna/README.md`
- Original disassembly: `docs/attempts/research-20260923-httpget-pass-luna/extractHTTPResponse-original-disasm.txt`
- Inputs: `probes/current-control.c`, `probes/inline-first-line-exact-helper.c`, `probes/inline-first-line-helper-param-order.c`
- Receipts: `docs/attempts/tu-context/game-httpget/luna-http-current-control-20260923.json`, `luna-http-inline-exact-helper-20260923.json`, `luna-http-inline-param-order-20260923.json`
- Full object/RTL/CFG comparisons: `build/tu-context/game-httpget/luna-http-{current-control,inline-exact-helper,inline-param-order}-20260923/`

No maintained source, generated current state, production ledger, or the existing dirty experiment files were edited.
