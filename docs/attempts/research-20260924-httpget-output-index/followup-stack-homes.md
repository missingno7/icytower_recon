# `extractHTTPResponse` stack-home follow-up (2026-09-24)

## Entry layout comparison

The historical function, current manual-parser output-index overlay, and first-line-helper plus output-index overlay all reserve `0x84c` bytes after saving `%edi/%esi/%ebx`. The earlier unindexed first-line-helper candidate reserved `0x85c`; its extra 16-byte frame area was attributed in the retained RTL study to a `pOutBuffer` spill first seen at IRA and stored/reloaded at `-0x84c(%ebp)`.

| Version | Entry home for `pHTTPData` (EAX) | Entry home for byte count (EDX) | First mismatch | Strict CU |
|---|---:|---:|---:|---:|
| Historical | `-0x834(%ebp)` | `-0x82c(%ebp)` | — | oracle |
| Current manual first-line parser + indexed helper | `-0x838(%ebp)` | `-0x834(%ebp)` | +14: candidate `0xc8`, original `0xcc` | 9/10; no losses |
| First-line helper call + indexed helper | `-0x834(%ebp)` | `-0x830(%ebp)` | +20: candidate `0xd0`, original `0xd4` | 7/10; loses `dumpHTTPResponse`, `HTTPFetchInternal` |
| Prior first-line helper call, unindexed helper | different frame (`0x85c`) | see prior report | +8 | 7/10; same two losses |

The indexed rewrite removes the 16-byte frame expansion in the helper-call version and restores the first argument home, but leaves the second argument four bytes below its historical home. With the current manual parser, both homes remain shifted down by four bytes. The helper-call variant also shifts DWARF's fixed `header` home from historical `ebp-2096` to candidate `ebp-2088`; the current manual-parser variant retains `ebp-2096`. Both overlays retain `slaskbuf` and `linebuf` at historical `fbreg -1056` and `fbreg -2080`. `pResponse` is in `%edi` in the original and both candidates for reported portions of its range, but its reported location ranges differ; this is register-allocation evidence, not proof of a source declaration error.

## DWARF boundary and decision

The original top-level local declarations are `slaskbuf` (line 90), `linebuf` (91), `i` (92), then `pResponse` (94), in the same order as maintained source. The original also records two `extractLine` inline instances, at call lines 97 and 107, with the helper's `bytesRead`, `last`, and `c` scopes. The current source's local types and header-loop scopes already agree with that evidence; prior work tested the DWARF-backed first-line helper call and found two exact-neighbor losses.

For both original entry parameters, DWARF location lists report `%eax`/`%edx` only over the first 36 function bytes (entry and early prologue), then provide no parameter location. They do not claim that either entry stack home is a stable source variable location. The prologue homes are generated spill/copy choices, not a DWARF declaration that can be repaired by changing a local type. The arrays and function-local types match; there is no supported alternate declaration order or additional local lifetime to test. The indexed helper is a discriminating compiler response, but it does not provide an evidenced edit that restores both homes while keeping 9 exact peers. No further probe is justified without historical pass/register-allocation evidence for the home assignment.

## References

- Focused card and original ranges: `docs/current/functions/httpget/extractHTTPResponse.json`; authoritative original DIE/location lists: `evidence/census/dwarf-dies.jsonl`, `evidence/census/location-lists.json` (DIEs 79696–80074; location-list offsets `0x2d1c`, `0x2d45`, `0x2d58`, `0x2d81`).
- Current manual-parser indexed output: `build/tu-context/game-httpget/output-index-cursor-20260924/comparison.json`, candidate DWARF in `build/tu-context/game-httpget/output-index-cursor-20260924/dwarf.txt`.
- Helper-call indexed output: `build/tu-context/game-httpget/helper-call-output-index-20260924/comparison.json`, candidate DWARF in `build/tu-context/game-httpget/helper-call-output-index-20260924/dwarf.txt`.
- Earlier IRA spill evidence: `docs/attempts/research-20260923-httpget-pass-luna/README.md` and retained RTL under `build/tu-context/game-httpget/http-pass-luna-rtlall-first-line-helper-20260923/`.

No new compile was run in this follow-up. No maintained source, recovery ledger, generated card, or exact neighbor was changed.
