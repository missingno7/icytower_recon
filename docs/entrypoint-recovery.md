# `mangled_main` recovery map

`_mangled_main` spans `0x415f10..0x4166a2` (source lines 5761--5933). It is
the real program lifecycle dispatcher, not a synthetic link entrypoint.

The oracle loads the PNG library, installs the Allegro version check, sets the
executable directory and logfile, then initializes the game. Its menu loop
starts menu music, draws/fades the menu, dispatches menu callbacks, starts a
new game and calls `play`, then ends/fades the game. Other branches handle
credits, instructions, score viewing, replay selection, profile creation and
option synchronization. Every normal exit uninitializes the game and calls
`allegro_exit`; failure paths log and call `exit`.

The source also recovers the oracle's entry prefix through the `init_game`
call at `0x41606f`: it attempts to load `exchndl.dll`, performs the Allegro
version check via `allegro_init`, registers PNG support, derives and enters the
`data` directory in the typed `working_directory[1024]` buffer, writes the
version `1.5.1` log header, and recognizes the `-check` argument as the
existing `itrcheck` switch. Its failed-initialization branch now preserves the
conditional alert, cleanup, and return. The source dispatcher now enters the
typed `main_menu` with `main_menu_callback`, preserving the observed
`must_fade` state and the action branches for both new-game codes, scores,
instructions, replay selection, and credits. The new-game branch clears a
pending replay, handles the `play` retry result, and preserves the decoded
menu-select sound; the replay branch owns its selector result and rebuilds
the menu before its 32-step fade-in.

The startup sequence at `0x41650e..0x416544` now has a directly decoded,
source-level recovery. After successful game initialization it calls
`init_scroller(&greeting_scroller, data[54].dat, scroller_greetings, 640, 30,
-1)`. The datafile offset is `0x360`, which is record 54 in the 16-byte
`DATAFILE` array; the other five arguments resolve to the typed persistent
objects and constants. This establishes the main-menu greeting state before
menu music starts. `_mangled_main` remains `DIFFER`: the isolated TDM-2
candidate is 1,644 bytes against the oracle's 1,938 bytes. The recovered
setup now initializes the menu parameter assets and resets the typed main
menu. It also handles the `-check` replay/ad path and the first-run
`timesStarted == 1 && lastProfile == "guest"` profile-creation transition.
Exceptional exit handling and exact compiler structure still require recovery.
