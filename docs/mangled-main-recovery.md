# `_mangled_main` recovery map

`_mangled_main` is the missing historical game entrypoint in `main.c`.  The
original is at `0x415f10`, has a 1,938-byte DWARF extent, and is the first
unresolved symbol in the ordinary recovered-game link.  This note records
oracle-derived structure only; it is not source input to normal compilation.

DWARF declares `argc`, `argv`, `i`, `ret`, `must_fade`, `full_path[1024]`,
`f`, `menu_x`, `menu_y`, `hDebugLibrary`, `should_chdir`, and
`logfilename[256]`.  Its `0x52c` stack allocation agrees with those two
buffers and saved registers.

The recovered control flow has five stages:

1. Load `exchndl.dll`, install Allegro's version check, register PNG support,
   derive and change to the executable directory, and create the versioned
   log file.
2. Scan command-line arguments for the working-directory option, log the
   argument list and directory, then call `init_game`.
3. On failed initialization, log the error, optionally display the failure
   alert, run `uninit_game`, and return failure. On success, either run a
   preselected replay or start menu music and enter the menu loop.
4. Initialize the scroller and menu controls when a profile must be created;
   otherwise draw/fade the menu and dispatch new-game, scores, instructions,
   replay-selection, and credits actions. New-game dispatch calls `new_game`,
   `play`, and `end_game` with the corresponding fade and menu-music changes.
5. On normal completion, stop menu music, call `uninit_game`, log completion,
   and return zero. The exceptional replay exit logs, calls `allegro_exit`,
   then calls `exit(0)`.

The direct game callees are `init_game`, `run_demo`, `load_new_ad_image`,
`startMenuMusic`, `stopMenuMusic`, `fadeIn`, `fadeOut`, `main_menu_callback`,
`draw_menu`, `handle_menu`, `new_game`, `play`, `end_game`, `show_credits`,
`show_instructions`, `view_scores`, `replay_selector`, `force_create_profile`,
`syncOptionsFromProfile`, `init_scroller`, `init_control`, `reset_menu`, and
`uninit_game`.  Their recovery order follows the ordinary linker frontier;
no stub entrypoint is acceptable.

## Menu-dispatch constraints

The normal menu loop begins after `clear_keybuf`, with `must_fade` initially
true. It takes its presentation bitmap from `data[?]` through the established
main-menu data path, installs the profile-derived menu coordinates, and uses
the typed `main_menu` and `menu_params` globals rather than a private menu
instance. The oracle dispatch values are `0x65` (new game), `0x85` (the
alternate new-game route), `0x69` (scores), `0x68` (instructions), `0x7a`
(replay selection), and `0x6b` (return to the menu loop). Any other result
falls through the timer-rest and redraw path.

Both new-game values set the observed replay-mode flag according to whether
the return was `0x65`, fade out, stop menu music, destroy and clear a pending
replay, then call `new_game`. On a successful creation they call `play`,
`end_game`, and fade out; a nonzero `play` result retries the new-game branch.
On a failed creation the entrypoint restores menu music when it exists and
returns to the menu loop. Scores draw the five oracle labels, instructions
fade out before invoking their screen, and replay selection runs the selected
replay before rebuilding and fading in the menu.

When no active profile exists, the entrypoint calls `init_scroller`, copies
the menu assets and state from the loaded data record, initializes controls,
resets the menu, forces profile creation, synchronizes its options, and then
enters the same dispatch loop. A special command-line mode follows the same
menu setup after a case-insensitive selector check. These edges are from the
complete `0x416109..0x416652` oracle range and must remain source-level calls,
not an injected control-flow replacement.

The supporting `menu_params` object is emitted from its DWARF layout as a
60-byte main-CU `.bss` record. The initialized main-CU menu objects have also
been recovered: `ctrl_menu[6]`, `snd_menu[3]`, `gfx_menu[5]`, `game_menu[1]`,
`profile_menu[3]`, `opt_menu[4]`, `custom_menu[5]`, `play_menu[3]`,
`main_menu[7]`, and `replay_menu[5]`. Their declaration sizes come from DWARF
and their captions, navigation codes, flags, and data links come from the
corresponding `.data` records at `0x4bc1c0..0x4bda84`. Each data link is a C
symbolic address, so normal COFF relocation owns the final pointer value.

The candidate TDM-2 object matches every table byte after masking only the
final four-byte `data` relocation of each 148-byte record. This includes the
main menu's links to the play, profile, and options tables. It must not be
replaced with a zeroed table or a pre-relocated address blob.

Reproduce the current dependency measurement with:

```powershell
python tools/recovered_game_link.py
```

It records `_mangled_main` first in
`build/recovered-game/tdm-2/link.json`.  A complete source implementation is
still required before this can become an independently linkable game.
