# `update_game_menu` interface and context follow-up

Date: 2026-09-24. Research-only isolated whole-TU probes using locked TDM-GCC 4.4.1 (`-O2`, i386, x87). The current focused card marks `body_edit_allowed: false` and `COMPILER_CONTEXT_DEPENDENCY`; I did not probe alternate control-flow spellings. No maintained source or recovery ledger was edited.

## Evidence read

Read `docs/current/functions/menu/update_game_menu.json`, its detailed evidence, both rows of `docs/attempts/game-menu/update_game_menu.jsonl`, and the existing context/RTL records in `docs/attempts/compiler-context/game-menu/`. Both historical body-attempt rows preserve the current body and remain FAST/DIFFER (first mismatch +103).

The historical function at `0x417adc` is 583 bytes. Its line table maps the function start through the menu scan and `draw_menu` call (lines 134–145), then maps the controller branches and position updates (lines 147–156), followed by corresponding later out-of-line blocks. Original disassembly confirms the menu scan ends at +0x30; `draw_menu` is called at +0x5b; the `ctrl` null guard at +0x63 branches to +0x21c; the up/down and F1 paths then feed the selected-item and return-value blocks. Current source expresses those same operations as the do/while scan, nested `if (ctrl)` checks and the selection update.

Historical DWARF says the parameters are `BITMAP *bmp` and `void **data`; the current candidate declaration is `void *bmp` and `int *data`. The caller has a local `void *data` and passes `&data`. No type-layout issue is recorded. The target card reports 582 candidate bytes, first mismatch +103, 379 differing offsets, 11 unequal relocations, and a local interface conflict. The verified candidate CU has seven exact functions; `draw_menu`, `update_game_menu`, and `handle_menu` remain DIFFER.

Prior compiler-context evidence mechanically observed that omitting `draw_menu` with the target body unchanged changes two target bytes at offsets 97 and 100, without changing the 582-byte extent; omitting `reset_menu` changes no target bytes; omitting `build_menu_string` changes the same two offsets as `draw_menu`. Each context variant still differs from the original. The RTL evidence for the draw-menu omission diverges first at GCC expand (pass 128), but is only a textual diagnostic and does not establish the code-generation cause.

## Isolated interface hypotheses

The research copy and three overlays are in this directory. Each overlay corrected the current prototype and definition to the DWARF-backed parameter shape in a full `game-menu` TU compile. Variants were: `BITMAP *` only; `void **` plus direct pointer assignment (`*data = m[pos].data`); and both parameter corrections together.

All three compiled, retained the same seven exact functions, and produced the same target instructions and effective relocations (deduplicated fingerprint `71a83ee6d2ee1c0a6f64ed2ebee543bac49832a69fd9cdc7446581e5ad72cdc6`). Each remains 582/583 bytes, DIFFER at +103, with 379 differing offsets and 11 unequal relocations. This rules out the observed parameter mismatch as the direct cause of the emitted code difference, while documenting the historically correct interface for any future interface work.

## Blocker and next discriminating experiment

No strict target candidate was found. The type-only corrections have zero code effect. Existing current-order source already reflects the historical visible controller operations, and body edits are disallowed by the focused card. The remaining concrete signal is compiler-context sensitivity to `draw_menu`, a preceding-emission peer whose current body is itself DIFFER (956 candidate / 1,118 historical bytes). The next high-information experiment is to use an isolated, source-backed `draw_menu` candidate that changes its emitted-body/peephole context while keeping `update_game_menu` byte-for-byte and source-byte-for-byte fixed, then rerun the strict whole-TU comparison. Do not treat the two changed offsets or RTL text divergence alone as proof of historical match.

## Artifacts and integrity

- Full source base: `menu-baseline.c`; interface overlays: `interface_bitmap.c`, `interface_data.c`, `interface_both.c`.
- Full TU receipts: `build/tu-context/game-menu/luna-update-game-menu-interface_{bitmap,data,both}-20260924/comparison.json`.
- `src/menu.c` SHA-256: `9496bbbaadc1b1cf646ddc733ed5e040ff18c7106e58d20f57c2212d611a5003`.
- `src/recovery.json` SHA-256: `2f0710c753742dda1de1bb624cce6fa378ba14c6a205adb9e3552c67bbd8f360`.
