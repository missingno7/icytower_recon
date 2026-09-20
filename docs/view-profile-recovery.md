# `view_profile` recovery map

`view_profile` is the partially reconstructed `profile.c` routine at
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
at offsets `0x4c`, `0x50`, `0x58`, and `0x88`.

The current source implements the observed page construction, rank badge and
next-rank panel, input debounce, snapshot background, 500-to-15 entry
animation, 15-to-500 exit animation, presentation blits, and every observed
release. The recovered link reaches the next genuine functions
(`_mangled_main`, `select_profile`, `play`, and `blit_to_screen`).

The pinned-toolchain candidate is `DIFFER` at 1,802 bytes. The remaining 447
bytes cover unrecovered layout and presentation details; this does not claim
byte-level equality with the 2,249-byte oracle.
