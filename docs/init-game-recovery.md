# `init_game` recovery map

`init_game` is the 5,788-byte main-CU initializer at `0x40e7dc`. The oracle
orders password/network setup, controls/config/high-score loading, display and
datafile setup, display callbacks, timer/input/sound/joystick installation,
and replay/profile discovery. Progress rendering is interleaved with these
setup stages through `draw_progress_bar`.

Its source body must preserve load/error cleanup and this ordering; a reduced
initializer would not establish the game state used by the real lifecycle.

The current source candidate is a 573-byte `DIFFER` body. It fixes the DWARF
interface to `init_game(argc, argv)`, resets packfile and application state,
processes display mode arguments, initializes Allegro's graphics, timer,
input, joystick, and audio subsystems, loads the datafile, and allocates the
swap buffer. It is sufficient for the independent linker to resolve
`init_game`; the remaining 5,215 bytes cover the original network,
configuration, profile, resource-loader, and staged progress work.

The verified base resource is `data/data.dat`, loaded with the manifest's
`CHEESE` packfile password. The candidate resets the password at entry, then
sets this password immediately before loading that datafile.

DWARF names the original inputs and setup locals: `argc`, `argv`, `fp`,
`black`, `i`, `title`, `tmpHandle`, `wsaData`, `wVersionRequested`,
`cfgfilename`, `check`, `checkFile`, `loader`, `fldLogo`, and `whiteColor`.
They anchor the configuration, resource-loader, network, profile, and startup
presentation portions of the source body.
