# main.c helper recovery

`src/main.c` currently establishes forty-two exact historical functions while the remaining
main CU entities stay absent. `get_version_str`, `get_demo`, and
`get_controls` each match their complete 10-byte bodies at -O2. The version
accessor's anonymous `"1.5.1"` string relocation is resolved only by its
unique NUL-terminated bytes in the original read-only data; `get_demo` and
`get_controls` resolve their `demo` and `ctrl` globals by name.

Direct `E8` calls and `E9` tail jumps are resolved when they land exactly on a
candidate same-unit function with a unique historical identity. This proves
the callee independently of its layout-dependent relative operand; it does
not establish whole-CU layout or object equality.

`ok_to_play` returns the original constant `1`, while `switchedFromProgram`,
`switchedToProgram`, and `clickedCloseButton` exactly update the named
`hasFocus` and `closeButtonClicked` globals.

`is_custom_replay` matches its 66-byte predicate over the five recovered
`Treplay` settings fields: floor shrink, floor size, start speed, speed
increase, and gravity.

`show_name` matches its 36-byte Allegro-message wrapper. Its format string is
resolved by unique printable, NUL-terminated read-only bytes, allowing
embedded newlines and any direct `.rdata` pointer instruction form.

`getSampleFromOggDatafile` matches its complete
32-byte body at -O2, including the tail call to `logg_load_memory`: it passes
the DATAFILE entry's data pointer and byte count without a substitute layer.

`drawSlot` matches its complete 328-byte body at -O2. It renders the title, framed white slot, and colored text through the independently typed main-CU `data` global, using the historical font stored in `data[54].dat`.

The loading progress callbacks recover `datafile_callback` as the 12-byte
progress-bar tail call and `color_map_callback` as its 22-byte
every-sixteenth-entry form. `datafile_callback_slow` has the original 33-byte
counter-based body and is `CODEGEN_SIMILAR`: its private `p` counter is a
function-scoped DWARF static whose candidate BSS placement conflicts with the
independently observed ordering of other partial-CU statics. Its only relocation is
therefore not accepted as an exact match.

`syncProfileFromOptions` matches its 58-byte body, copying the four named
options settings (flash, jump hold, music volume, and sound volume) into the
current profile at their independently recovered DWARF offsets. `startMenuMusic`,
`stopMenuMusic`, `play_menu_select`, and `play_menu_move` match their 59-,
25-, 37-, and 37-byte bodies, respectively; each resolves its sample global
and call target by name.

`replaceBadCharacters` matches its 125-byte body. Its 63-byte local alphabet
and signed `strlen` loop bound come from DWARF and the original control flow;
the latter is required to preserve the historical signed comparison branch.

`pwd_garble_string` matches its complete 52-byte in-place XOR loop. The
independently recovered `len_i` local preserves the original signed loop bound.

`line_intersect` matches its complete 302-byte body. Its ten integer
parameters, two integer outputs, three float locals, and segment-endpoint
tests come from DWARF and x87 disassembly. The final `0.5f` conversion literal
is repeated in the original; the verifier establishes its address from the
unique preceding 12-byte read-only float-table neighbourhood, then derives the
literal's target from that independently established table position.

`end_game` has an exact 32-byte source body: it logs `" freeing custom data"`
and calls `destroy_custom_data` on the typed main-CU `custom` global.

`save_config` is exact at 154 bytes. It builds the 256-byte configuration
path, opens it in historical `"wp"` mode, saves options and all fifteen score
tables, closes the packed file, and logs the failure path when opening fails.

`change_profile` now recovers the profile-switch workflow. It persists an
existing profile after synchronizing options, opens the selector with the
typed profile list and controls, replaces the active allocation, records the
selected name in `options.lastProfile`, synchronizes the selected settings,
saves configuration, and rebuilds the profile list. The candidate has the
observed calls, fields, and 188-byte semantic path, but the compiler places
the null-profile setup in a 196-byte tail block instead of the original
fall-through block; it remains `DIFFER` pending a source-level explanation.

