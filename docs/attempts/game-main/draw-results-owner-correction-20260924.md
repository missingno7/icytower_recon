# `draw_results` table owner correction

## Evidence

- Historical DWARF DIE 136974 identifies global `category_names` as `char *[15]`, declared in the main CU at line 124, with `DW_OP_addr 0x4bc080`. The original COFF owner is `.data + 0x80`, size 60 bytes (see `docs/current/storage/game-main/136974.json`).
- PE section mapping places VA `0x4bc080` in `.data` at file offset `0xba680`. The complete 60-byte table is 15 pointers. Resolving those pointers through PE sections yields, in order: `Score`, `Best Combo`, `Floor`, `Lost Combo`, `Top Floor, No Combos`, `Clock Challenge 1` through `Clock Challenge 5`, then `Single Jump Sequence`, `Double Jump Sequence`, `Triple Jump Sequence`, `Quadruple Jump Sequence`, and `Quintuple Jump Sequence`. The exact 20-byte prefix of the first five pointer entries occurs once in the PE.
- The retained source had only an uninitialized `char *category_names[15]` and introduced `static char *result_categories[5]`. The historical `draw_results` instruction at offset 124 indexes the global 15-entry table. The candidate-only five-entry static table was therefore the wrong owner even though its first five strings matched.

## Isolated correction

The historical-order overlay at `build/tu-context/game-main/draw-results-owner-correction-20260924/overlay/src/main.c` initializes the existing global `category_names[15]` with the 15 strings above, removes `result_categories[5]`, and changes the `draw_results` lookup to `category_names[categories[i]]`. It does not edit `src/main.c` or `src/recovery.json`.

In the resulting COFF object, `_category_names` is `.data + 0x80`; all 15 initializer slots have `IMAGE_REL_I386_DIR32` relocations to `.rdata` literals whose independently read contents match the corresponding original strings. The corrected `draw_results` reference has an `IMAGE_REL_I386_DIR32` relocation to `.data + 0x80`, which is the same DWARF/COFF owner as the historical global. Strict comparison classifies `draw_results` as `FUNCTION_MATCH`.

## Whole-TU outcome and limits

The historical-order baseline retained 63 `FUNCTION_MATCH` peers. The correction has 64, with no losses and `draw_results` as the only gain. See `build/tu-context/game-main/draw-results-owner-baseline-20260924/comparison.json` and `build/tu-context/game-main/draw-results-owner-correction-20260924/comparison.json`.

The correction was promoted through `draw_results_category_owner_20260924` on the current maintained main TU. The fresh strict check found 64 matches versus 63 before, with `draw_results` the sole gain, no exact peer losses, and all 15 `category_names` initializer relocations independently resolved. Function acceptance tests, diagnostic link, and global audit passed. The whole `.data` and `.rdata` contributions remain unequal; this establishes a function match and one complete data owner, not `OBJECT_MATCH` or `CU_MATCH`.
