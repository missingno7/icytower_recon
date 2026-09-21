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
