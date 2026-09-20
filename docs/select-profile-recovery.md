# `select_profile` recovery map

`select_profile` spans `0x41acc0..0x41b8be` (3,070 bytes) in `profile.c`,
source lines 705--867. DWARF records the four arguments as the current
profile, a packed array of 32-byte profile names, the profile count, and the
shared control object. Its named locals are `selectedProfile`, `kp`, `done`,
`old_font`, `profileIndex`, `offset`, `page_size`, `ctrl_wait`, `pageY`,
`targetY`, and `bgbmp`.

The routine swaps datafile font record 54 for record 55 while it runs,
snapshots the 640x480 screen, clears keyboard input, and renders the existing
`draw_profile_selector` panel with a 17-row (`page_size`) viewport at
`(16,140)`. It eases the panel from `pageY=500` to target `50`, then reverses
it to 510 before destroying the snapshot and restoring the former font.

The control loop polls with joystick-only mode, checks window close and its
own `done` flag, and applies a 20-frame `ctrl_wait` debounce. Down/up update
the selected index and keep the offset inside the 17-row window. Control fire
is converted to Enter; up/down are converted to the historical keyboard
scan codes so one keyboard dispatcher handles both inputs.

Dispatcher actions recovered from the oracle are: Down and Up; Delete, which
protects the guest/current profile and confirms before `delete_profile` then
`rebuild_profile_list`; Enter, which creates a guest profile when selected or
loads the selected profile; and Escape/close, which exits. Create displays a
modal name field, normalizes bad characters to `_`, calls `create_profile`,
then presents success or failure alerts. Load failure presents the broken
profile alert. The selected or newly-created allocation becomes the return
value after exit animation.

The current `profile.c` source implements these paths and resolves
`select_profile` in the ordinary reconstructed link. The pinned-toolchain
candidate is `DIFFER` at 2,626 bytes against the 3,070-byte oracle, so it is
an independently compiled partial recovery rather than a missing function.
