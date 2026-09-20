# `init_game` recovery map

`init_game` is the 5,788-byte main-CU initializer at `0x40e7dc`. The oracle
orders password/network setup, controls/config/high-score loading, display and
datafile setup, display callbacks, timer/input/sound/joystick installation,
and replay/profile discovery. Progress rendering is interleaved with these
setup stages through `draw_progress_bar`.

Its source body must preserve load/error cleanup and this ordering; a reduced
initializer would not establish the game state used by the real lifecycle.

The current source candidate is a 4,169-byte `DIFFER` body. It fixes the DWARF
interface to `init_game(argc, argv)`, resets packfile and application state,
creates and resets the 15 original high-score tables, loads or resets options
and each persisted table, increments the ordinary-run counter, processes the
original `-check` replay-validation path and five gameplay command switches,
then initializes Allegro's graphics, timer, input,
joystick, and audio subsystems, installs the display-focus and close callbacks,
seeds runtime randomness, establishes the original joystick defaults, loads
the main and SFX datafiles, assigns the exact decoded Ogg sound-record mapping
to the menu/game sound slots, allocates the active player, ensures the profile
directory exists, and allocates the swap buffer,
and recovers the profile/character discovery path. It also restores the
136-byte `Tmenu_selection` ABI: an integer value and size followed by 32
string pointers. The initializer allocates the original eye-candy, speed,
floor-size, and gravity captions in their observed storage order, starts FLD
advertisement discovery, and carries the loaded custom-game settings into
their menu controls. It recovers the original joystick configuration branch:
when a joystick is installed it loads `gamepad.txt` and maps `up`, `down`,
`left`, `right`, and `b1` through `b32`; otherwise it installs the original
default controls. It rebuilds the profile
list, loads the remembered profile with the guest fallback/create sequence,
synchronizes profile options, and propagates character-loading failure.
The recovered final profile stage also computes the start-floor selector from
the profile's `best_floor` and persisted `start_floor`, limiting its maximum
to nine tiers exactly as the oracle does.
Before loading packed graphics, the candidate now restores the oracle's full
Allegro color-conversion mask (`0x00ffffff`).
The pre-configuration order now matches the oracle: it allocates all menu
selection captions and starts FLD discovery before argument parsing; replay
validation then precedes high-score table allocation, control initialization,
and config-file loading.
It is sufficient for the independent linker to resolve `init_game`; the
remaining 1,619 bytes cover the original graphics fallback,
resource-loader,
and staged progress work.

The loader presentation is now recovered from `0x40edfe..0x40eede`: it prints
the standard wait message, disables color conversion, opens
`data/loading.dat` under the `(c) Free Lunch Design` password, resets that
password, selects the datafile's first-entry palette, clears the display
white, centers the second-entry FLD logo at `(320,200)`, and releases the
temporary datafile. The verified base resource is `data/data.dat`, loaded
with the manifest's `CHEESE` packfile password. The candidate resets the
password at entry, then sets this password immediately before loading that
datafile.

The recovered startup path also now carries the original order through the
first resource stages: it initializes controls before graphics, installs the
focus/close callbacks and random seed after the temporary loader, presents a
progress step before each timer, keyboard, sound, joystick, swap-buffer, and
primary-data stage, and resets the main datafile password before profile
discovery. It loads SFX only after the player, profile, and character stages,
following palette selection; the SFX password is cleared before the recovered
Ogg sample mapping runs.

After SFX unload, the initializer repeats the persisted music/sound slider,
eye-candy, gravity, floor-size, and scroll-speed values in the original
sequence, then derives the capped start-floor selector from the profile. This
keeps the final menu widget setup at `0x40fc7e..0x40fce4`, after the resource
stages that the oracle uses.

The initializer tail now includes the original loading cadence. It adds the
two final progress steps, waits until input or the 150-tick cutoff while
advancing progress once per changed ten-tick boundary, seeds `new_rand` from
`rand() % 2367`, fades and clears the display, clears input, marks `init_ok`,
and returns `-1` as the successful startup result.

`-check` is now parsed in the initializer's argument path. It loads the
specified replay before configuration and graphics setup, records an invalid
replay through `dropped_file_is_not_a_replay`, and enables `itrcheck` only
after a successful load. The candidate no longer accepts non-oracle
`-windowed` or `-fullscreen` switches, and it no longer treats every ordinary
non-option argument as a replay.

The pre-graphics network setup is recovered from `0x40e811..0x40e87a`. It
formats the `Icy Tower v1.5.1` window title, requests Winsock 2.2 through the
real `WSAStartup@8` import, and logs both setup and too-old-version failures
without aborting startup. The source keeps the historical 400-byte `WSADATA`
ABI locally because the period Allegro headers conflict with modern Winsock
headers in this compiler configuration.

Graphics setup now follows the observed split path: a windowed request tries
`640x480` windowed mode, retries fullscreen after a failure, and switches to
text mode with the original error message only if the retry fails. A fullscreen
request fails directly to that same text-mode error. On success it verifies
`screen`, installs the mouse and hardware hand cursor, and exposes the cursor
for windowed mode before rendering the loader screen.

The loader, swap-buffer, primary-datafile, and player-allocation failure paths
now all switch to text mode and show their individual oracle strings before
returning failure. These restore four independent exits that previously fell
through to bare returns.

The profile-directory, guest-profile, and character-discovery failures now
also switch to text mode with their oracle diagnostics, including the profile
directory path and the multiline character installation guidance.

DWARF names the original inputs and setup locals: `argc`, `argv`, `fp`,
`black`, `i`, `title`, `tmpHandle`, `wsaData`, `wVersionRequested`,
`cfgfilename`, `check`, `checkFile`, `loader`, `fldLogo`, and `whiteColor`.
They anchor the configuration, resource-loader, network, profile, and startup
presentation portions of the source body.
