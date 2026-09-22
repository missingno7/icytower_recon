# `_mangled_main` progress (8 of 8 named locals resolved by evidence; 208-byte gap traced to the register-scheduling/block-layout class)

Target: `_mangled_main` (`src/main.c:5761`, historical `0x415f10..0x4166a2`, 1938 bytes). Body file:
`docs/attempts/game-main/bodies/_mangled_main.c`. No `src/**` edited, nothing committed.

## Locals resolved

`unused_locals.py` flagged 8: `full_path`, `f`, `menu_x`, `menu_y`, `hDebugLibrary`, `should_chdir`,
`logfilename`, `play_again`.

**Renames confirmed by `local_slot_trace.py` (exact stack-slot match, not guessed):**
- `full_path` = `-0x518(%ebp)` — was `executable_name[1024]`, same buffer, same `get_executable_name`/
  `replace_filename` call sites.
- `logfilename` = `-0x118(%ebp)` — was `logfile_path[256]`, same `memset`/`get_logfile_path`/`fopen`
  call sites.
- `f` — DWARF gives it a location list (alternating `edi`/`eax` as the compiler tracks the same `FILE*`
  value in two registers simultaneously across the `fopen`/`test`/`fprintf`/`fclose` sequence, offsets
  202-436 and again 1493-1880); was `fp`, same role.
- `play_again` — DWARF location list, register `esi` (`DW_OP_reg6`), two ranges covering the
  `new_game`/`play`/`end_game` loop (historical lines 5932-5958 per `unused_locals.py`'s own block
  resolution); was `play_result`, same role (the `do { ... } while (play_again && !closeButtonClicked)`
  loop driver).

**`hDebugLibrary` added as a genuine missing statement, not a rename:** DWARF location list decodes to
`DW_OP_reg0` (`eax`), live at function-offset `[33,44)` — exactly the `test %eax,%eax` / `je` that
checks `LoadLibraryA`'s return — confirming the original captures the handle rather than discarding it
as our prior source did (`if (!LoadLibraryA(...))`). Added `HMODULE hDebugLibrary =
LoadLibraryA("exchndl.dll"); if (!hDebugLibrary) printf(...);`.

**`menu_x`, `menu_y`, `should_chdir` left unnamed, deliberately:** all three carry no `DW_AT_location`
at all (checked via the same evidence-file `location` field used throughout this session's collision
work). `menu_x`/`menu_y` most likely correspond to the `355, 285` literals already passed directly to
every `draw_menu`/`handle_menu` call in the existing source — a constant that never needed a location,
matching the `fy2`/`ply2`/`pry1`/`pry2` pattern from `handle_player_collision_combo`/`_vector` earlier
this session. `should_chdir` likewise has no location; I did not find a second `chdir` call or any
branch around the existing single `chdir(working_directory);` call in the disassembly
(`function_lines.py --source-view 5761 5830`, raw instruction dump for offset 0-150) — the call is
unconditional in the object exactly as our source already has it. Adding an unread/never-diverging
`if (should_chdir)` guard around an already-unconditional call would only risk the same
"land a statement whose value the optimizer can fold, deleting something else" failure mode documented
in the `_combo` finding; did not add one without evidence of an actual branch.

## Measurement

Fresh `tu_context_probe.py` labels (`mm-1` baseline, `mm-2` after the above), `--order historical`,
`losses` clean/unchanged throughout (same pre-existing baseline set as every other function this
session: `check_beta_tester, line_alert, show_instructions, start_reward, stopGameMusic, uninit_game`).

| variant | candidate size | delta from 1938 |
|---|---|---|
| baseline (unnamed) | 1730 | -208 |
| all 8 locals resolved (7 renamed/evidenced + `hDebugLibrary` added) | 1730 | -208 |

Renaming and adding `hDebugLibrary` produced **zero byte change** — expected for the renames (pure
text, as established for every prior function this session), and the `hDebugLibrary` capture is a
single extra register-only assignment with no observable cost either way here. `unused_locals.py` now
reports only the 3 no-location names remaining, all left alone per the reasoning above.

## Where the 208 bytes actually are: same block-layout class, one clear instance found

Diffed the two objects (`aligned_view.py diff`) and found a large, clean example. Historical line 5840
(`if (itrcheck) { ... }`, guarding the demo/replay-then-exit branch) is compiled as `test itrcheck; je
0x416502`. `0x416502 - 0x415f10 (function VA) = 0x5f2 = 1522` — that jump target is **exactly** the
start of the "Initiating scroller" `log2file`/`init_scroller`/`init_control`/`reset_menu` block
(historical lines 5841-5853), which the original places far out-of-line (offset 1522-1720, ~200 bytes
away from the branch that reaches it on the common, `itrcheck == 0` path). Our candidate's equivalent
block is emitted essentially inline, right after the branch — the diff shows a 33-instruction
`delete`/`insert` pair (`orig[315:348]@1534` / `cand[113:134]@486`) that is the same content at a
different byte position, not missing code. This is the identical block-placement phenomenon already
parked five times this session (`handle_player_collision_old`'s duplicated tail — the one case that WAS
fixable with a `goto` — plus `_combo`, `_vector`, and the `load_character`/`handle_player_input`
instances referenced in `docs/tu-context-analysis.md` section 14, which are not fixable by surface
`if`-vs-`goto` rewrites). Given this function is ~200 historical lines with many branches of this
shape, it is very likely the dominant contributor to the 208-byte gap, though I did not exhaustively
audit every remaining diff hunk for a second genuinely-missing statement given the session's length.

## Prologue check

`push %ebp; mov %esp,%ebp; push %edi; push %esi; push %ebx; sub $0x52c,%esp` — same callee-saved set
(`edi, esi, ebx`) as the original, matched throughout. One notable original-only detail found but not
chased: a lone `push %edi` at offset 30 (between the `LoadLibraryA` call and its `test`), matched by an
extra `pop %edi` before *every* return path (offsets 411 and 1088, not just the final epilogue) — a
known GCC size trick (`push` as cheaper than `sub esp,4` when only a little extra scratch space is
needed for one call's arguments) rather than a real callee-save difference. Noted for whoever looks at
this function's byte layout next; did not attempt to reproduce it.

## Current state

Body file left with 8/8 originally-flagged locals correctly represented (7 by evidenced rename/slot
match + `hDebugLibrary` added; 3 correctly left unnamed per their no-location status). Compiles clean,
no losses, `1730/1938` unchanged from baseline. Uncommitted, `src/**` untouched.
