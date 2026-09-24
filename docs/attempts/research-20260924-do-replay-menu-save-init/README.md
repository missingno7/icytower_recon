# `do_replay_menu` save-buffer initialization follow-up — 2026-09-24

## Scope and control

Research-only body overlays for `game-main`, built as the complete TDM-2 GCC 4.4.1 historical-order TU with `--no-prototypes`. No maintained source, generated current state, or recovery ledger changed. The corrected scope/exit control is the retained `play-again-exit.c`; its control remains `DIFFER`, 2643/2661 bytes, first mismatch +364, with 63/82 exact functions and no gains or losses.

## New source-backed discrepancies

The original DWARF source lines and disassembly expose three save-buffer operations that the retained body had misreconstructed:

- At original function offset +364, `fname` is filled with 511 spaces. At +375, the NUL store targets the array base at `-0x218(%ebp)`, so the statement is `fname[0] = 0`, not `fname[511] = 0`.
- At +382, the original fills the `pname` array at `-0x418(%ebp)` with 511 spaces before the guest/non-guest `strcpy` paths. GCC emits this inline as `rep stos`, so it is absent from the direct-call inventory.
- At +427..+454, the original fills `comment` and stores NUL at its base `-0x618(%ebp)`, so the terminator is `comment[0] = 0`, not `comment[511] = 0`.

The byte offsets agree with the card's DWARF locations for `fname`, `pname`, and `comment`, and the historical source line table maps these instruction ranges to lines 5508–5510. The menu state CFG reaches both `strcpy` paths after the `pname` fill. These are source operations supported by the original, not padding or call-count inferences.

## Historical-order batch results

All probes retained 63 exact functions out of 82 with no gains or losses; all remain `DIFFER` and the complete `.text` contribution remains unequal.

| Probe | Change | Result |
|---|---|---|
| `drm-save-init-control-20260924` | Corrected scope/exit body | 2643/2661 B, first +364 |
| `drm-pname-fill-511-20260924` | Add `memset(pname,' ',511)` | 2647/2661 B, first +376 |
| `drm-pname-fill-sizeof-retry-20260924` | Same fill as `sizeof(pname)-1` | 2647/2661 B, first +376; same effective output as the literal count |
| `drm-save-init-zeroes-20260924` | Change both terminators to index 0 | 2643/2661 B, first +364; distinct effective output, no strict gain |
| `drm-save-init-all-20260924` | Add `pname` fill and both index-0 terminators | 2647/2661 B, first +406 |

The pname fill changes the target output and advances the first mismatch by 12 bytes. The two terminator corrections alone change the effective output but do not move the first mismatch. Combining the evidence-backed operations advances the first mismatch further, but no exact function match was produced. This is an information-gain boundary for these initialization hypotheses; further work should align the newly exposed +406 window or investigate a distinct source/context fact rather than vary equivalent fill spellings.

## Artifacts

- Candidate bodies and manifests: this directory (`control.c`, `pname-fill-511.c`, `pname-fill-sizeof.c`, `terminators-zero.c`, `all-observed-inits.c`, and batch manifests).
- Historical-order receipts: `docs/attempts/tu-context/game-main/drm-pname-fill-511-20260924.json`, `drm-pname-fill-sizeof-retry-20260924.json`, `drm-save-init-control-20260924.json`, `drm-save-init-zeroes-20260924.json`, `drm-save-init-all-20260924.json`.
- Full TU comparisons and objects are retained under the matching `build/tu-context/game-main/<label>/` directories.
- Effective outcome groups: `python tools/effective_outcomes.py game-main do_replay_menu --pattern 'drm-save-init-*-20260924.json' --compact`.
