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
