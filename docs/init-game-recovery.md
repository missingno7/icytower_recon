# `init_game` recovery map

`init_game` is the 5,788-byte main-CU initializer at `0x40e7dc`. The oracle
orders password/network setup, controls/config/high-score loading, display and
datafile setup, display callbacks, timer/input/sound/joystick installation,
and replay/profile discovery. Progress rendering is interleaved with these
setup stages through `draw_progress_bar`.

Its source body must preserve load/error cleanup and this ordering; a reduced
initializer would not establish the game state used by the real lifecycle.

DWARF names the original inputs and setup locals: `argc`, `argv`, `fp`,
`black`, `i`, `title`, `tmpHandle`, `wsaData`, `wVersionRequested`,
`cfgfilename`, `check`, `checkFile`, `loader`, `fldLogo`, and `whiteColor`.
They anchor the configuration, resource-loader, network, profile, and startup
presentation portions of the source body.
