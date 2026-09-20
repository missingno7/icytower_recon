# Replay selector recovery map

`draw_replay_selector` spans `0x41be58..0x41cce6` (3,726 bytes), source line
460. Its named state covers the replay/file list, selection and offset,
viewport geometry, current filename, colors, view percentage/offset,
directory visibility, selected version, and custom-replay flag.

`replay_selector` spans `0x41d258..0x41dd75` (2,845 bytes), source line 701.
It owns controller input, path, replay result, current file, paging/debounce,
rename eligibility, update state, and slide animation bitmap/coordinates.
Both remain missing and must be recovered as a renderer/controller pair.

The controller setup at `0x41d258..0x41d364` is now directly decoded. It
saves the current font as `old_font`, creates `bg` at the active display
dimensions, snapshots the display into it, changes the font to `data[54]`,
and derives `page_size` as `270 / text_height(data[54])`. It clears the key
buffer, starts the slide position at 500, sets the page-update flag, zeroes the
list offset, replay pointer, current-file tracking, and completion state, and
starts the controller debounce at 1000. The first loop refreshes the selected
replay through `load_replay`, polls the supplied control object, and gates new
input on that debounce. These are source-level prerequisites for the later
renderer call and animated presentation loop.

The controller's remaining direct branches are now mapped. Its keyboard jump
table feeds a single redraw loop; `is_up`, `is_down`, and `is_fire` translate
to the same keyboard actions through `simulate_keypress`. Navigation maintains
the selected file and viewport offset, with move/select sounds. The action
branches include returning a loaded replay, cancelling and destroying a
preview, confirming and deleting the selected replay, choosing a directory or
file through `file_select_ex`, canonicalizing the resulting path, and changing
the four persisted sort modes. Each successful path requests a file-list
refresh and preview reload. The presentation loop snapshots the background,
uses a translucent slide from 500 toward its target, calls
`draw_replay_selector`, then blits to screen. Its exit releases every
file-list allocation, destroys the presentation bitmap, restores `old_font`,
and returns the selected replay pointer.
