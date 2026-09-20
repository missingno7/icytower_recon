# Archived recovery narrative

Historical README narrative retained during the production-line audit. This is not
current status; links in the preserved text were relative to the repository root.

Historical recovery summary (refer to generated current status for live counts):

- Fresh PE/COFF census, 148 DWARF CUs, 130,019 DIEs, 39,981 line rows,
  32,978 type DIEs, complete source-file tables, location/range lists, and
  no unresolved abstract-origin/specification chains.
- All 25 historical game source filenames generated; 18 GAME, 5
  VENDORED_UPSTREAM (two exact revisions unresolved), and 2 AMBIGUOUS.
  Three loadpng source files are populated verbatim from Allegro 4.4.1.
- Complete game beta.c, control.c and timer.c: all 25 functions and their entire
  2043-byte text contributions match, including padding and resolved relocations.
- custom.c has all ten source implementations, with nine exact function bodies
  at -O2. `load_character_bmp` still differs; its reconstructed dependencies
  link in a separate synthetic audio PE but it is not naturally integrated yet.
- directories.c: all seven functions and the complete 307-byte text contribution
  match, and the CU is included in the synthetic integration build.
- stars.c: all three functions and the complete 643-byte text contribution
  match, including the historical x87 star-scrolling arithmetic.
- particle.c: all three functions and the complete 304-byte text contribution
  match; its recovered `new_rand` dependency resolves in the separate synthetic
  custom-audio PE.
- main.c: `get_version_str`, `get_demo`, `get_controls`, `new_rand`,
  `new_srand`, `ok_to_play`, the three focus/close callbacks, and
  `is_custom_replay`, `show_name`, `getSampleFromOggDatafile`, and two
  progress callbacks match at -O2. `datafile_callback_slow` retains its
  original 33-byte counter body but is not exact while partial-CU BSS-static
  ordering remains unresolved. `syncProfileFromOptions`, menu-music
  start/stop, and the two menu-sound wrappers also match; the other main
  functions remain explicit partial-CU work. `replaceBadCharacters` also
  matches its complete signed string-filtering loop, and `pwd_garble_string`
  matches its in-place XOR transform. `line_intersect` matches its full
  302-byte x87 segment-intersection body, and the historical Allegro
  `END_OF_MAIN()` macro emits the exact 50-byte `WinMain` wrapper.
  `set_current_avatar` also matches its complete 96-byte profile-avatar scan,
  `for_each_directory` matches its 109-byte Allegro enumeration wrapper, and
  `run_demo` and `uninit_game` match their complete 159- and 646-byte bodies.
  `play_sound` plus its 141-byte `play_jump_sound` threshold selector are
  recovered source bodies whose direct same-CU call displacements remain
  layout-dependent in this partial build.
- scroller.c: `scroll_scroller`, `restart_scroller`, and `init_scroller` match
  at -O2; the 396-byte `draw_scroller` candidate has one remaining
  argument-register difference.
- map.c: `reset_map`, `is_solid`, and `get_level` match at -O2. The
  107-byte `getFloorData` candidate and unresolved `add_floor` remain partial.
- csv.c: all six functions and its 680-byte text contribution match. Its
  upstream ownership remains ambiguous and separate from game-owned totals.
  The natural beta/control/csv address-and-extent prefix spans 2576 bytes.
- httpget.c: the recovery-owned partial object has exact `getSocketError`,
  `HTTPRequest`, `HTTPHead`, and `HTTPGet` bodies. Its ordinary-link frontier
  now begins at `SplitURL` and `HTTPFetchInternal` rather than the public
  request entry points.
- loadpng.c, savepng.c, and regpng.c: all fifteen functions and their complete
  text contributions match at `-O2`. The ordinary recovered-game link now
  resolves `load_png` through a runtime-derived `libpng3.dll` import candidate;
  the original import archive has not been recovered.
- All 114 historical Allegro core CUs build into a static library. The recovered
  game CUs link against it with a synthetic main and no fallback code.
- Allegro 4.4.1 timer.c and color.c: complete text contributions match at
  -O2, totaling 11,752 bytes; initialized data is checked separately.
- Modified logg.c: all 18 emitted functions and its complete 2061-byte text
  contribution match; the reconstructed memory extension is kept separately
  from the locked upstream source. All 22 Xiph CUs build into candidate archives
  and link with logg/Allegro in a separate, unexecuted synthetic audio PE.
- A real historical CRT link produces the original entry RVA 0x1110 and
  eight original startup symbol addresses with TDM-2. The first 792 bytes have matching
  function starts and spans. It is not a game layout or whole-byte match.
- Twenty-two validation tests include wrong relocation targets, altered code and
  padding, unknown relocation kinds, origin chains, and independent builds.

See [machine-readable progress](docs/progress.json),
[blockers](docs/blockers.json), [proof levels](docs/proof-levels.md), and
[the timer experiment](docs/timer-experiment.md),
[control recovery](docs/control-experiment.md), [beta recovery](docs/beta-experiment.md),
[custom recovery](docs/custom-experiment.md), and
[runtime selection and integration](docs/runtime-selection.md). Measurements and full
symbol/relocation records are retained in [docs/experiments](docs/experiments).

