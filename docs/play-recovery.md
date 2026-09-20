# `play` recovery map

`play` is the main-CU game loop at `0x411a00..0x415e0c`, a 17,420-byte
function declared at source line 3405. It is the final ordinary game-flow
linker frontier after profile selection, input editing, and presentation
recovery.

DWARF records its gameplay state directly: `playing`, `old_map_pos`, `level`,
`diff`, `quit`, scrolling state (`scroll_acc`, `scroll`, `max_scroll`), speed
state, sampled-audio controls, `game_over`, falling/shake/flash state, step
and next-floor counters, retry state, camera coordinates, combo statistics,
rank state, replay controls, and clock/query-performance/time instrumentation.

Recovery must retain the full loop and its game, replay, profile, audio,
timing, and presentation transitions. A reduced loop would only hide the
real boundary and is not an acceptable resolution for this function.
