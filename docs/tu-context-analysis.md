# Translation-unit compile context in `main.c` (GCC 4.4.1)

Root-cause analysis of the recurring "compiler context" deadlock, with the
`handle_player_input` / `checkMenuFocus` reproducer.  Evidence lives in
`docs/attempts/tu-context/game-main/*.json` (produced by `tools/tu_context_probe.py`),
the model in `tools/tu_context_model.py`, tests in `tools/test_tu_context_model.py`.
Nothing here changes the meaning of `FUNCTION_MATCH`; the strict verifier stays the only
function-equality oracle.

## 1. The reproducer

| experiment | layout | bodies | exact | same historical predecessor | losses |
|---|---|---|---|---|---|
| `baseline-current` | production `main.c` | production | 54 | 28 / 82 | – |
| `cur-order-hpi` | production order | + retained `handle_player_input` | 51 | 28 / 82 | checkMenuFocus, startGameMusic, stopGameMusic |
| `hist-order` | DWARF `decl_line` definition order | production | 52 | 62 / 82 | check_beta_tester, line_alert, uninit_game (gain: start_reward) |
| `hist-order-hpi` | DWARF order | + retained `handle_player_input` | 51 | 62 / 82 | check_beta_tester, line_alert, uninit_game |

Per-pass RTL dumps of `checkMenuFocus` are identical between `baseline-current` and
`cur-order-hpi` through `181r.csa` and first differ in **`182r.peephole2`**:

```
- (insn 45 2 46 2 (set (reg:SI 2 cx) (mem/c/i:SI (symbol_ref:SI ("in_replay_menu")...
+ (insn 45 2 46 2 (set (reg:SI 0 ax) (mem/c/i:SI (symbol_ref:SI ("in_replay_menu")...
```

The `cmp mem,0 -> mov mem,reg; test reg,reg` peephole asks `peep2_find_free_register` for a
scratch register.  That function keeps a **file-static cursor** (`static int search_ofs` in
`recog.c`) that is advanced past every register it hands out and is never reset between
functions.  The scratch registers chosen across the unit therefore form one rotating sequence
(`ax, dx, cx, ...`, call-saved registers only where already live in the function), and every
function that uses such a peephole depends on how many scratch registers *all earlier-emitted
functions* consumed.  A six-function test unit reproduces the rotation exactly
(`test_peephole_scratch_rotates_across_functions`).

Answers to the five questions:

1. **Does `checkMenuFocus` move in emission order?**  No.  In both A and B it is emitted at
   position 58 after `startGameMusic` and `stopMenuMusic`; `handle_player_input` is at 55 in both.
2. **Does only its predecessor change?**  No.  Its predecessor (`stopMenuMusic`) is unchanged
   and itself still exact.  What changes is the scratch cursor reaching it: the stub
   `handle_player_input` consumes one scratch (`ax`), the reconstruction consumes four
   (`si di ax dx`).  Sequence A: hpi `ax` -> startGameMusic `dx` -> checkMenuFocus `cx` (historical).
   Sequence B: hpi `si di ax dx` -> startGameMusic `cx` -> checkMenuFocus `ax`.
3. **Is its source body byte-identical?**  Yes; only `handle_player_input` changed.
4. **Consistent with the persistent peephole/register state?**  Yes; this *is* that state, now
   identified: `peep2_find_free_register`'s static cursor.  The earlier "clear order"
   observation (`xor reg; mov reg,mem` vs `movl $0,mem`) is the same mechanism (a scratch peephole).
5. **Minimum context change that restores the historical context?**  `checkMenuFocus` is exact
   in the current layout only because the stub's single `ax` find happens to leave the cursor
   where the historical prefix leaves it.  Historically `checkMenuFocus` is emitted at 23,
   long *before* `handle_player_input` (43), so the historical fix is the historical emission
   order: with definitions in DWARF `decl_line` order (`hist-order-hpi`) the reconstruction is
   present and `checkMenuFocus` stays exact.  No smaller move works: removing or changing the
   stub's find before `checkMenuFocus` shifts its cursor unless the whole prefix is historical.

## 2. Emission order model (validated)

