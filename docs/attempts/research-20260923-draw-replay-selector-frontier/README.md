# `draw_replay_selector` static sprites and sort-indicator switch

Research-only isolated TDM-2/GCC 4.4.1 `-O2` probe, based on the combined owner-aligned TU `property-case-order-source.c`. No maintained source, `src/recovery.json`, generated current state, cards, or sibling repository was edited.

## Historical CFG recovered

The original line table and CFG contain a missing sprite presentation segment between the title and list clipping:

| Historical arm | Bitmap owner | Destination | Evidence |
|---|---|---|---|
| unconditional line 491 | `data[89]` (`data+0x590`) | `(x+0x136, y+0x22)` | Original offsets 761–787 and 41c140–41c18c |
| unconditional line 492 | `data[112]` (`data+0x700`) | `(x+0x137, y+0x104)` | Original offsets 823–852 and 41c18f–41c1cd |
| `sort_method == 1` | `data[115]` (`data+0x730`) | `(x+0x112, y+0x141)` | Original block 41cc00 |
| `sort_method == 2` | `data[116]` (`data+0x740`) | `(x+0x112, y+0x163)` | Original block 41cade |
| `sort_method == 3` | `data[113]` (`data+0x710`) | `(x+0x11e, y+0x163)` | Original block 41c990 |
| `sort_method == 4` | `data[114]` (`data+0x720`) | `(x+0x11e, y+0x141)` | Original block 41c94e |

The source-level `draw_sprite` form reproduces the original inline vtable depth branch. Unsupported values fall through without a sort indicator, matching the CFG. This adds real datafile asset references and no synthetic literals or padding.

## Strict isolated results

- Combined owner-aligned baseline: `draw_replay_selector` 3007 bytes; sort-switch-only probe: 3328; static sprites plus switch: 3528. Original is 3726 bytes.
- Final probe remains `DIFFER` (first mismatch at function offset 8; 97 unequal relocations). It is a partial body reconstruction, not a strict candidate.
- Eight functions remain `FUNCTION_MATCH`: `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, `save_replay`, `create_replay`, `get_replay_property`.
- The remaining seven CU functions remain `DIFFER`: `calc_replay_checksum_131`, `calc_replay_checksum`, `draw_replay_selector`, `load_replay`, `replay_selector`, `my_strcmp`, and `add_itr_file`.
- Object contributions baseline → final: `.text` raw size 11132 → 11652, relocations 359 → 370; `.rdata` raw size 1184 and relocation count 95 in both; `.data`/`.bss` stay empty; external common symbol set is unchanged. Final object hash is `4f2ddf549b3788bb2334d76054808ccd1a819c8f9594be5011688446aa3b90a9`. The `.rdata` section hash changes with the altered TU output; no new literal owner was introduced.

## Artifacts

- `selector-combined-baseline-20260923-source.c` / `...-functions.json`: deduplicated source-identical baseline anchor (SHA-256 `9f223c2b4a1057cf299ba49934a017a67e2ea3b0ffeee0b88b732f9cffa93329`).
- `selector-sort-indicator-switch-20260923-source.c` / `...-functions.json`: one discriminating switch-only probe.
- `selector-static-and-sort-indicator-source.c`, `...-summary.json`, and `...-functions.json`: final two-sprite plus switch probe.
- Locked compiler objects/dumps are under `build/tu-context/game-replay/selector-*-20260923/`.

The switch and assets are directly supported by historical code/data references. Further source reconstruction is still needed for strict `draw_replay_selector` equality; this probe does not establish the rest of the missing body or justify production promotion.
