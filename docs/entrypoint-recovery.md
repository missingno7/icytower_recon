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

The startup sequence at `0x41650e..0x416544` now has a directly decoded,
source-level recovery. After successful game initialization it calls
`init_scroller(&greeting_scroller, data[54].dat, scroller_greetings, 640, 30,
-1)`. The datafile offset is `0x360`, which is record 54 in the 16-byte
`DATAFILE` array; the other five arguments resolve to the typed persistent
objects and constants. This establishes the main-menu greeting state before
menu music starts. `_mangled_main` remains `DIFFER`: the surrounding menu
dispatch and its error paths have not yet been recovered.
