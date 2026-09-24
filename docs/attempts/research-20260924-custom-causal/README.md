# `load_character_bmp` causal probe (2026-09-24)

## Result

A full-TU, locked TDM-2 `-O2` probe tested whether an explicit source label can position the first `fopen` failure block just before the later `[datafile]` fallback, while a `goto` keeps successful fallthrough out of that error block. This is a source-only experiment; no maintained source, generated current state, or recovery ledger was changed.

The candidate remains `DIFFER`: 2,009 bytes versus 1,992, first mismatch at offset 134, 1,709 differing byte positions. All eight peer functions that were `FUNCTION_MATCH` in the baseline remain exact. The current candidate is 1,993 bytes. The explicit label therefore worsens the target by 16 bytes and does not repair its first branch.

## Causal evidence

The historical branch at offset `+0x84` jumps to `+0x56d`. That block logs “Could not open %s”, zeroes the return value, and jumps to a shared epilogue at `+0x475`. Current code keeps the same failure semantics; GCC emits the block at `+0x77b`. Existing retained work already tested shared null exits, the outer `if (fp)` form, alternative parser-loop exits, alignment flags, and declaration/scope variants. The current DWARF has the three nested error buffers, image/color-conversion scope, frame-cropping locals, and datafile scope; no missing local or type gap is evidenced.

The new `goto` placement test makes the error block appear after the frame path in source, before `[datafile]`, but GCC still does not match the historical first branch and the whole function grows to 2,009 bytes. This narrows the unresolved factor to a different historical surrounding block shape or compiler block-placement decision. It does not justify another local declaration guess or a match claim.

## Artifacts

- `open_error_before_fallback.c`: complete isolated full-TU source overlay.
- `result-open-error-placement.json`: compact strict outcome and preserved peer list.
- `build/research-20260924-custom-causal/open_error_before_fallback/comparison.json`: full strict function, relocation, and symbol comparison.
- `docs/current/function-evidence/custom/load_character_bmp.json`: read-only current DWARF/CFG evidence.
- `docs/attempts/research-20260924-custom-character-bmp/handoff.md` and `docs/attempts/research-luna-custom-loader/status.json`: prior source/CFG and alignment trials consulted.
