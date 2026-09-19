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

Reproduce the current dependency measurement with:

```powershell
python tools/recovered_game_link.py
```

It records `_mangled_main` first in
`build/recovered-game/tdm-2/link.json`.  A complete source implementation is
still required before this can become an independently linkable game.