`tools/tu_context_model.emission_order` reproduces the compiled function order of every layout
checked (production, DWARF order, both with and without the reconstruction, and the synthetic
test units): GCC expands `cgraph_postorder` in reverse; the postorder walks *caller* edges from
the newest cgraph node to the oldest; definitions create nodes in source order, library callees
are created during analysis (analysis order is the LIFO queue of needed functions, so the
first-defined function is analysed last and its callees are the newest nodes), and caller lists
are prepended.  The consequence that matters here: **the callee-closure of the externals first
referenced by the earliest-defined functions (`log2file` at historical line 399) is emitted
last**, which is why the historical `main.c` emits `_mangled_main`, `run_demo`, `play`,
`do_replay_menu`, `main_menu_callback`, ... at the end.

Declaration placement does **not** matter: a layout with every declaration first and all
definitions after them (`baseline-current`) compiles byte-for-byte to the production object.
Only (a) definition order and (b) the call graph (call sites, including inlined builtins such
as `strlen`) determine emission order.  Storage class matters too, because static functions
enter the analysis queue only when first reached: an early version of the probe misread the
out-of-line DIEs of `new_srand`, `syncProfileFromOptions`, `update_reward`, `is_custom_replay`
(which carry only `DW_AT_abstract_origin`) as static; their abstract DIEs have `DW_AT_external`
and `DW_AT_inline`, so they are historically `inline` with external linkage exactly as in the
current source.  The negative is retained as `hist-order-hpi-static.json`: making them static
drops their out-of-line copies (four MISSING) and moves six more historical predecessors away.
`main.c` has no historically static function; `historical_static` now reads the origin-merged
attributes and reports, for example, the three `loadpng.c` helpers correctly.

With the historical definition order and the *current* call graph the model predicts (and the
compiler confirms) 62 / 82 historical predecessors.  The remaining deviations are call-graph
differences of incomplete bodies: `play` (23 of ~75 historical callees, missing the only
historical call to `do_replay_menu`), `draw_frame`, `_mangled_main`, `init_game`.  As those
bodies regain their historical call sites, the order converges without any further reordering.

## 3. Why the historical order costs three matches today

