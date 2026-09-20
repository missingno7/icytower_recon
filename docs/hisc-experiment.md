# Partial `hisc.c` experiment

`destroy_hisc_table`, `make_hisc_table`, `reset_hisc_table`,
`generate_checksum`, `qualify_hisc_table`, `sort_hisc_table`,
`save_hisc_table`, `load_hisc_table`, `enter_hisc_table`, and `draw_table` are
byte-exact at `-O2`.
`draw_table` uses the historical datafile fonts, optional header, zero-based
five-row scan, and displayed one-based rank.
The persistence wrappers serialize five 36-byte `Thisc_post` records, each
followed by its historical inlined checksum; loading validates all five and
returns the aggregate success flag. DWARF establishes the
`Thisc_table` layout as a 32-byte name followed by its five `posts` entries;
the recovered source preserves the allocation/failure paths, ordered `free`
calls, reset loop, checksum recurrence, score qualification, and insertion
sort.

`view_scores` remains a partial 2,498-byte candidate against the historical
2,552-byte body. DWARF declares `data` as `DATAFILE *`; the original's
`+0x420`, `+0x410`, and `+0x400` loads therefore select entries 66, 65, and
64, rather than doubled indices. The viewer also draws entries 9 and 6 at
`x = 626 - dark`, at y positions 380 and 40, after each overlay update.
Its interaction loop preserves the original `canDone` debounce: fire completes
immediately; F1, Enter, and K complete only after all three have been released.
`closeButtonClicked` is the outer-loop exit condition. The panel begins at the original
`pageY = 500`, eases toward zero while darkening toward 158, clamps its
scroll at `485 - panel_height` and zero, then slides back to 500 while clearing
the overlay before teardown. Each entry frame renders at the prior position
and alpha, then polls input, waits for the timer, and advances page position
for the next frame. Each easing calculation adds in double precision before
the result is truncated, matching the original x87 sequence. The original
text is used only as an oracle by
`build/experiments/tdm-2/game-hisc/O2`.
