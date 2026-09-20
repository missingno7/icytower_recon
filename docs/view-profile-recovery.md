# `view_profile` recovery map

`view_profile` is the unresolved `profile.c` routine at
`0x419aec..0x41a3b5` (2,249 bytes), declared at source line 538 with one
profile argument. Its oracle prologue drains the shared game control, clears
the keyboard buffer, creates a 640x480 presentation bitmap, and allocates a
second content bitmap sized from datafile record 86 plus a 50-pixel border.

The content construction calls the recovered page helpers in this order:
`profile_data_page_general`, `profile_data_page_basic`, and
`profile_data_page_advanced`; it also calls `draw_buffer` for each page and
`set_next_rank_message` for the rank panel. The source-level loop must retain
those calls rather than duplicate their string layouts.

DWARF establishes the three generated page pointers (`data_basic`,
`data_advanced`, and `data_general`), `pageY`, `targetY`, `bg`, and `bmp`.
The profile rank comparisons use the existing rank tables and profile fields
at offsets `0x4c`, `0x50`, `0x58`, and `0x88`. The unfinished tail is the
scroll/input loop, page blits, and freeing of all three generated buffers and
both bitmaps; recover it before emitting the C body.
