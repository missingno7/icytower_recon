# `view_scores` recovery map

`view_scores` spans `0x404c38..0x405634` (2,552 bytes) in `hisc.c`. It creates
backing bitmaps, renders high-score tables, and enters an interactive control
loop. The oracle polls the shared controls, uses up/down/fire navigation,
checks menu focus, composites through `blit_to_screen`, waits on frame timing,
then clears keyboard state and destroys its temporary bitmap.

The current source candidate is 2,414 bytes at `-O2`. It captures the observed
asset order: it builds the score-panel bitmap from datafile entries 66, 65,
and 64; draws each non-empty table at `x=40`; scrolls in 16-pixel steps; and
fades the panel over a captured screen bitmap. The main and exit frames also
draw entries 9 and 6 at `x=626-dark`, at y positions 380 and 40. It is
`DIFFER`, not an exact recovery: the original retains 138 bytes of unmatched
control and presentation structure.

The source recovery must retain the selection and animated table presentation;
calling `draw_table` once or substituting a static score list is not an
equivalent viewer lifecycle.

DWARF fixes the interface and animation state: parameters `tables` and
`names`; locals `bg`, `pageY`, `targetY`, `dark`, `targetDark`, `listHeight`,
`th`, `mh`, `bh`, `lh`, `bmpHeight`, `bmp`, and `yPos`. These establish a
scrolling/fading table viewer with a temporary backing bitmap, rather than a
single static rendering call.
