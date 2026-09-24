# `update_game_menu` context follow-up (2026-09-24)

Scope: isolated compiler-context research for `game-menu/update_game_menu` after the accepted typed `view_profile(Tprofile *)` interface. No maintained source, generated current card, recovery ledger, or protected body was edited.

## Strict candidate

The maintained typed source compiles successfully with locked TDM-2 at `-O2`. `update_game_menu` remains **DIFFER**, 582 bytes versus historical 583, with first strict mismatch at function offset 103 (`0x00417b43`): candidate byte `0x39`, original byte `0xb1`. It is not a function or layout match. The full fresh function/object comparison is under `build/tu-context/game-menu/research-20260924-menu-update-context-typed/comparison.json`; whole-TU result and full relocation/object inventory are retained beside it. The run preserves all 7/10 existing exact menu functions and loses/gains none.

## Isolated hypotheses and outcome

Commands used `tu_context_probe.py` with `--order current --no-prototypes`; only the untyped control uses the isolated `menu-untyped-control.c` retained below. A second source-order hypothesis swapped `draw_menu` after `update_game_menu` without changing either body.

`effective_outcomes.py game-menu update_game_menu --pattern 'research-20260924-menu-update-context-*' --compact --response` grouped all three runs into **one effective output** (`81f02039d62d9471`):

- accepted typed `extern int view_profile(Tprofile *);` (current source control);
- untyped `extern void view_profile(void *);` retained diagnostic control;
- `draw_menu` reordered after `update_game_menu`.

Each compilation retained all 7/10 exact peers. The target stayed 582 bytes and DIFF with first difference at offset 103. The retained earlier draw-menu-body context follow-up also produces this same effective outcome. No candidate improvement or exact claim resulted.

This establishes that the accepted `view_profile` typing does not change `update_game_menu` effective code in this CU, and a source-order swap alone does not perturb its context. Stop further local declaration spellings and source-order variants.

## Next discriminator

The existing current card records a separate omitted-peer experiment: omitting `draw_menu` changes only target offsets 97 and 100 while keeping its extent 582. That is evidence of compile-context dependency, but no historical target context has been recovered. The next useful probe should change the relevant GCC emission/cgraph or peephole predecessor context with DWARF-backed evidence, or compare against a recovered historical `draw_menu` definition. Do not edit the seven exact peers; do not treat an isolated output as proof.

## Artifacts

- `menu-untyped-control.c`: untyped signature control, isolated from `src/`.
- `order-draw-menu-after-update.json`: isolated order list.
- Typed run: `build/tu-context/game-menu/research-20260924-menu-update-context-typed/`.
- Order run: `build/tu-context/game-menu/research-20260924-menu-update-context-order-draw-after-update/`.
- Untyped run: `build/tu-context/game-menu/research-20260924-menu-update-context-untyped/`.

## Whole-CU receipt inventory

The focused typed receipt covers all 10 functions: seven exact (`build_menu_string`, `get_selection_value`, `get_slider_value`, `key_to_str`, `reset_menu`, `set_selection_value`, `set_slider_value`); `draw_menu`, `handle_menu`, and `update_game_menu` remain DIFFER. It records 52 object symbols and all 395 COFF relocations (83 `.text`, 154 `.debug_info`, 1 `.debug_line`, 134 `.rdata`, 20 `.debug_frame`, 1 `.debug_pubnames`, 2 `.debug_aranges`). The only common allocation is `_stepIn` (16 bytes). No `.data` or `.bss` payload is allocated; `.rdata` is 768 bytes and initialized-data content differs. Whole `.text`, OBJECT_MATCH, and CU_MATCH are false. The comparison JSON retains the complete symbol and relocation records.
