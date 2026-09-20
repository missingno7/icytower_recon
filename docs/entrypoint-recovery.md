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
