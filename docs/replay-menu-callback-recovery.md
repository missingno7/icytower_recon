# `replay_menu_callback` recovery

`replay_menu_callback` spans `0x4073f8..0x4076c0` (712 bytes) in `main.c`.
The recovered source candidate is a `FUNCTION_MATCH`: it has the same 712-byte
extent, its masked text matches, and all relocation targets resolve to the
oracle values.

The callback draws alternating vertical and horizontal zero-color stripes into
`swap_screen`, overlays datafile image 87 at `(120, 140)`, and returns when
the summary message is empty. Otherwise it advances `summary_scroller`, draws
the translucent three-band top overlay, renders the two scroller passes, and
restarts the scroller after its terminal pass. The source follows DWARF lines
5337--5359 and preserves the observed call and branch order.