Under the DWARF order `check_beta_tester` and `uninit_game` lose their (single-register)
matches because the stubs `play`, `do_replay_menu` and `run_demo` are emitted early (wrong
call graph) and their scratch finds shift the cursor; `line_alert` becomes `CODEGEN_SIMILAR`
because the read-only literal pool follows emission order and the stubbed `draw_frame` supplies
none of its literals.  The monotone family `prefix10..prefix82` (first *k* historical
definitions in DWARF order, rest current) never reaches zero losses; the full historical order is
the floor with exactly these three.  All three are context-accidental matches: their sources
are unchanged and they return as soon as their historical prefixes (`play`'s call structure,
`my_alert`, `force_create_profile`, `new_game`, `draw_frame`'s literals) are recovered.

The current production order has the mirror problem: `checkMenuFocus`, `startGameMusic`,
`stopGameMusic`, `run_demo`, `testWindowResolution`, `uninit_game`, `check_beta_tester` are exact
only through accidental cursor arithmetic, so *any* body reconstruction emitted before them
(`handle_player_input`, and later `draw_frame`, `play`) regresses some of them.

## 4. Transaction model

The existing CU-wide re-verification (`refresh_recovery.py --verify-all` with
`no_regressions`) already accepts or rejects a whole translation-unit state atomically; the
missing pieces were (a) a generated, reproducible edit set covering definition order, retained
bodies and evidenced declarations, (b) a diagnostic bench that compiles such a set in isolation
and reports the final TU state, and (c) the understanding above.  `tools/tu_context_probe.py`
is (b); the `TU_CONTEXT` task (`tools/tu_context_task.py`) is (a) with the strict final-state
gate: every previously exact function exact, no data-owner regression, no unresolved symbols,
ordinary link succeeds, no new implicit declarations, fresh locked identities.

Decision needed from the project owner: the strict gate cannot accept the historical-order
transition until the three context-accidental matches are re-established through real
reconstruction (`play` call structure and the bodies above).  The recommended path is to do
that reconstruction against the historical layout in the probe overlay (`--order historical
--body ...`) and land everything as one `TU_CONTEXT` transaction when it reaches zero losses.

## 5. What the mechanism has landed (2026-09-21)

| transaction | unit | edit set | result |
|---|---|---|---|
| `order_profile` | profile.c | whole-unit DWARF definition order | 8 -> 11 exact (`load_profile`, `save_profile`, `profile_data_page_advanced`), 0 losses |
| `order_menu` | menu.c | whole-unit DWARF order | 7 -> 7, historical predecessors 7 -> 10 / 10 |
| `order_replay` | replay.c | whole-unit DWARF order | 5 -> 5, historical predecessors 5 -> 15 / 15 |
| `order_player` | player.c | whole-unit DWARF order | 2 -> 2 |
| `main_hpi_context` | main.c | retained 728-byte `handle_player_input` + three historical-anchor moves | 54 -> 54, 0 losses, historical predecessors 28 -> 31 |

The `main.c` repair came from the bounded search (`tools/tu_context_repair_search.py`; candidates = an
island or a DWARF-contiguous block placed after its historical predecessor, combinations of at most
three; 63 compiles).  Under the old single-move model the retained `handle_player_input` regressed
`checkMenuFocus`, `startGameMusic` and `stopGameMusic`; as one transaction with `startGameMusic`
after `check_characters` (lines 818/876), `handle_player_input` after `play_jump_sound`
(2381/2389) and the `startMenuMusic..._mangled_main` tail after `force_create_profile` (5650/5726),
all three stay exact and the fuller body is in production.  The single move of
`handle_player_input` alone was also loss-free; the compound was preferred for its higher
historical-predecessor count.  None of the component edits was judged on its own: several of them
regress when applied alone (`docs/attempts/tu-context/game-main/bounded-repair-search-pre-transaction.json`).

Whole-unit reorders are now always `TU_CONTEXT` cards (`source_order.py`), queued only when the
retained whole-unit probe is fresh and loss-free; `order_main` remains SUPERVISOR with its three
context-accidental losses named.  The way to clear it is unchanged: reconstruct `play`'s call
structure, `draw_frame`, `_mangled_main` and `init_game` against the historical layout in the probe
overlay (`--order historical --body ...`), then land the order and the bodies as one transaction.

## 6. Structural convergence of `main.c` (2026-09-21, later)

Two more mechanisms became visible once large bodies were reconstructed against the historical
layout, and both are now reported by the probe.

**Inlining hides source-level edges.**  GCC's optimized call graph loses every call it inlined
into its caller, so a reconstruction that is *smaller* than history shows edges as missing that
its source really makes: with a 5007-byte `play`, 34 callees (including `handle_player_input`,
`update_player`, the five collision handlers and `poll_control`) were inlined into it, while the
17420-byte historical `play` was far past the inliner's size limits and called all of them.  The
probe therefore reads source-level edges from the pre-inlining section of the dump and reports
what was inlined separately (`--focus`).  Edge deficits close as the body grows; they are not a
reason to add calls.

**Undeclared historical interfaces.**  `main.c` was missing six of its own globals
(`is_playing_custom_game`, `gdComboStart`, `hints`, `fall_count`, `clock_angle`,
`checkMusicVoiceID`, all DWARF variables of the CU with an address and a decl line) and seven
cross-CU prototypes (`get_rank_id`, `getGameDataXML`, `add_combo`, `add_jump_sequence`,
`qualify_hisc_table`, `sort_hisc_table`, `enter_hisc_table`).  Both sets were restored as
`TU_CONTEXT` transactions with `add_top_level` declaration edits, each placed next to its nearest
historical neighbour: 54 exact before and after, no loss, no data-owner regression.  The same
mechanism replaced the hand-written `ShellExecuteA`/`WSAStartup`/`WSADATA`/`MAKEWORD` substitutes
with Allegro's `<winalleg.h>`, which also removed the last implicit declaration (`LoadLibraryA`)
and the linker's stdcall fixup warning.

**Where the historical order stands.**  With the reconstructed `play` present, the historical
definition order costs only two matches instead of three, and both are downstream of bodies that
are still incomplete:

| function | why it is not exact under the historical order |
|---|---|
| `line_alert` | three bytes: its `.rdata` addend, i.e. the read-only literal pool offset, which moves when `draw_frame`'s literals are restored |
| `run_demo` | scratch cursor: it is emitted directly after `play`, whose four peephole scratch finds are those of a 5007-byte body, not of the 17420-byte original |

Historical predecessors under that order rose from 31 to 71 of 82, and `check_beta_tester` and
`uninit_game` returned on their own.  The remaining work is body reconstruction, not ordering:
`draw_frame` (literal pool) and the rest of `play` (cursor).  When both reach zero losses, the
order, the bodies and the declarations land as one transaction.

## 7. Reconstructing a large body against the historical layout (2026-09-22)

Three failure modes cost more time than the reconstruction itself, and all three are now tooled.

**A local read before it is written deletes code.**  `play`'s loop variable was declared and never
assigned, so GCC treated the read as undefined and removed the whole game loop: the body compiled
cleanly at 5060 of 17420 bytes with every historical call edge present in the source, and three
regions measured zero bytes.  Adding the one missing statement took it to 12545.
`tools/uninitialized_locals.py` reports such locals for a retained body; it also explains empty
regions in the byte budget, and an unused local occupies no stack, which shows up as a frame that
is too small.

**Byte counts must be read per region, not per line.**  A reconstruction's line numbers are its
own, so comparing bytes per line against the historical line table is meaningless.
`tools/merge_regions.py` records each region's span in the merged body and
`tools/line_budget.py --regions` charges every instruction, including code inlined into the region,
to the region it came from.  Its `--no-inline` mode exists only to make a body far smaller than its
original comparable with a history that inlined none of those callees; it is diagnostic and never
touches a promotion path.

**The call graph converges before the code does.**  All 59 historical call edges of `play` and all
of `draw_frame`'s were restored long before either body was the right size, because edges come from
statements while size comes from their contents.  Edge parity is the signal that the structure is
right; the byte budget and then the aligned diff are the signals that the statements are.

Both bodies are now within a few percent of their originals (`play` 15229 of 17420, `draw_frame`
7574 of 8518) and sit at their historical emission positions, so ordinary first-difference grinding
applies: both stack frames are 16 bytes short, which is the next thing to fix.  Under the historical
order the unit stands at 54 exact with `draw_progress_bar` and `start_reward` gained and `run_demo`
and `stopGameMusic` lost, both to the scratch cursor.  The losses move as the bodies grow, so the
transaction lands when they reach zero, not before.

## 8. What the last two losses require (2026-09-22)

With `play` at 16110 of 17420 bytes and `draw_frame` at 8384 of 8518, both at their historical
emission positions and with every historical call edge present, the historical order still costs
`run_demo` and `stopGameMusic`.  The peephole dumps say exactly why, and the answer is not a
context question any more:

`play` performs 65 peephole scratch finds and is emitted directly before `run_demo`.  Its last
find leaves the cursor on `si`, so `run_demo` picks `dx, cx`; it is exact only when it picks
`cx, bx`, which needs the cursor to arrive on `ax`.  One find more or fewer anywhere inside
`play` moves it.  `stopGameMusic` sits after `draw_frame` and `handle_player_input` and is exact
only when its single find is `cx` instead of `ax`, which likewise depends on `draw_frame`'s eleven
finds being the historical ones.

So the two functions are not blocked by ordering, declarations or neighbours: they are blocked by
the remaining 1310 bytes of `play` and 134 bytes of `draw_frame`.  A function whose scratch finds
must match exactly is effectively asking for the body itself, which is the right thing to be
asking for.  The transaction lands when the bodies do.

## 9. Dead writes name their missing readers (2026-09-22)

A reconstruction that writes a value the original writes, and then stops, compiles shorter than the
original for a reason that looks like a compiler difference and is not: GCC deletes the write because
nothing reads it, and what is missing is the code that reads it.  Three separate passes wrote off
`play`'s `rank_y` and `alpha_pos` on exactly this evidence ("the write is dead, the compiler removes
it, nothing to do"), and one went further and blamed a different original toolchain.

`tools/local_slot_trace.py` settles such a question in one command by listing every instruction in the
original that touches a local's stack slot, with its historical source line:

| offset | line | access |
|---|---|---|
| 12056 | 4821 | `rank_y = 580` |
| 12391 | draw.inl:238 | a sprite draw reads it |
| 12503, 12522, 12556 | 4823 | the easing reads it and writes it back |
| 13756 | draw.inl:238 | a second sprite draw reads it |
| 13966, 13996, 14023 | 4885, 4886, 4891 | `alpha_pos` incremented, masked, decremented |

So the rank banner is drawn twice from `rank_y`, and `alpha_pos` is the letter-navigation cursor.
Neither write is dead in the original; both readers are simply absent from the reconstruction.

The same trace disambiguates a stack slot shared between locals of different scopes, which is not a
detail: `gameover_bmp_id` and `alpha_pos` share `-0x930(%ebp)` in `play`, and the second argument of
the first `draw_results` call reads that slot while it still holds `gameover_bmp_id`, so a pass that
assumed `alpha_pos` had written the wrong argument into the reconstruction.

The rule this establishes: when a body compiles short and a local's write looks dead, trace the slot
before concluding anything.  A dead write is a symptom of missing readers, never a cause in itself.

## 10. The peephole cursor is a global counter, and a downstream loss is a downstream indicator

`peep2_find_free_register` keeps a file-static `search_ofs` that rotates through the allocation
order (ax, dx, cx, bx, si, di, bp) and is never reset between functions.  Two measurements pin the
behaviour down exactly.

In `httpget.c` a control overlay inserted one artificial extra scratch consumer ahead of every
other function.  It took `dx`; `destroyHTTPResponse` moved `ax -> cx` and the candidate
`dumpHTTPResponse` moved `dx -> bx`.  Each consumer advances the cursor by one step for everything
emitted after it, with no other coupling.  That arithmetic is strong enough to run backwards: the
original's `dumpHTTPResponse` takes `cx` where ours takes `dx`, so exactly one more scratch was
consumed before it historically; `SplitURL` is exact and consumes none; therefore the missing
consumer is `extractHTTPResponse`, and the original's `extractHTTPResponse` does contain the
predicted peephole at offset 70 with the predicted register `dx`.
(`docs/attempts/game-httpget/dumpHTTPResponse-finding.md`.)

In `main.c` the same arithmetic explains the single loss that blocks the prepared historical-order
transaction.  Under the historical order with the reconstructed `play` and `draw_frame` bodies, the
probe reports gains `draw_progress_bar`, `log2file`, `open_web_browser` and one loss, `run_demo`,
which needs `cx, bx` and gets `dx, cx`: one step short.  133 scratches are consumed before it and
134 are needed.  Sixteen of the functions emitted before `run_demo` are still DIFFER (`draw_frame`
alone consumes 11, `play` 67), so the deficit is not `play`'s private property and `run_demo` is not
a separate problem to solve.  It is an indicator that goes green when the bodies ahead of it are
right, and it must not be chased by altering `run_demo` or by reordering around it.

The order is only worth having with the bodies.  A control overlay applying the historical
definition order **alone**, with no reconstructed bodies, is a net regression: one gain (`log2file`)
against six losses (`check_beta_tester`, `line_alert`, `show_instructions`, `start_reward`,
`stopGameMusic`, `uninit_game`).  The same order with the two bodies is +3/-1.  Order and bodies are
one transaction precisely because neither is acceptable alone.

## 11. A DWARF local our source never names is a located gap

Every local the historical source declared got a stack slot or a register, so a DWARF local whose name
appears nowhere in a reconstruction marks statements we have not recovered.  Unlike a byte budget this
does not depend on line attribution, cross-jumping or inlining, so it stays meaningful while a body is
still far from its original size, which is exactly when a byte budget stops being trustworthy.
`tools/unused_locals.py` reports them with each one's lexical block resolved to a historical line span.

On `play` it located three separate gaps in one call, two of which two byte-budget passes had failed to
find: `clockSpeed`/`qpcSpeed`/`timeSpeed` in a debug-timing block at lines 3604..3661; `skipCategories[5]`
and `achs` in a block covering exactly lines 4753..4770, where the reconstruction had written two string
copies instead (and where our three spurious `memcpy`/`__builtin_memcpy`/`strlen` call edges come from);
and `done`, `pos`, `hyTarget`, `scrollerY`, `scrollerTargetY`, `rankTargetY` in the results block, whose
`*Target` names give away the easing shape of a block that had twice been reconstructed wrongly.

The check is cheap enough to sweep the whole project.  Excluding `play` and `draw_frame`, whose
production definitions are placeholders, the functions with unrecovered locals are, by count:

| function | unnamed locals | candidate / historical |
|---|---|---|
| handle_player_collision_vector | 16 | 1021 / 1071 |
| handle_player_collision_vector_2 | 13 | 1057 / 1086 |
| handle_player_collision_combo | 9 | 1381 / 1390 |
| do_replay_menu | 9 | 2159 / 2661 |
| init_game | 8 | 5666 / 5788 |
| _mangled_main | 8 | 1730 / 1938 |
| draw_profile_selector | 5 | 1242 / 1268 |
| handle_player_collision_old | 4 | 961 / 894 |
| select_profile | 3 | 2706 / 3070 |
| draw_results | 2 | 839 / 839 |
| extractHTTPResponse | 2 | 918 / 923 |

The four collision handlers share the same missing geometry variables (`fx1`, `fy1`, `fx2`, `fy2`,
`plx1`, `ply1` ...), so they are one gap appearing four times, not four gaps.  `draw_results` is already
the exact historical size with two locals unnamed, and `extractHTTPResponse` needs only `last` and `c` --
and it is the function whose single missing peephole scratch is the one thing keeping `dumpHTTPResponse`
from being exact (section 10).

The converse carries no information: a name we do use may still be used for the wrong thing.  On
`draw_frame` the tool reports nothing missing, and `draw_frame` is still 12 bytes short.

## 12. Reading the original's DWARF location lists, and what a transaction may add

Three separate passes have now misread the original's `.debug_loc`, so the recipe belongs here.
`evidence/census/location-lists.json` is a list of tables keyed by `offset`, the value a DWARF local's
`location` string carries (`0x6c9b (location list)`).  Each entry's `begin` and `end` are relative to
the **compilation unit's** `low_pc`, not the function's, so for `main.c` the base is 0x406960 (from
`evidence/census/compilation-units.json`) and an offset inside a function is `BASE + begin - VA`.
`evidence/census/range-lists.json` holds a lexical block's spans in exactly the same form.

Iterate a table's entries directly and call `dwarf_locations.decode_location` on each
`expression_hex`.  Do not use `expression_at()` for this: it returns None whenever more than one entry
covers the PC, which silently hides most of a real table and reads as "the local is not live here".

This is worth the care because a location list answers questions a byte budget cannot.  It said that
`load_character`'s `filename` parameter lives in `esi` only from offset 31 to 58 and is re-read from
`ebp+8` for the rest of the function, which is the whole of that function's thirteen differing bytes
and rules out four source rewrites that had already been tried.  It also distinguishes a local that
was optimised out from one that is register-resident, which matters: `clockSpeed`, `qpcSpeed` and
`timeSpeed` have no stack slot at all and are nonetheless real computed values.

### A transaction may now add a definition

`src/httpget.c` has unresolved ownership and therefore emits only what the oracle has independently
proved, so `dumpHTTPResponse` had no definition to replace.  `TU_CONTEXT` accordingly gained the
narrowest possible power to add one: a retained body whose name has no island in the production
source is emitted at its place in the order, provided it is named in the spec's `add` list, is one of
the retained bodies, and is `MISSING` in the ledger.  Both the plan and the final-state gate check
that exact set, and both still refuse any removal, so a definition cannot appear or vanish by
accident.  Nothing about `FUNCTION_MATCH` or the no-regression rule changed.

One incidental fix came with it: the forbidden-directive count now excludes the generated
forward-declaration block, which only repeats each definition's own signature.  Without that, any
transaction on a file containing a historically evidenced `__attribute__` on a definition was rejected
for "introducing" the attribute that the generated prototype merely echoed.

The first transaction through this path promoted `dumpHTTPResponse` exact and `HTTPFetchInternal` with
it, 7 -> 9 exact in that unit, and took the project's MISSING count to zero.