`run_demo` matches its complete 159-byte body. It conditionally replaces the
loaded replay, runs it through `new_game`, `play`, and `end_game`, and restores
the typed profile `start_floor` and floor-menu value after ordinary replay
execution. DWARF establishes the `file_name` parameter and `fo` local, while
the disassembly establishes the two `itrcheck` paths and the exact field
offsets; all external and direct same-CU transfer targets resolve by identity.

`add_profile` recovers the 195-byte profile-directory callback. It ignores dot
entries, builds the profile path in its DWARF-sized 1024-byte local buffer,
adds a valid handle to the typed 32-byte `Tavailable_profile` array, and
returns zero. Its executable instructions and named data and call targets are
identical; the `"%s%s"` format literal occurs three times in the original
read-only data and cannot be independently located in this partial CU, so the
verifier records it as `CODEGEN_SIMILAR` rather than exact.

`rebuild_profile_list` likewise recovers its full 198-byte profile-list reset:
it frees and clears the old array, adds the initial `"CREATE NEW PROFILE"`
handle, enumerates profile directories through `add_profile`, returns the
count, and optionally exposes the new array through its typed out-parameter.
Its code and all non-literal transfer targets match, while the initial handle
literal has two original read-only-data occurrences; it remains
`CODEGEN_SIMILAR` under the same proof policy.

`loadScrambled` reconstructs the complete 247-byte PNG decode bridge. It
loads the source into a heap buffer, XORs each twelve-byte group with the
historical password, writes the temporary `data/com/temp.dat`, loads it with
the typed PNG reader and palette, and deletes the temporary file. DWARF
establishes all ten locals and the disassembly fixes the password loop and
error paths. The bytecode and every named or uniquely resolved literal target
match, including the file modes after the beta-test literals establish their
candidate read-only-data neighbourhoods.

`check_beta_tester` recovers its full source behavior from the 254-byte
historical body. It reads and garbles the
eight-byte password, compares it against each typed 276-byte beta record,
sets the selected tester, and reports the historical missing-file and
no-match paths. Its 16-byte initializer contains an explicit second NUL;
that source detail is required for the historical ten-byte initialization
copy. The current candidate is 250 bytes: its only observed source-layout gap
is after the `fopen` failure branch, so it remains `DIFFER`. The combined
partial snapshot's literal neighbourhood remains reported by the generated
comparison inventory.

`check_characters` recovers the 345-byte character discovery and loading
workflow. It enumerates the base and optional custom directories, allocates
the DWARF-sized character records, invokes the typed loading callback, derives
each `ok` flag from its bitmap pointer, and chooses the current avatar. Its
instruction sequence and all named data, callbacks, and direct calls match;
the repeated `"Searching '%s'"` literal has no independent original
read-only-data position in this partial CU, so it remains `DIFFER`.

`load_character` recovers the 330-byte directory callback used by character
discovery. It validates the character directory and descriptor, loads the
character bitmap and metadata through the typed custom-CU API, logs the
outcome, preserves the static load counter, and restores Allegro's error
state while removing failed entries. The compiler retains the filename and
basename in the opposite registers and merges the success return path into a
315-byte candidate, so this evidence-backed source remains `DIFFER`.

`update_reward` recovers the inline fixed-point reward transition over the
typed `reward_time` and `reward_scale` globals. It adds 3277 above 60 ticks,
subtracts 6554 at nine ticks or below, and decrements the timer. The candidate
has the original operands and relocations but a 54-byte equivalent branch
layout rather than the original 55-byte layout, so it also remains `DIFFER`.

`myDeleteFile` recovers the 63-byte path/file deletion wrapper: it formats the
two input strings into a 2048-byte local buffer with `"%s%s"`, then calls
Allegro `delete_file`. Its non-relocation code and both call relocations match.
The short format string is duplicated in original read-only data and the
partial CU cannot independently establish its table position, so it is
`CODEGEN_SIMILAR` and receives no exact-function credit.

`WinMain` matches its full 50-byte entry-point wrapper. The historical
Allegro `END_OF_MAIN()` macro emits this wrapper, which passes the address of
the still-unimplemented `_mangled_main` symbol to `__WinMain`. Its two
relocations resolve by their named symbols; the forward declaration comes from
DWARF and supplies no missing game-function body.

