# `game-menu` body follow-up after typed interface promotion (2026-09-24)

Research-only whole-TU control compiled from the current maintained `src/menu.c` after `update_game_menu` was accepted as `BITMAP*` / `void**`. No maintained source, generated current state, recovery ledger, or accepted function body was edited.

## Fresh strict state

`research-20260924-menu-interface-followup-control` compiled successfully with current definition order and no added prototypes. It remains 7/10 exact. Exact peers retained: `get_slider_value`, `set_slider_value`, `get_selection_value`, `set_selection_value`, `key_to_str`, `reset_menu`, and `build_menu_string`. `draw_menu`, `update_game_menu`, and `handle_menu` remain DIFFER; no gains/losses.

The current `handle_menu` is 1066/1120 bytes, first mismatch +13, 995 differing offsets, 35/35 unequal relocations. Its effective identity is `1806630c6a86af27`, identical to the earlier control from the pre-promotion typed-profile batch. Historical prologue loads `mp` into `%edi`; candidate prologue instead assigns `%esi` to `ctrl` and `%edi` to `bmp`. Six source-backed permutations of `stepIn = dx`, `data = 0`, and `reset_menu(...)` had already kept this first mismatch at +13 and 989–995 differing bytes. The accepted callee signature therefore did not change this caller's effective code.

Current `update_game_menu` is 582/583 bytes, first mismatch +103, 379 differing offsets and 11/15 unequal relocations. The fresh effective identity `81f02039d62d9471` matches both retained typed-parameter store probes, including direct `*data = m[pos].data`; the accepted interface and the store expression do not explain the remaining body mismatch.

## Source and DWARF facts

- `handle_menu`'s original function-scope locals are `menu_return`, `handle_keys`, `done`, `data: void *`, and `key_counter`. Its nested selection, key-capture, and alert locals have matching current declarations. No supported local-type or declaration-scope discrepancy explains the prologue register choice.
- Historical `update_game_menu` locals are `num_posts`, `old_pos`, `pos`, and `return_value`, all `int`; current source declares the same set. Historical final parameter is `void **`, caller local `data` is `void *`, and `Tmenu.data` is `void *` at offset 144. Current body still narrows `m[pos].data` through `(int)`, but the retained direct-pointer-store candidate has the same effective output under the typed interface.
- The update mismatch at +103 is the displacement of the conditional branch at +101. Existing context evidence shows omitting `draw_menu` changes target bytes at +97 and +100, while the source-order-only swap did not change the effective output. The candidate `draw_menu` remains DIFFER, leaving its historical compiler context unrecovered.
- The handle key-capture path has two source `rest(2)` paths after the ESC branch; compiler CFG splits the candidate into an extra emitted call. The source-backed ternary probe collapsed to baseline. This remains a separate concrete difference, with no new source-backed strict candidate.

## Deduplication and blocker

The fresh current-source control deduplicates with the retained typed update-interface outputs. Existing handle probes group into six effective outcomes across eight runs; all remain DIFFER at +13 and preserve the same seven exact functions. The remaining candidates would repeat tested startup-order, clear/clear_bitmap, cast, ESC ternary, or parameter/store hypotheses. No source-backed declaration or body distinction remains here that justifies another variant. Current cards still mark `handle_menu` DIFFER and `update_game_menu` COMPILER_CONTEXT_DEPENDENCY / body edits disallowed.

## Artifact

- Fresh control receipt: `docs/attempts/tu-context/game-menu/research-20260924-menu-interface-followup-control.json`
- Full strict comparison: `build/tu-context/game-menu/research-20260924-menu-interface-followup-control/comparison.json`
- Prior handle batch: `docs/attempts/research-20260924-handle-menu-context/README.md`
- Prior update context analysis: `docs/attempts/research-20260924-menu-update-context/README.md`
