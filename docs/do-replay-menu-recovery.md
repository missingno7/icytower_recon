# `do_replay_menu` recovery map

`do_replay_menu` spans `0x410f98..0x4119fd` (2,661 bytes) in `main.c`. It is
an `int`-returning routine declared at source line 5474. DWARF identifies its
three named locals: `ret` (line 5475), `play_again` (line 5476), and
`isGuest` (line 5477).

The current source has the recovered `replay_menu` data and its exact
`replay_menu_callback`, but this owner routine remains missing. Its recovery
must keep the callback-driven replay menu lifecycle and the guest-profile and
play-again branches in source; neither may be replaced by a synthetic menu
return path.

The oracle dispatches `handle_menu` returns `e`, `|`, and `{` to Play Again,
Watch Replay, and Save Replay. Watch Replay fades out, formats the selected
replay path, calls `run_demo`, and returns to the menu. Save Replay prompts
for and sanitizes a filename, replaces its extension, rejects existing paths,
then calls `save_replay`. The load path destroys any prior replay, calls
`load_replay`, and rejects a checksum mismatch before returning to the menu.
These calls and their failure alerts define the required source control flow.

At entry, the oracle compares `profile->handle` with `"guest"`, logs the
menu transition, initializes `play_again` to zero and `ret` to `-1`, then
calls `handle_menu(replay_menu, &menu_params, &ctrl, swap_screen,
replay_menu_callback, 180, 160, 0)`. The outer loop ends when the close button
is set or the menu returns `l`; `e` sets `play_again` before exiting.

The source candidate now contains the full modal save/load flow recovered from
the oracle: three 512-byte editor fields, the named-profile prefill and guest
owner prompt, filename normalization, metadata copy, temporary-replay reload,
checksum gate, overwrite confirmation, and save-result alerts.  It remains
`DIFFER` at 2,146 bytes against the oracle's 2,661-byte body: the remaining
gap is source-shape and control-flow fidelity, not an omitted persistence
subsystem.  The isolated `-O2` object compiled successfully and the complete
independent recovered-game link succeeded after this update.

The save tail copies the selected owner name into replay metadata with a
30-byte `strncpy`, copies the optional comment, derives the filename with
`replace_extension`, rejects an existing full path unless the user confirms
overwrite, then calls `save_replay(replay_directory, filename, demo,
demo->size + 2, 1)`.  Its success and failure branches return through modal
alerts before rejoining the replay menu.

The persistence object is the global `demo`; the load-validation branch checks
the replay checksum against global `uberChecksum` before accepting it.

DWARF line mapping places the save/load UI and its alert outcomes at source
lines 5508--5636, following the outer dispatch at line 5474.
