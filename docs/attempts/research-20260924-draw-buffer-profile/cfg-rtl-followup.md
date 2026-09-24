# draw_buffer CFG and RTL follow-up

Probe labels: historical-order, direct-dereference/no-`c`, makecol-prototype-removal (receipts and exact neighbor set are listed in `README.md`). `python tools/effective_outcomes.py game-profile draw_buffer --pattern 'draw-buffer-*.json' --response --compact` groups all three as `c87e157d5dda279a`.

## CFG/pass evidence

Built the maintained TU with the locked TDM-2 compiler at the standard `-O2 -g -mfpmath=387 -DALLEGRO_STATICLINK` settings plus diagnostic `-fdump-tree-cfg -fdump-rtl-expand`. Artifacts are in `build-dumps/`. The tree CFG for `draw_buffer` retains the two semantic operations in source order at the loop join: compute/load `buffer + 1`, then increment `buffer`. It has the same high-level topology described by the historical branch decode: one initial empty-buffer exit, one loop test/exit, a newline split, the two append/reset paths, and the shared loop rejoin.

The RTL expansion dump already represents the loop join as incrementing the buffer pseudo-register and then loading through its updated value. The emitted candidate consequently uses `inc ebx; mov al,(ebx)` on both append and newline paths. Historical bytes use `mov al,1(ebx); inc ebx` on both paths. Thus this is not evidence of a different source CFG; the observable mismatch is in lowering / instruction ordering after equivalent high-level operations. The 4-byte total shortening (two 1-byte pointer-load/update reorderings plus 2 bytes of epilogue alignment) accounts for the first raw byte mismatch at +27, which is the initial `je` displacement.

This diagnostic does not prove which exact GCC pass first diverges from the unavailable historical compile state: the original `.o` and compiler dump are unavailable. The current `.rdata` relocation at function offset 105/addend 133 also remains unresolved, so no layout-only classification or strict promotion follows from this CFG analysis.

## Disposition

No source body form beyond the three unique effective outcomes was justified by DWARF or the historical instruction stream. Source-form search is exhausted for this evidence set; route the remaining instruction-order/compiler-context question to supervisor investigation. Maintained source and current/acceptance ledgers were not modified.