`set_current_avatar` matches its full 96-byte character-selection loop. It
compares each of the DWARF-sized 2188-byte character records against the
profile avatar field, and writes the matching index to both named selection
globals. All five global references and the `stricmp` call resolve by symbol.

`update_frame` exactly reproduces the typed reward, player-death, edge-draw,
and frame-advance transitions in 120 bytes. The reward thresholds are two
independent checks: above 60 ticks it adds 3277, and at nine ticks or below it
subtracts 6554. Those ranges do not overlap, but preserving the separate
checks gives the historical high-reward tail block and resolves every
relocation. The death-counter update does not suppress the edge-draw or
frame-advance work: the original continues into both checks after updating the
counter.

`checkMenuFocus` recovers the replay-menu guard and the focus-change music
transition over the named `in_replay_menu`, `hasFocus`, and `lastFocus`
globals. The candidate has the historical 59-byte extent but chooses different
dead registers for the first two loads, so it is also `DIFFER` without exact
credit.

`check_dir` exactly reproduces the 103-byte directory-enumeration callback: it logs the
candidate path, accepts non-dot directories, checks for `"%s/%s.txt"`, and
counts a matching character. Its external calls, format string, and
`num_chars` reference and direct same-CU logging target resolve exactly.

`for_each_directory` matches its full 109-byte wrapper. It copies the base
directory into its DWARF-sized local buffer, appends `"*"`, and invokes the
named Allegro `for_each_file_ex` callback API with directory attributes.

`play_sound` exactly recovers its full 215-byte source body. It preserves the
`itrcheck` gate, randomized pitch, sound-volume guard, player-x pan conversion,
fast-forward pitch doubling, and Allegro `play_sample` call. Every symbolic
reference, instruction sequence, and the direct same-CU `new_rand` target
matches. The `32.0f` pan-offset literal has the original bytes but occurs more
than once in the partial-CU read-only data, so its relocation target is not
independently established. It is `CODEGEN_SIMILAR`, rather than an exact
function match.

`play_jump_sound` similarly recovers its full 141-byte threshold selector. It
selects one of the three typed `custom.jump_sound` entries from the player
vertical-speed thresholds `-22.0f` and `-15.0f`, then calls recovered
`play_sound`. The first threshold is repeated in original read-only data, so
the verifier anchors it through the unique succeeding two-float sequence; a
shifted relocation is covered by a mutation regression. Its direct same-CU
sound call remains layout-dependent in this partial build, so it is `DIFFER`.
The two 37-byte menu-sound selectors now make the same direct call, so their
otherwise identical bodies are likewise recorded as `DIFFER` until the full
translation-unit layout is recovered.

`stopGameMusic` and `startGameMusic` recover the three-source music lifecycle:
the custom sample, custom MIDI, and fallback beat sample, with the typed
`gameMusicVoiceID` state reset and cleaned up through the corresponding Allegro
APIs. Their candidates have the historical 58-byte and 144-byte extents and
are `CODEGEN_SIMILAR`. `stopGameMusic` has a masked-equal 58-byte body; its
only unresolved relocation is the same-CU data-section placement of
`gameMusicVoiceID`. `startGameMusic` retains its separately documented MIDI
guard register-allocation difference, so neither routine receives exact-function
credit.

`syncOptionsFromProfile` recovers its full 157-byte reverse profile sync. It
copies the four persisted option fields, updates the three menu-control values,
selects the saved avatar, and rebuilds the profile replay directory with its
`"replays/"` suffix. The instruction stream, avatar call, and literal target
all agree. The only unresolved relocations are the same-CU `.data` placements
of the sound and music volume sliders, so it is `CODEGEN_SIMILAR`, rather than
an exact function match.

`get_gamepad_value` matches its complete 166-byte configuration-action parser.
It reads the requested action with the fallback `"nothing"`, maps `up`,
`down`, `left`, `right`, and `jump` to their five input-bit values, and returns
zero for every other value. Its strings resolve through the verifier's unique
read-only-data checks and all six configuration/string API calls resolve by
name.

