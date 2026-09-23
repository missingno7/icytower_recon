# `draw_profile_selector` interface and DWARF probes

This isolated batch extends the prior typed late-header full-TU baseline. It changes only the selector definition in that retained overlay and uses TDM GCC 4.4.1 TDM-2 with `-O2 -g -mfpmath=387` and the locked target configuration. It does not modify `src/`, current cards, recovery state, or shared source.

## Hypothesis and evidence

The original DWARF names `width`, `height`, and `scrollHeight` in the selector and names row-local `icon` (`char`) and `selected` (`int`). It records `selected` at `EBP-0x44`; `icon` is optimized out. Original `BITMAP*` fields are read at offsets 0 and 4. These facts motivated direct `bmp->w` / `bmp->h` accesses and an explicit row-local `icon` / `selected` form.

## Outcomes

All probes compiled as full translation units and strict comparison preserved the same 11 `FUNCTION_MATCH` functions. No exact function was gained or lost.

- `bitmap_native_fields`: code identity exactly collapses to the earlier typed-late-header selector (`ca125968…`); `draw_profile_selector` stays 1250/1268 bytes, first mismatch +8. Direct `BITMAP` fields do not change generated selector code.
- `typed_historical_row_locals`: 1269/1268 bytes, first mismatch +8; selector code changes but does not recover the entry frame.
- `typed_row_and_extent_locals`: 1281/1268 bytes, first mismatch +8; likewise no recovery.

The shared caller `select_profile` remains `DIFFER`, 2698/3070 bytes, first mismatch +12 in every variant. The selector entry still reserves `0x9c` bytes versus the oracle's `0xbc` (`-32` bytes), which is the byte at the first strict mismatch. The typed baseline and explicit row-local forms do not explain this frame difference, so there is no evidence here that a further interface spelling will unlock either function.

The historical selector uses Allegro bitmap virtual dispatch for drawing operations; the typed candidate already emits the same dispatch, so this is not a missing native `BITMAP` call path. The aggregate layouts remain independently supported by `Tprofile` and `Tavailable_profile` DWARF/header evidence. The remaining blocker is selector source/CFG/frame recovery, plus the large independent caller mismatch.

## Artifacts

- `batch-results.json`: compact outcomes and all 11 exact neighbors.
- `batch-summary.json`: detailed result and object section evidence.
- `run_batch.py`: reproducible local runner.
- `overlay/*.c`: complete full-TU candidates.
- `build/*/comparison.json`: strict per-function, section, initialized-data, common/BSS, and relocation reports.
- `build/*/unit.o`, `unit.d`, `interfaces.aux`, and compiler logs: build inputs and outputs.

No status or ledger file was edited.
