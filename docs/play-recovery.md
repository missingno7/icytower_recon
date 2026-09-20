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

Its oracle call graph fixes the update order: `handle_player_input`,
`update_player`, `update_particle`, `add_floor`, combo/reward updates, then
one of the five collision handlers. Rendering calls `draw_frame` and
`blit_to_screen`; the terminal paths draw results, update high scores, save
profiles and replays, stop music/voices, and either re-enter the game or
return to the menu. Pause, screenshot, replay-menu, and scroller paths are
also owned by this function and must remain in the recovered source.

The prologue and first steady-state iteration have source anchors from the
oracle: line 3485 enters the play setup, lines 3493--3530 establish timing,
and lines 3553--3559 start samples and game music. The first update phase is
anchored at lines 3702--3711 (input/player/particles), 3789 (floor advance),
3842--3851 (reward/combo), and 3983--4100 (sound and jump-sequence state).