`load_sound` matches its complete 166-byte loading helper. It conditionally
draws its loading message, stores the WAV result through the supplied pointer,
and shows the original seven-argument failure dialog only when loading fails.
Its UI, audio, dialog, font, and read-only-string references all resolve
exactly.

`take_screenshot` recovers the complete 203-byte capture workflow. It allocates
the next unused `screenshots/icytower_%04d.png` name with the historical
post-increment counter, enforces the 9999 limit after every existence test,
saves a sub-bitmap with the current palette, and waits for F12 release. Its
instruction stream, calls, and literals match; the only unresolved relocations
are the function-static counter allocation and the external Allegro
keyboard-array placement. It is `CODEGEN_SIMILAR`, rather than an exact
function match.

`open_web_browser` recovers its complete 111-byte URL-launch helper. It builds
the historical `url.dll, FileProtocolHandler` argument, logs the command, and
calls the stdcall `ShellExecuteA` API through `rundll32` with show mode 4. The
instruction stream, named call targets, and nonempty literal targets match. Its
only unresolved relocation is the empty working-directory string: the original
uses a NUL byte pooled after an unrelated literal while this partial CU emits a
different empty-string occurrence. It is therefore `CODEGEN_SIMILAR`, not an
exact function match.

`load_new_ad_image` recovers the complete 100-byte application-side ad bridge.
It selects an `FLDAdSpot`, logs its typed local image path, destroys the prior
bitmap, loads the replacement, and retains the selected ad pointer. All ad-CU,
bitmap, and global references resolve by name; the same-CU logging call leaves
the partial build `DIFFER`.

`log2file` has a same-sized 189-byte candidate but is not exact. Its recovered
source preserves the original early `itrcheck` gate, pthread mutex, lazy
logfile path, append-mode output, newline, and historical va_list reuse. The
first instruction-level difference is how the compiler loads `itrcheck`.
The function therefore remains DIFFER even though its visible control flow
and call order agree.

`new_rand` and `new_srand` also match their complete 128-byte and 14-byte
bodies at -O2. The verifier resolves the random generator's x87 double and
single-precision literal relocations by their unique bytes in the original
read-only data, independently of masked instruction equality. That exact
dependency permits the recovered particle CU to enter the separate synthetic
custom-audio link.

`start_reward` now recovers the nine level bands, 80-frame reward setup, selected `data[90 + r]` image, combo sound, and non-flash particle burst. Its 476-byte candidate is four bytes longer than the original 472-byte body because its burst branch has a different register allocation and placement. In particular, the original keeps `itrcheck` in `edi` and reuses it as the burst-loop counter, while the candidate uses `ebx` for the guard before the loop. DWARF confirms that the recovered local declaration order is already exact: `r` at line 2344 and `i, p` at line 2345. It is recorded as `DIFFER`; future source experiments must preserve this guard live range without changing reward behavior. Typing its `reward_bmp`, `combo_sound`, and 512-entry `stars` globals also resolves the complete bodies of two existing helpers.

`update_reward` was independently derived from its named `reward_time` and
`reward_scale` globals, but both source control-flow forms tested at -O2 emit
a 54-byte body with the high-reward branch placed after the shared epilogue;
the original is 55 bytes and places that branch first. It remains non-exact
pending a source-level explanation for that compiler layout.

This is intentionally a partial CU report: there are 82 original main.c
functions, so it cannot support a CU-wide text or object claim. The exact
helper is checked by the pipeline test, and the complete comparison inventory
is `docs/experiments/game-main-partial-O2.json`.


line_alert is reconstructed from the 0x409138 overlay sequence. It applies the original alpha-158 black blend, clears the active display through gfx_driver dimensions, draws asset 88 at (103,200), and centres its message with asset 51 at (320,220). The candidate has the original 353-byte extent and remains DIFFER pending instruction-level layout recovery.


show_instructions is reconstructed from 0x40c368. It blits assets 126 and 70 to the screen, clears held controls, fades in, then pumps focus and control state until fire, Escape, or window close before the matching fade out.

