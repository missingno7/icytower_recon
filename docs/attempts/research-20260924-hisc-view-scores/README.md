# view_scores declaration placement audit (2026-09-24)

## Audit correction

The first staged overlay files, `01_staged_declarations.c` and `02_staged_initializers.c`, accidentally placed `int i;` at file scope immediately before `view_scores`. Their earlier 2558-byte result is invalid negative evidence and must not be used for promotion. Those source files and build receipts are retained to preserve the experiment history.

The corrected candidate is `03_staged_declarations_local_i.c`; it keeps `int i;` as the first local inside `view_scores`. `retained-body.c` contains exactly that complete function definition. `transaction-spec.json` is the raw TU_CONTEXT specification for the retained body, current definition order, and no generated prototypes.

## Source audit

- Historical DIEs show the 16 locals as direct function-scope children with original types: `int` (14 variables) and `BITMAP *` (`bg`, `bmp`). No type change or nested block scope is present.
- The corrected function declares each local at a location supported by its DWARF declaration line. Removing those declarations from the maintained and corrected function bodies leaves identical C token streams (915 tokens each). The complete translation units also compare byte-for-byte outside the `view_scores` function.
- No statements, expressions, branches, calls, types, or initializers changed. `i` is local in the corrected body; the candidate object has no `i` global symbol.
- The one-function retained body compiled successfully from `transaction-spec.json`'s settings using the equivalent diagnostic command:

  `python tools/tu_context_probe.py game-hisc src/hisc.c hisc_view_rawspec_fixed --order current --no-prototypes --no-dumps --focus view_scores --body view_scores=docs/attempts/research-20260924-hisc-view-scores/retained-body.c`

## Full-TU result

The corrected declaration placement compiles to the same `.text` section bytes as the maintained current-order/no-prototypes control. `view_scores` remains `DIFFER`, 2498 bytes versus 2552 historical bytes, with the existing first mismatch at offset 8. The TU retains all 10 exact hisc functions; there are no gains or losses. Object-relative ownership, common allocations, and initialized-data comparisons equal the control, and no new function or file-scope `i` symbol appears. This is not a function or CU match.

The prior invalid 2558-byte result was caused by the unintended file-scope `i`, so discard it as promotion evidence. No production source, current card, or recovery ledger was edited; no TU_CONTEXT plan, begin, or promotion was run.

Retained body SHA-256: `ddd71fe9b5ae05294ccaa5b0124aee294fbb0aeaf585fc8c6d0fecb4faf9edae`.
Transaction spec SHA-256: `52f65aa334f7011a840a8aa593551c8ca3ff0e9cabe6ae9e83edbb048bad733d`.
