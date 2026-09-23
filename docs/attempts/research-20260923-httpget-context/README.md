# 2026-09-23 `extractHTTPResponse` interface and codegen probes

Scope: diagnostic-only work in this directory. No maintained source, generated state, recovery ledger, or sibling repository was edited. Candidate source copies and compiler outputs remain beneath this directory.

## Existing strict state and evidence

`extractHTTPResponse` remains `DIFFER` (923 historical bytes, 924 candidate bytes; first difference at function offset 14, candidate `0xc8` vs original `0xcc`). The original `DW_TAG_subprogram` signature is `HTTPResponse *(const unsigned char *, int)`. The current source has `HTTPResponse *(char *, int)` plus `regparm(2)`. Historical entry disassembly receives the first argument in `%eax` and the second in `%edx`, so preserve `regparm(2)` even though the function DIE does not record a calling convention.

More interface evidence comes from the original `extractLine` inline instances beneath `extractHTTPResponse`: exactly two instances, at source call lines 97 and 107. Their `pBuffer` formal resolves to `const unsigned char *`, `pOutBuffer` to mutable `char *`, and inline locals `last` and `c` to `unsigned char`. This supports the first status-line read being an `extractLine(...)` call. The current helper instead has `char *pBuffer`, signed `char last` and `char c`, and a top-tested `while` loop. Existing code in the CU calls it for header lines.

## Isolated compiler batch

All candidates were compiled with the locked TDM-2 GCC 4.4.1 command shape (`-O2 -g -mfpmath=387 -DALLEGRO_STATICLINK`, project include paths). `run_probes.py` records inputs, compiler diagnostics, object disassembly, function instruction-byte counts, and SHA-256 output identities in `probe-results.json`.

| Hypothesis | Candidate result | Effective emitted `extractHTTPResponse` output |
|---|---|---|
| Change only the function interface to historical `const unsigned char *` | Compiles; incompatible helper/log string diagnostics remain | Same as control: 924 instruction bytes, SHA-256 `77dea10a…` |
| Also change helper input type to historical `const unsigned char *` | Compiles | Same control identity |
| Call `extractLine` for the first line, as the original inline call DIE records | Compiles; both existing helper call sites inline | New identity: 920 instruction bytes, SHA-256 `40ee0e99…`; first raw mismatch is stack allocation at offset 8 (`0x84c` original vs `0x85c` candidate) |
| Combine the helper call with historical pointer/local types | Compiles | Same 920-byte helper-call identity; signedness/interface type spellings did not change code |
| Also change helper loop to `if (iDataLeft > 0) { do ... while (...) }` | Compiles | New identity: 1,012 instruction bytes, SHA-256 `3a67b762…`; larger than historical and not promising |

The 924-byte control candidate reserves the historical `0x84c` frame, but first differs at offset 14 because the saved arguments are spilled at `-0x838` and `-0x834`; historical spills are `-0x834` and `-0x82c`. The direct-helper-call candidate restores those argument spill offsets but increases the reserved frame by 16 bytes. Thus the helper-call shape is DWARF-supported yet did not explain the target’s initial stack layout; type corrections are instruction-neutral.

The `if`/`do` variant is only a diagnostic negative result. It was tested because the retained manual first-line parser uses that shape, but the source-line and inline-DIE evidence alone does not prove that the helper used it historically.

## Deduplicated outcomes and limit

The pointer-only function signature, explicit cast spelling, helper parameter type, and unsigned local type variants all collapse to the same 924-byte effective output. The two helper-call variants collapse to the same 920-byte output. No exact candidate was found; no match claim or production promotion was made. The original-EXE disassembly is local verifier evidence, not a compilation input.

## Artifacts

- `run_probes.py` and `probe-results.json`
- `extractHTTPResponse-original-disasm.txt`
- Per-hypothesis source, compile logs, and `object-disasm.txt` under each named candidate directory
- Current evidence: `docs/current/functions/httpget/extractHTTPResponse.json`, `docs/current/interfaces/extractHTTPResponse.json`, and `evidence/census/dwarf-dies.jsonl`
- Retained prior body/attempt evidence: `docs/attempts/game-httpget/extractHTTPResponse.jsonl` and `docs/attempts/game-httpget/bodies/extractHTTPResponse.c`

`objcopy` confirms the function-signature-only, helper-pointer-only, cast, and local-type variants all produce the same complete 2,336-byte `.text` contribution (SHA-256 `51a68cde…`), so these interface edits leave every emitted `game-httpget` function byte unchanged in this probe. The direct-helper-call variants produce a 2,332-byte contribution; the `if`/`do` variant produces 2,424 bytes.

## Maintained declaration follow-up

The original-backed `extractHTTPResponse` and `extractLine` unsigned-byte
declarations, including `extractLine`'s `last` and `c`, were applied to
`src/httpget.c`. Fresh 25-CU `refresh_recovery.py --verify-all` retained all
209 exact functions, including 9/10 in `game-httpget`; the generated
`extractHTTPResponse` interface card now says `AGREE`. This is an interface
correction, not a recovered function body.

The historical `HTTPFetchInternal` DWARF also types `dataPtr` as
`unsigned char *`. A trial changing that caller-local declaration in the
maintained source altered the protected exact `HTTPFetchInternal` body, and
the strict refresh rejected it. The declaration was reverted before the
successful refresh. Its correction needs an isolated caller/TU context
transaction that preserves the exact function; the present historical parser
signature accepts the existing `char *` caller with a compiler diagnostic.