`fadeOut` is recovered from its 0x40bf5c body and the DWARF-owned
`swap_screen` bitmap. It copies the display, blends the copy over the swap
buffer from alpha 0 through 255 at the requested rate, presents each frame
after a timer tick, then clears the display. The new independent body is 578
bytes against the historical 609 bytes and remains `DIFFER` while its local
and basic-block allocation is recovered.

`fadeIn` is recovered from 0x40c1c0. It mirrors the transition in reverse:
it draws the supplied bitmap into a temporary surface, blends it from alpha
255 toward transparent, presents each timer-driven frame, and destroys the
temporary. Its independently compiled body has the exact 424-byte historical
extent and remains `DIFFER` only at a late register/layout decision.

`show_credits` is reconstructed from the 0x40c4dc body and its DWARF locals. It fades the menu music from `options.msc_volume` over 150 timer frames, draws assets 125 and 126, centres the three original credit lines, and preserves the focus, close-button, Escape, and timer handling before fading out. The independently compiled body is 654 bytes against the historical 634 bytes; its draw and timing sequence agrees, while GCC places the loop tests differently, so it is recorded as `DIFFER`.

`testWindowResolution` is reconstructed from the 0x40db18 body. It recovers the DWARF-backed `options.full_screen` field and `window` state, preserves the palette around the fullscreen/windowed 640x480 changes, re-establishes display-switch focus callbacks, and restores the mouse over `screen` for windowed mode. Its `SWITCH_BACKAMNESIA` and `SWITCH_BACKGROUND` modes, calls, strings, and global references resolve to the original; the candidate has the exact 388-byte extent but loads the initial `window` value through a different register and remains `DIFFER`.

`draw_progress_bar` is independently recovered from the 0x407a08 body. It preserves the `itrcheck` guard, four-pixels-per-step clamp at 212, screen locking, all three fills, centered `last_log` text, and incremented progress state. The candidate is 482 bytes against the historical 486 and remains `DIFFER`. Its first layout divergence is the guard live range: the original loads `itrcheck` into `ecx` and reserves `ebx` for the function-static progress value, while the candidate reuses `ebx` for both non-overlapping values. Future recovery must preserve that source-lifetime distinction without introducing an artificial local.

`Tprofile` is now mapped from the main-CU DWARF record: a 1360-byte profile begins with a six-byte header, a 32-byte handle, checksum and play statistics, then five-element `cccNum`, `cccTotal`, `ccc`, and `jc` integer arrays. The retained padding preserves the independently confirmed offsets of flash, jump hold, floor, and volume settings used by the recovered main paths.

`handle_player_collision_original` is independently recovered from the 456-byte body at `0x407e10`. It queries the left and right player-foot contacts through `is_solid`, records `any11`, `any12`, and the three cleared collision diagnostics, changes airborne status to 3 when both contacts are clear, stops vertical movement on impact, aligns the player with the floor, and records the impacted edge. The exact DWARF `Tplayer` definition is now present, including the 184-byte layout and its `status`, `rotate`, and `edge` fields; `Tmap map` and the diagnostic globals are likewise typed. The candidate preserves the first 205 bytes after relocation resolution and has a 449-byte body. It remains `DIFFER`: the historical compiler keeps separate tail branches for the equal-edge and right-edge cases, while the recovered source compacts portions of that tail differently. Two source variants are rejected: making the right-contact path unconditional after the left test yields a 430-byte body, and reversing the branches to test the missing left contact first moves the `play_sound` path from its historical function offset 405 to 385. The retained source keeps that direct call at offset 405.


`uninit_game` is independently recovered as the exact 646-byte shutdown path at `0x40e288`. It saves the configuration and active profile when initialization completed, releases testers, every sound group, custom-character bitmaps, the datafile, swap surface, high-score tables, and the active player, then switches to text mode and exits Allegro. The original log literals, including the leading newline before `UNINIT`, are preserved; its COFF relocation-resolved body is a `FUNCTION_MATCH`.

`_mangled_main` remains missing, but its 1,938-byte entrypoint state machine,
DWARF locals, direct callee surface, and ordinary-link dependency position are
now recorded in [the entrypoint recovery map](mangled-main-recovery.md). This
preserves the recovered initialization, menu, replay, and shutdown phases as
source-recovery constraints without introducing a synthetic entrypoint.
