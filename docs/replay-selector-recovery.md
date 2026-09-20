# Replay selector recovery map

`draw_replay_selector` spans `0x41bdb8..0x41cc46` (3,726 bytes), source line
460. Its named state covers the replay/file list, selection and offset,
viewport geometry, current filename, colors, view percentage/offset,
directory visibility, selected version, and custom-replay flag.

`replay_selector` spans `0x41c9a8..0x41d4c5` (2,845 bytes), source line 701.
It owns controller input, path, replay result, current file, paging/debounce,
rename eligibility, update state, and slide animation bitmap/coordinates.
Both remain missing and must be recovered as a renderer/controller pair.
