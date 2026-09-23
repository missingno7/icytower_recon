# `new_game` recovery

`new_game` is reconstructed in `src/main.c` from the original function at
`0x40dc9c` (1,139 bytes, DWARF declaration line 2871). Its only named local
is `i`; the compiler also records inlined `new_srand` at source line 2878 and
`is_custom_replay` at line 2914.

The recovered source resets session and recording state, derives replay
settings for either an existing replay or a new recording, seeds both random
streams, clears the map and game statistics, adds the first 30 floors,
initializes the active player, and loads the selected custom character. The
literal messages and direct game API targets come from the original code and
read-only data.

The current TDM 4.4.1 `-O2` candidate is 1,135 bytes versus the original
1,139 and remains `DIFFER`. Original offsets 67–117 clear `bg_stripe_ids[4]`
through `[0]`, not the five `cmdline` fields the earlier candidate cleared.
That correction removed the named-data mismatches and moved the first
difference from offset 69 to 127. Original offsets 142–179 cap
`best_floor` before dividing and write `floors.value` once after selecting
the smaller of that cap and `start_floor`; the source now follows that shape.
The first remaining instruction difference loads `itrcheck` into `esi`
instead of the original `eax`, shifting the following block by one byte.
The earlier `if (!demo) return 0` immediately after `create_replay(64000)`
was also removed: the original proceeds directly to copy the profile name,
with no such check at that point.
The player writes now reload `ply[player_id]` after `reset_player`, as the
original does at offsets 442–532, rather than carrying an invented local
pointer. The `gameData` allocation failure path logs and then proceeds to
the replay assignment in the original; the earlier candidate's `return 0`
was unsupported and has been removed.
The fresh whole-CU verifier retains 58/82 main functions exact with no
regressions. `python tools/recovered_game_link.py --diagnostic` links this
incomplete source for dependency analysis; ordinary recovered-game linking
is gated because other active bodies are synthetic or unmatched.
