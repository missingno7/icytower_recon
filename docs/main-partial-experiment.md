# main.c helper recovery

`src/main.c` currently recovers thirty-eight historical helpers while the remaining
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

The three loading progress callbacks also match: `datafile_callback` is the
12-byte progress-bar tail call, `color_map_callback` is its 22-byte
every-sixteenth-entry form, and `datafile_callback_slow` is the 33-byte
counter-based variant. Its private `p` counter is resolved through the unique
DWARF static variable owned by the already shape-matched function, not its
relocation operand; the compiler's serialised local COFF name is not stable.

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

`check_beta_tester` recovers its full 254-byte body. It reads and garbles the
eight-byte password, compares it against each typed 276-byte beta record,
sets the selected tester, and reports the historical missing-file and
no-match paths. Its 16-byte initializer contains an explicit second NUL;
that source detail is required for the historical ten-byte initialization
copy. The combined partial snapshot's literal neighbourhood remains reported
by the generated comparison inventory.

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

`update_frame` recovers the typed reward, player-death, edge-draw, and frame
advance transitions. Its 125-byte candidate differs from the historical
120-byte branch layout, so it is recorded as `DIFFER` and receives no exact
function credit.

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
reference and instruction sequence matches, including the direct same-CU
`new_rand` target.

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
all symbolic targets resolve. The compiler chooses a different register for a
MIDI guard, so both remain `DIFFER` pending the original full-CU register
allocation.

`syncOptionsFromProfile` recovers its full 157-byte reverse profile sync. It
copies the four persisted option fields, updates the three menu-control values,
selects the saved avatar, and rebuilds the profile replay directory with its
`"replays/"` suffix. All named data references resolve, while the direct
same-CU avatar call and a duplicated suffix literal remain layout-dependent;
it is therefore recorded as `DIFFER`.

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
static counter allocation and direct same-CU logging call remain
layout-dependent, so it is recorded as `DIFFER`.

`open_web_browser` recovers its complete 111-byte URL-launch helper. It builds
the historical `url.dll, FileProtocolHandler` argument, logs the command, and
calls the stdcall `ShellExecuteA` API through `rundll32` with show mode 4. The
local logging call and a duplicated empty string make the partial-CU candidate
layout-dependent, so it remains `DIFFER`.

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

`update_reward` was independently derived from its named `reward_time` and
`reward_scale` globals, but both source control-flow forms tested at -O2 emit
a 54-byte body with the high-reward branch placed after the shared epilogue;
the original is 55 bytes and places that branch first. It remains non-exact
pending a source-level explanation for that compiler layout.

This is intentionally a partial CU report: there are 82 original main.c
functions, so it cannot support a CU-wide text or object claim. The exact
helper is checked by the pipeline test, and the complete comparison inventory
is `docs/experiments/game-main-partial-O2.json`.
