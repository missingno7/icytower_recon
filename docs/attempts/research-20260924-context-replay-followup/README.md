# Context follow-up: `update_game_menu`

Date: 2026-09-24. Research-only isolated `game-menu` TU probe using locked TDM GCC 4.4.1 (`-O2`, i386, x87). The candidate changes only `draw_menu`; `update_game_menu` remains byte-for-byte from maintained `src/menu.c`.

## Candidate basis

Current card `docs/current/functions/menu/update_game_menu.json` records a known `COMPILER_CONTEXT_DEPENDENCY`: omitting the incomplete `draw_menu` peer changes target bytes at offsets 97 and 100 with target body unchanged. It also has a concrete interface discrepancy against original DWARF (`BITMAP *bmp`, `void **data` historically; candidate currently `void *bmp`, `int *data`) and complete typed local evidence (`num_posts`, `old_pos`, `pos`, `return_value`). Parameter-only whole-TU variants already collapsed to one output, so a typed interface fix alone is not a discriminator.

## Probe

Overlaid the retained source-backed, frame-correct `draw_menu-recorded-candidate.c` from `research-luna-menu-family`. The copy used here is `draw-menu-recorded-candidate.c`. Ran:

`python tools/tu_context_probe.py game-menu src/menu.c research-20260924-update-game-menu-draw-menu-context-followup-20260924 --order current --no-prototypes --body draw_menu=docs/attempts/research-20260924-context-replay-followup/draw-menu-recorded-candidate.c`

Result: compile succeeded; strict exact-function count stayed 7; no gains/losses; `update_game_menu` stayed DIFFER at its current first mismatch +103. The probe reports no effective `code_changed_with_unchanged_body`; its raw-only list includes `update_game_menu` and `handle_menu`, so the observed changes are relocation/layout encodings, not a normalized target body change. Whole `.text` contribution remains unequal. Receipt: `build/tu-context/game-menu/research-20260924-update-game-menu-draw-menu-context-followup-20260924/comparison.json`.

## Assessment and discriminator

`update_game_menu` is a valid same-signature lead because its parameters/locals are DWARF-grounded and the incomplete `draw_menu` neighbor is a measured context dependency. This concrete source-backed neighbor candidate did not reproduce an effective target-body change; do not promote a context inference from raw relocation shifts. Its interface spellings remain historical evidence, but prior parameter-correction overlays had no target code effect.

The next discriminating input is a different historically constrained `draw_menu` emission candidate, with `update_game_menu` held source-identical; compare resolved effective target bytes and strict function result. A repeated type-only edit or peer omission is not discriminating.

No maintained source, current generated state, recovery ledger, or accepted body was changed.
