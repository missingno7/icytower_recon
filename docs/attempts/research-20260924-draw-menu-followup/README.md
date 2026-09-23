# `draw_menu` type-expression follow-up

Date: 2026-09-24. Research-only full `game-menu` TU overlays compiled with locked TDM-GCC 4.4.1 (`-O2`, i386, x87). Only `draw_menu` is replaced in the copied current source; `update_game_menu` remains byte-for-byte source-identical. No maintained source, current generated state, or recovery ledger was edited.

## Historical CFG, calls, locals, and field types

`draw_menu` is 1,118 bytes at `0x41767c`. Its original prologue reserves `0x16c` bytes and assigns `bmp` to `%esi`, `mp` to `%edi`, and `m` to `%ebx`. The loop stores `stepIn=dx`, computes `h=mp->font_height-12`, starts `pos` at -1, then builds one menu string per item. It tests item flags for key output (`64`), bullet drawing (`1`), the three menu icons (`16`), and the centered bitmap (`32`), advances `m` by `0x94` and `y` by `h`, and continues while the signed flags byte is nonnegative. The historical line table and DWARF confirm `pos`, `str[256]`, and `h` at function scope; `x` is loop scoped; `key_str[32]` is inside the key block; `b` is inside the bitmap block. There is no historical `DATAFILE *assets` local.

The original uses three DATAFILE entries at `mp->fo`, `mp->fo+1`, and `mp->fo+2`, and an entry `((BITMAP **)m->data)[2]` for flag 32. `Tmenu_params` is 60 bytes with `bullet` at offset 44, `data` (`DATAFILE *`) at 52, and `fo` at 56; the current recovered header carries these types and offsets. All six `draw_sprite` source calls inline; the current compiler report identifies `draw_sprite` as inlined into `draw_menu`, so the source-level extra edge is not a missing historical call.

## Prior evidence and bounded probes

Read `docs/current/functions/menu/draw_menu.json`, its detailed evidence, all five rows in `docs/attempts/game-menu/draw_menu.jsonl`, the retained context/source notes, and `docs/attempts/research-20260924-update-game-menu/README.md`. Prior attempts already removed `assets`, tried both equivalent DATAFILE-index expression forms, and swapped `h`/`stepIn` ordering. The retained best body is `draw_menu-recorded-candidate.c` in the prior menu research folder (896 bytes, correct `0x16c` frame, first difference +16). In that output, the first selection-register mismatch is historical `mp -> %edi` versus candidate `mp -> %edx`; candidate uses `%edi` for `dx`.

The new source-backed batch tests whether redundant casts around recovered typed fields alter GCC allocation: baseline retained body; direct `mp->data[...]` access; and direct `mp->data[...]` plus `mp->bullet` access without casts. These forms are grounded in the `Tmenu_params` DWARF types. They all compile to the same effective target output and relocs:

| Probe(s) | Distinction | `draw_menu` result | `update_game_menu` result | Exact functions |
|---|---|---|---|---:|
| `luna-draw-menu-recorded_control-20260924` | retained frame-correct control body | DIFFER, 896/1118; first +16; 846 differing offsets, 6 unequal relocs | DIFFER, 582/583; first +103; 379 differing offsets | 7 |
| `luna-draw-menu-direct_data_type-20260924` | remove redundant DATAFILE cast | DIFFER, 896/1118; first +16; 846 differing offsets, 6 unequal relocs | DIFFER, 582/583; first +103; 379 differing offsets | 7 |
| `luna-draw-menu-direct_data_and_bullet_types-20260924` | remove redundant DATAFILE and BITMAP casts | DIFFER, 896/1118; first +16; 846 differing offsets, 6 unequal relocs | DIFFER, 582/583; first +103; 379 differing offsets | 7 |

`effective_outcomes.py` reports 3 probes and 1 effective output. The seven retained exact neighbors are unchanged; the TU has seven exact functions: `get_slider_value`, `set_slider_value`, `get_selection_value`, `set_selection_value`, `key_to_str`, `reset_menu`, and `build_menu_string`. `draw_menu`, `update_game_menu`, and `handle_menu` remain DIFFER. Across the batch `update_game_menu` has the same effective code/relocation fingerprint (`3961940b6cd6fa3df87ce3340d982e912d18a4097baf66fe99269b931bacb66f`); the draw body edit did not perturb its emitted function.

## Stop point and next discriminator

No strict candidate found. The source-backed type simplifications collapse before code generation. The known assets-local fix repairs the frame but does not recover historical register allocation; the remaining difference is the `%edi`/`%edx` assignment for `mp` and extensive downstream instruction selection. No further source-level lifetime, type, or expression distinction is evidenced in the current card: the scopes, field types, calls, and loop conditions now match the recorded DWARF/CFG. The next useful experiment needs new GCC-context or RTL register-allocation evidence for why historical `mp` stays in `%edi`; repeating cast, indexing, or statement-order variants is not discriminating.

## Artifacts and integrity

- Copied TU base and exact overlays: this directory.
- Full TU receipts: `build/tu-context/game-menu/<label>/comparison.json`.
- Effective-output grouping: `python tools/effective_outcomes.py game-menu draw_menu --pattern 'luna-draw-menu-*-20260924.json' --compact`.
- Maintained `src/menu.c` SHA-256: `9496bbbaadc1b1cf646ddc733ed5e040ff18c7106e58d20f57c2212d611a5003`.
- Maintained `src/recovery.json` SHA-256: `2f0710c753742dda1de1bb624cce6fa378ba14c6a205adb9e3552c67bbd8f360`.
