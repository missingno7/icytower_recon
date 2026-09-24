# `get_string` next-front audit (2026-09-24)

Research only. No maintained source, generated current state, or recovery ledger was edited. The full current body and the explicit-edge candidate are retained here. The candidate was compiled as a current-order, no-prototype full `game-main` TU with the locked compiler.

## Current supported correction

The accepted source now uses `if (keypressed()) { ... }` and then reaches `while (!cycle_count) rest(2);`. This matches the original no-key edge semantically. In the original executable, `keypressed()` is tested at function offset 500; its false branch at +502 goes directly to the cycle-count test at +232. When the count is zero, that test enters `rest(2)` at +660; `rest` returns to +232. The true path falls through to `readkey()` and switch handling, then reaches the same wait. The old source form `if (!keypressed()) continue;` skipped the wait and was corrected in the accepted TU-context transaction.

All five historical locals are represented in source and DWARF: `block` (`BITMAP *`), `letters` (`char[67]`), `i`, `tick`, and `c`. The observed calls and rendering operations are present: bitmap creation, `blit`, the `rectfill` vtable call, `textout_ex`, `blit_to_screen`, `keypressed`/`readkey`, `strchr`, `text_length`, `rest`, and the cleanup returns. The candidate does not show an omitted source-level call or local.

## Explicit historical edge probe

`explicit-no-key-wait.c` spells the observed false edge as `if (!keypressed()) goto get_string_cycle_wait;`, places the wait at that label, and keeps key processing on the true path. This changes no behavior relative to the accepted positive guard.

The strict full-TU result is `DIFFER`, 784/790 bytes, first mismatch +91, with all 63 exact main-CU peers preserved and no gains/losses. Its normalized instruction stream, relocations, and direct transfers are byte-for-byte identical to the current candidate (`docs/current/reports/game-main.json`), so the explicit branch spelling collapses to the accepted source output. It supplies no new compiler-layout lever.

## Remaining blocker

Original layout evidence shows GCC has rotated the bottom `while (!cycle_count) rest(2);` test into a shared loop latch. On first entry, original offset +227 jumps to the close-button check at +245, skipping the cycle test at +232. After an iteration, the no-key edge and the `rest` back-edge both reach +232. The current candidate instead keeps a separate bottom wait latch and places another cycle-count test at the outer-loop entry; its offset +227 is a NOP. The positive-guard accepted fix reaches the right wait path but did not cause GCC to merge/rotate this latch. Existing attempts for `goto continue`, shared returns, `while (!closeButtonClicked)`, and positive keypress guard are all retained in `docs/attempts/game-main/get-string-loop-rotation/README.md`; none restores the historical rotation. The explicit wait-label probe is an effective-output duplicate of that guard candidate.

One `.rdata` relocation owner remains unresolved at historical function offset +663 (candidate addend 316). The original switch dispatch uses a table at `0x4d4c5c`; the current verifier does not independently establish that candidate section base/owner. Keep it unresolved; it is not evidence for inventing or removing a switch operation.

No additional CFG, call, data, or DWARF fact supports another body hypothesis. Further loop or switch reshaping would be speculative, so no candidate/spec is submitted for serialized acceptance.

## Probe receipt

- Candidate body: `explicit-no-key-wait.c`
- Current body snapshot: `current-body.c`
- Full-TU comparison: `build/tu-context/game-main/research-20260924-get-string-explicit-no-key-wait/comparison.json`
- Current strict report: `docs/current/reports/game-main.json`
- Prior bounded attempts and their distinct outcomes: `docs/attempts/game-main/get-string-loop-rotation/README.md`
