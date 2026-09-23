# `main_menu_callback` storage-scope probe (2026-09-24)

Historical-order, isolated full-TU probes of the retained rank/version
presentation. No maintained source, current document, or recovery ledger was
changed. Both probes use `--no-prototypes`, the same caller-side
`get_rank(Tprofile *)` declaration and Allegro cursor include, and keep
`new_game` and `run_demo` exact.

## Evidence and experiment

Original DWARF gives `face` and `count` function-static scope under
`main_menu_callback`; the storage cards
`docs/current/storage/game-main/129929.json` and `129948.json` record original
addresses `0x4dd31c` and `0x4dd318`. Maintained `src/main.c` instead declares
both at file scope. The retained callback also already contains the supported
rank/version presentation and cursor work.

The historical-order control used the retained callback unchanged. It kept
63/82 exact functions and the expected same-CU neighbors, including
`new_game` and `run_demo`. The callback remains `DIFFER`, 3,775 bytes against
3,741, and its first data references resolve `count` and `face` to the wrong
candidate `.bss` addresses (`5101380`/`5101376` vs `5100312`/`5100316`).

The single source-backed variant moves `face` and `count` to local-static
declarations in the callback and removes the file-scope copies from the
isolated source skeleton. This makes the callback's initial `.bss` relocations
resolve exactly to `5100312` and `5100316`. It remains `DIFFER`, 3,775/3,741,
with later instruction and data mismatches. The TU retains `new_game` and
`run_demo` as exact functions, but total exact functions fall to 62/82 because
`draw_progress_bar` loses its previously exact `.bss+0x0c` target: the variant
emits `.bss+0x14`, whose owner cannot be independently resolved. This proves a
real storage-order interaction; it does not justify accepting the callback
or changing the neighbor.

An initial shadow-only variant left the obsolete file-scope variables in place.
It also kept the callback `DIFFER` and yielded 62/82 exact functions, so the
clean removal variant is the informative storage result. No size-driven or
rank/interface spelling variants were run. The `get_rank(Tprofile *)`
caller-side declaration remains supported by original main-CU evidence, while
the reconstructed profile-CU `Tprofile_rank *` definition remains an
independent unresolved type conflict.

## Receipts and blocker

- Historical-order control receipt:
  `docs/attempts/tu-context/game-main/luna-main-menu-scope-baseline-historical-20260924.json`
- Shadow-only diagnostic receipt:
  `docs/attempts/tu-context/game-main/luna-main-menu-local-statics-historical-20260924.json`
- Clean local-static diagnostic receipt:
  `docs/attempts/tu-context/game-main/luna-main-menu-local-statics-clean-historical-20260924.json`
- Full object comparisons and locked compiler build metadata are in matching
  directories under `build/tu-context/game-main/`; the clean probe wrapper,
  declarations, and retained body are in this research folder.

The closest blocker is candidate BSS layout: moving two variables into their
DWARF-supported function scope corrects this callback's first references but
shifts the independently exact `draw_progress_bar` relocation and leaves the
callback's remaining code differences. Further work needs source-backed
evidence for historical BSS allocation/order and the remaining callback CFG;
do not promote the isolated candidate or claim layout-only equality.


## BSS owner map and declaration-order follow-up

The original DWARF owner map around this region is:

| Original VA | Owner / scope | Evidence |
|---|---|---|
| `0x4dd314` | `in_replay_menu`, global | CU DWARF location |
| `0x4dd318` | `count`, `main_menu_callback` function-static (line 5139) | DWARF location and storage card |
| `0x4dd31c` | `face`, `main_menu_callback` function-static (line 5138) | DWARF location and storage card |
| `0x4dd320` | `someCounter`, lexical local in `play` | CU DWARF location |
| `0x4dd324` | `blit_mode`, common/function-static in `blit_to_screen` | COFF common plus DWARF |
| `0x4dd328` | `p`, function-static in `datafile_callback_slow` | DWARF location and storage card |
| `0x4dd32c` | `value`, lexical local in `draw_progress_bar` | DWARF location; original relocation target |

The retained historical-order control's COFF `.bss` local-symbol offsets are
`old_msc +0`, `someCounter +4`, `p +8`, `value +12`, `load_character count
+16`, `take_screenshot number +20`; old file-scope `face` and `count` are at
`+1056` and `+1060`. The control independently resolves the original
`draw_progress_bar` relocations from `.bss+0x0c` to `0x4dd32c`.

The clean function-static candidate emits `count +0`, `face +4`, `old_msc +8`,
`someCounter +12`, `p +16`, `value +20`, then the other two function-local
owners at `+24` and `+28`. Its callback relocations to `.bss+0` and `.bss+4`
resolve to the original `count`/`face` addresses. Its draw-bar relocation is
`.bss+0x14`; the candidate section base is unproved, so the apparent base
`0x4dd318` (from the callback targets) would put `value` at the original
`0x4dd32c`, but this is not accepted as independently resolved ownership.
These offsets also put `someCounter` four bytes later than its original DWARF
location, showing that the callback anchor alone does not prove the whole
candidate BSS map.

I tested the source-backed declaration sequence `face`, `count`, `old_msc`,
matching their original DWARF declaration lines 5138-5140. Its COFF order is
`old_msc +0`, `count +4`, `face +8`, `someCounter +12`, `p +16`, `value +20`.
The callback's `count +4`/`face +8` relocations again land at `0x4dd318` and
`0x4dd31c`, but this constrains `.bss` base to `0x4dd314`; `.bss+0x14` then
lands at `0x4dd328`, four bytes before the original `value`. The exact-function
total stays 62/82 and the same `draw_progress_bar` function ceases to match.
This supported reorder does not solve the section ownership conflict.

The local-static probe receipt is
`docs/attempts/tu-context/game-main/luna-main-menu-local-statics-historical-decl-order-20260924.json`;
the detailed COFF symbols, relocations, and function inventory are in
`build/tu-context/game-main/luna-main-menu-local-statics-historical-decl-order-20260924/comparison.json`.
No source outside this research archive was edited.
