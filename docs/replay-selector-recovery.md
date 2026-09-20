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
