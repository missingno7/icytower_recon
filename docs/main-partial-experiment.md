# main.c helper recovery

`src/main.c` currently recovers twenty-five historical helpers while the remaining
main CU entities stay absent. `get_version_str`, `get_demo`, and
`get_controls` each match their complete 10-byte bodies at -O2. The version
accessor's anonymous `"1.5.1"` string relocation is resolved only by its
unique NUL-terminated bytes in the original read-only data; `get_demo` and
`get_controls` resolve their `demo` and `ctrl` globals by name.

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

`end_game` has a recovered 32-byte source body: it logs `" freeing custom
data"` and calls `destroy_custom_data` on the typed main-CU `custom` global.
Its read-only-data and `custom` relocations resolve exactly. The direct call to
the separately defined `log2file` has no COFF relocation, so its displacement
remains layout-dependent while the rest of historical main.c is absent; it is
therefore recorded as `DIFFER`, with no exact-function credit.

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
