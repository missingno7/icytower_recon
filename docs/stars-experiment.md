# stars.c recovery

All three historical functions in `src/stars.c` match at -O2, including the
complete 643-byte logical text contribution, inter-function padding and
independently resolved relocations. The CU has no initialized data or common
allocation. This is text equality, not object or debug-metadata equality.

DWARF establishes `Tstar` as two doubles and an int (24 bytes), and the
star-field layout as eight scalar fields plus 1024 stars (24,608 bytes).
The source preserves the historical four independent bounds checks: negative
x, negative y, x past width, then y past height. Each reset independently
generates a new depth value. `init_star_field` initializes all 1024 array
slots, not only the configured visible-star count.

The renderer relies on Allegro's historical inline rectfill and putpixel
expansions. No rendering substitute or runtime test is used. The source is
included in the synthetic integration link, which remains an unexecuted
layout experiment. See `docs/experiments/game-stars-O2.json` for the function,
symbol and relocation records.
