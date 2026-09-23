# draw_scroller context and relocation audit (2026-09-23)

## Current state and protection

The generated current function card is authoritative: `docs/current/function-evidence/scroller/draw_scroller.json` reports `DIFFER`, 396/396 bytes, first mismatch offset 93, `COMPILER_CONTEXT_DEPENDENCY`, and `body_edit_allowed: false`. I did not edit the body, `src/`, generated current state, or recovery ledger.

The three neighbors remain exact: `scroll_scroller` (14 B), `restart_scroller` (28 B), and `init_scroller` (200 B). `Tscroller` layout and all five `draw_scroller` parameters/local `i` are already represented by the focused evidence; the card reports no local or type mismatch.

## Concrete mismatch and relocation ownership

The changed bytes are exactly `[93, 96, 100, 103, 107, 110]`. They are six register-field bytes in argument preparation for the first vertical-branch `set_clip_rect` call. From function offset 92:

- Historical: load `y` into ECX/store at `esp+8`; load `x` into EAX/store at `esp+4`; load `bmp` into EDX/store at `esp`.
- Candidate: load `y` into EAX/store at `esp+8`; load `x` into EDX/store at `esp+4`; load `bmp` into ECX/store at `esp`.

The stack argument locations and call order are the same; the compiler selected a different temporary-register assignment. The five direct external relocations in the function all resolve equal to the original: `set_clip_rect` at offsets 113, 283, 382; `textout_centre_ex` at 239; and `textout_ex` at 340. There is no data relocation at the mismatch, no function-owned static object implicated by the card, and no call-target/layout difference that could explain the six bytes. This makes a relocation-owner repair unsupported by present evidence.

The candidate declarations in `include/scroller.h` are standard prototypes for the same four source functions. Both isolated prototype-order permutations retained cgraph/emission order `scroll_scroller`, `restart_scroller`, `draw_scroller`, `init_scroller`, preserved the three exact neighbors, and deduplicated to baseline `draw_scroller` output. No signature mismatch is indicated by current cards or the TDM aux file.

## Whole-TU context evidence

Prior isolated context evidence, pinned to unchanged `src/scroller.c`, establishes an effect but not a repair:

- Baseline resolved `draw_scroller` identity is 396 B with the six original differences.
- Omitting the emitted predecessor `restart_scroller` changes resolved target bytes at offsets 13, 15, 118, and 121, while the six offsets above remain different. The omission also makes the peer absent, so this is not a candidate.
- Omitting `init_scroller` or `scroll_scroller` deduplicates to baseline.
- Reordering the four header prototypes in two ways also deduplicates to baseline.
- Older `-fno-unit-at-a-time` evidence deduplicates to the restart-omission output class and makes `restart_scroller` DIFFER; `-fno-schedule-insns2` deduplicates to baseline. Neither is an acceptance input.
- The restart omission's first changed RTL snapshots are in `expand`, then `initvals`/`unshare`; recorded differences include temporary/label numbering. These dumps demonstrate compiler context sensitivity, but historical GCC internal state is unavailable, so they do not identify the exact allocator state that produced the historical register choice.

The original and candidate function order is the same in the COFF layout. Changing prototype order does not change cgraph order. Thus source-definition order and relocatable section placement have no supported corrective edit here. The peer probe is sufficient to explain the protected workflow state; it does not explain which source-level or upstream difference made the historical compiler choose ECX/EAX/EDX.

## Stop point and next evidence needed

No new source/header/Allegro-owner compile probe was run. Existing evidence leaves no source-supported discriminating owner hypothesis: type/signatures match, relocations resolve to the same targets, and prototype order is negative. Further reorder or body spelling probes would repeat known outcomes or alter a protected exact neighbor. The causal gap is the historical compiler's per-function internal context before the first call setup; no original RTL/cgraph dump or independent original object for the `scroller.c` TU is available here. A useful next input would be that historical compiler trace or a validated original CU object with its symbol/relocation and pass context. Until then the six-byte register-allocation mismatch remains a supervisor context issue, not a body repair or layout match.

## Artifacts

- Current function evidence: `docs/current/function-evidence/scroller/draw_scroller.json`
- Prior baseline/peer probes and RTL snapshots: `docs/attempts/research-20260923-scroller-context/evidence/game-scroller/draw_scroller.json`, `draw_scroller-rtl.json`
- Prior declaration-order overlays and strict CU comparisons: `docs/attempts/research-20260923-scroller-context/tu-context/game-scroller/luna-scroller-restart-prototype-first-20260923.json` and `luna-scroller-reverse-prototype-order-20260923.json`
- Strict baseline full-CU comparison including function relocations, all sections, symbols and data ownership: `docs/attempts/research-20260923-scroller-context/build/game-scroller/draw_scroller/reference/comparison.json`
- Prior context conclusions: `docs/attempts/research-20260923-scroller-context/findings.md`
