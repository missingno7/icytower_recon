# `draw_menu` rendering evidence

Historical `draw_menu` is at `0x0041767c` (1,118 bytes). DWARF identifies the
parameters as `BITMAP *bmp`, `Tmenu *m`, `Tmenu_params *mp`, `x`, `y`, and
`step_in`. The pinned Allegro headers confirm the two required ABI layouts:
`FONT` is `{ data, height, vtable }` (12 bytes) and `DATAFILE` is 16 bytes.

The original renders each 148-byte menu entry after `build_menu_string`, uses
`mp->font` and its vtable draw callbacks, steps entries by `font_height - 12`,
and branches on flags `1`, `16`, `32`, and `64` for selection and asset
rendering. `mp->bullet` is at offset `0x2c`; `mp->data` and `mp->fo` at
offsets `0x34` and `0x38` select the three slider assets. These facts are
derived from the original only as an oracle and the pinned historical headers.
