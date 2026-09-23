# `extractHTTPResponse` output-cursor discriminator (2026-09-24)

## Question and evidence

The current `game-httpget` card keeps `extractHTTPResponse` at `DIFFER`, 924 candidate bytes vs 923 historical, first difference offset 14 (`0xc8` candidate / `0xcc` original); 9/10 CU functions match. DWARF records the historical inline `extractLine` formal `pOutBuffer` in `%edx` at both inlined instances. The retained helper-call candidate previously produced a 16-byte larger frame (`0x85c` vs `0x84c`): `172r.ira` first adds a spill for the first `pOutBuffer` value, and `182r.peephole2` stores it at `-0x84c(%ebp)` before reload. Historical `extractLine` inlines occur at source lines 97 and 107. Both current calls pass `sizeof(linebuf)` where `linebuf` is 1024 bytes.

That evidence supports one specific lifetime/representation discriminator: retain the helper-call form and helper ABI, but keep `pOutBuffer` as a base pointer and express output writes as indices derived from `iOutSize`, writing the final NUL at byte 1023. The rewrite is isolated evidence testing, not a historical source claim.

## Results (effective outputs deduplicated)

| Overlay | `extractHTTPResponse` | Strict CU | First difference | Effective outcome |
|---|---:|---:|---:|---|
| Current manual first-line parser + indexed helper | 915 B, `DIFFER` | 9/10 exact; no losses or gains | 14 (`0xc8` vs `0xcc`) | `f375199ee62c523f` |
| Retained first-line `extractLine` call + indexed helper | 987 B, `DIFFER` | 7/10 exact; loses `dumpHTTPResponse`, `HTTPFetchInternal` | 20 (`0xd0` vs `0xd4`) | `06626c325a9ad84d` |

The second overlay restores the frame allocation to `0x84c`, removing the extra 16-byte frame seen in the earlier helper-call output. This is consistent with eliminating the earlier pointer spill. It does not recover the original argument spill layout: its entry stores are at `-0x834` and `-0x830` versus historical `-0x834` and `-0x82c`. The body grows to 987 bytes, and two exact neighbors are lost, so this form is rejected. The current-parser overlay also produces a distinct output but remains eight bytes shorter than historical and preserves the offset-14 first mismatch. No exact candidate was found.

No pass dumps were generated for these two variants; the frame result is a compiler output discriminator, not proof that the same IRA spill is the sole cause of the whole body difference. The earlier RTL boundary and its limitation remain documented in `../research-20260923-httpget-pass-luna/README.md`.

## Artifacts

- `hypothesis.md`: rationale for the bounded rewrite.
- `httpget.c`: current complete TU with only the inline helper output writes rewritten; probe `output-index-cursor-20260924`.
- `helper-call-index/httpget.c`: same helper rewrite plus the previously retained DWARF-backed first-line helper call; probe `helper-call-output-index-20260924`.
- Receipts: `docs/attempts/tu-context/game-httpget/output-index-cursor-20260924.json` and `.../helper-call-output-index-20260924.json`.
- Strict whole-TU reports: `build/tu-context/game-httpget/output-index-cursor-20260924/comparison.json` and `.../helper-call-output-index-20260924/comparison.json`.
- `effective_outcomes.py` grouped both 2026-09-24 probes as two distinct effective outcomes. Both compiled with current order and `--no-prototypes`; no maintained source, recovery ledger, or generated card was changed.
