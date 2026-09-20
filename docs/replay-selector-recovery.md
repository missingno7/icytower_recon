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

`draw_replay_selector` has eight typed inputs in the oracle order: `bmp`,
`rep`, `file_list`, `selection`, `offset`, `max_posts`, `x`, and `y`. Its
DWARF locals establish the panel dimensions, font height, filename, two gray
colors, view ratio and offset, directory visibility, selected replay version,
and custom-replay indicator. The opening renderer phase computes `fh` from
the active font, creates the 25-gray foreground and 85-gray middle color,
clamps the visible-list ratio to one, and draws the `data[86]` panel with the
historical translucent layout. The same decoded region sets list/panel geometry
from `x` and `y`, leaving the later text rows, replay details, version state,
and custom indicator to the remaining renderer phases.

The remaining renderer call map fixes those phases. Lines 487--509 draw the
clipped file-list rows and selected filename; the latter obtains its basename
through `get_filename`. Lines 525--543 restore the clip, classify a present
preview with `is_custom_replay`, and compose the clipped replay-detail text.
Lines 551--569 render the labelled score, floor, combo, and replay fields with
left and right text helpers. The final phase invokes the panel's inline sprite
and rectangle operations, selects a version/detail presentation, and renders
the remaining formatted labels. Every clip transition, text helper, and
custom-replay call is therefore anchored to a source line and direct oracle
transfer for the future complete body.
