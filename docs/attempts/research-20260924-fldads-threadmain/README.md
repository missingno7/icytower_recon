# `fldads_threadmain` strict-match research (2026-09-24)

All maintained source, `src/recovery.json`, generated current state, and existing attempt ledgers remain unchanged. Candidate source overlays, summaries, full fresh CU comparisons, and scripts are retained in this directory. Locked compiler: TDM-2 GCC 4.4.1, target `game-fld-adspot`.

## Starting evidence

The focused card is `docs/current/functions/fld_adspot/fldads_threadmain.json`: `DIFFER` / `CODEGEN_SIMILAR`, 223 bytes against 223, seven differing bytes, first at `+46`. The function has eight direct calls and all are resolved. Its three DWARF locals agree with source (`shouldDownloadAds`, `statCsv`, lexical `pResponse`). The five mismatches are `.rdata` operands for strings whose bytes are equal but whose owner/placement is not independently proven (`CONTENT_EQUAL_OWNER_UNPROVEN`). Body editing remains prohibited by that ownership state.

The current CU has 11/12 exact functions. `fldads_get_random_ad` is the adjacent exact function whose relocation outcome changes in the already-known target-correct source-order branches. Historical whole-CU definition order gives the target an exact function verdict but loses four exact functions, reducing the CU to 8/12.

## New probes

- Rebuilt an unchanged-source control, corrected the local `HTTPResponse` layout to historical DWARF, and corrected `fldads_update_cache`'s definition from `int` to historical `size_t`. All three had identical effective target output and kept the same 11 peer functions exact; `fldads_threadmain` stayed `DIFFER` at `+46`. The HTTP fields keep their four-byte ABI width, and the update-cache call signature did not change emitted target bytes.
- Moved `fldads_start` to its historical position after `fldads_threadmain`, then repeated with the now-unneeded forward declarations removed. Both candidates retain 11 exact functions and the same target effective output as baseline; the first target mismatch stays `+46`. Thus the historical local caller/order correction does not control the string relocation state.
- Adaptive TU follow-up combined the known target-correct `fldads_update_local_adimg` move with moving `fldads_get_random_ad` after `fldads_threadmain`. This makes `fldads_threadmain` `FUNCTION_MATCH` (223/223), but `fldads_get_random_ad` remains `CODEGEN_SIMILAR` at `+82`; the CU remains 11/12. Moving that function after the target did not restore its relocation owner.

Effective-output deduplication is in `effective-output-hashes.json`. Type and caller variants converge exactly to the baseline target hash `42673a53…`; the successful target-context branches from the preceding 2026-09-23 research converge to `05965bf…` for the target and the same unresolved random-ad relocation outcome. Their source orderings are useful candidate evidence only, because they regress an exact peer.

## Strict status and remaining blocker

No production-safe strict candidate for `fldads_threadmain` plus all 11 protected exact peers was found. An isolated `FUNCTION_MATCH` target candidate exists only with `fldads_get_random_ad` regressed. No change has been made to production source or ledger and no promotion was run.

The remaining issue is CU read-only pool placement/ownership shared by the target strings and the random-ad floating constant. The exact target overlay resolves all 15 relocations and three direct transfers, but shifts the random-ad constant relocation from `.rdata+0x1a0` to `.rdata+0x19c`. Rearranging historical caller order, correcting evidenced type declarations, or emitting the random-ad definition after the target did not restore the pair. This requires a TU-context solution that retains both owners or independent evidence for the mapping; current string contents alone are insufficient.

## Artifacts

`typed_interface_batch.py` and `typed-interface-batch-summary.json` cover source/type hypotheses. `start_after_threadmain.py` and its comparison cover caller/source-order hypotheses. `probe_random_after.py` and its comparison cover the adaptive section-pool hypothesis. `effective_hashes.py` and `effective-output-hashes.json` deduplicate outcomes by resolved target output. Full comparison JSON is retained beside each candidate.

## Source of the four-byte section change

The measured change is caused by moving the complete, unchanged `fldads_update_local_adimg` definition before `fldads_load_cache_from_csv`, the historical order supported by their DWARF source lines (80 before 114). GCC emits those functions' `.rdata` strings in the changed order. In the baseline object, the sequence is `Warning...` at `+0x18`, `Local file...` at `+0x54`, then `Downloading %s -> %s` at `+0x8e`. After the move, it is `Local file...` at `+0x18`, `Downloading %s -> %s` at `+0x52`, then `Warning...` at `+0x68`. The later target strings and tail move by two to four bytes; the section shrinks from 420 to 416 bytes through changed padding/packing. No source literal or initialized object is added or deleted.

The original PE provides a 420-byte window from `0x4d42f0` through `0x4d4494` with `ads.csv` at its start, the target's strings in their historical content order, and the `00 fe ff 46` bytes at relative `+0x1a0`. Its bytes do not equal the baseline object `.rdata` sequence, so the window is a useful content/order observation, not proof of the original object-section boundary. The target-correct candidate's strings resolve independently through unique contents; its get-random operand remains unowned. Original `.rdata` has six occurrences of the float byte pattern; the instruction directly references `0x4d4490`, but PE bytes alone do not bind that occurrence to this CU's anonymous pool entry.

`relocation-base-constraints.json` also rejects one common-base explanation for all these references: content-resolved target strings imply multiple historical bases, while the random-ad relocation's `+0x19c` placement cannot be independently resolved. The original object or historical link map is missing, so a DWARF/PE/relocation-backed paired strict proof is unavailable. No padding or linker-placement candidate was tried; that would not supply the missing owner evidence.
