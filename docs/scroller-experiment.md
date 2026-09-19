# scroller.c recovery

`scroll_scroller`, `restart_scroller`, and `init_scroller` match their complete
14-byte, 28-byte, and 200-byte bodies at -O2. DWARF establishes the 2,084-byte
`Tscroller` layout: its horizontal flag, text and font pointers, dimensions,
offset, row count, horizontal text length, and 512 line pointers.

`draw_scroller` has the historical 396-byte body size and matches its bounds
checks, clipping, vertical row loop, signed width shift, and all resolved
calls. It remains DIFFER at the first vertical `set_clip_rect` argument setup:
the candidate uses equivalent registers in a different order. This is not a
complete-text, object, or CU claim. See
`docs/experiments/game-scroller-O2.json` for the full comparison record.
