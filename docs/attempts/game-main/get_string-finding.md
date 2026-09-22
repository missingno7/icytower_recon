# `get_string` — recorded finding (not resolved)

`get_string` (`src/main.c`, currently lines 2910..2975) is 790 of 790 historical bytes (exact
size), 541 differing bytes (478 of them real, i.e. not covered by any relocation's 4-byte field).
Retained body used for measurement: `docs/attempts/game-main/bodies/get_string.c` (currently a
byte-identical copy of `src/main.c`; no fix attempted). Measured via
`tools/tu_context_probe.py game-main src/main.c gs-1 --order historical --body
get_string=... --no-dumps`.

`unused_locals.py`: 5 DWARF locals, 0 never mentioned — no missing-statement lever here, unlike
`draw_replay_selector`/`replay_selector`.

## The shape: a missing loop rotation, not a localized difference

Real (non-relocation) differing bytes span **offsets 91 to 789** — essentially the entire function
after the initial setup (`create_bitmap`, the `letters[]` copy, `strlen`, the initial `blit`, the
`key[KEY_ENTER]||key[KEY_SPACE]` spin-wait, `clear_keybuf()`). This is not a localized
statement-level bug; it is a difference in how GCC laid out the `for (;;) { ... }` loop.

### What history does

`function_lines --source-view` on the relevant range shows:

- `main.c:5385` (`if (closeButtonClicked) { destroy_bitmap(block); return 0; }`, the top of the
  loop body) has **two** fragments: `227..232` and `245..259`.
- `main.c:5445` (`while (!cycle_count) rest(2);`, the last statement of the loop body) also has
  **two** fragments: `232..245` and `660..680`.
- Offset 227 is a `jmp` to offset 245 (`jmp 40bd39` -> `+0xf5` = 245), landing *inside* the
  `closeButtonClicked` test, **skipping over** the `cycle_count` test at 232..245.
- The `cycle_count` test's *other* fragment (660..680) is the real, physical location of
  `while (!cycle_count) rest(2);`, deep in the function after the `switch`. It ends with
  `672 jmp 40bd2c` -> `+0xe8` = 232 — back to the *same* `cycle_count` test, not to
  `closeButtonClicked`.

So historically: the `cycle_count` test (the inner `while` loop's own condition) is hoisted to
serve as the **outer `for(;;)` loop's back-edge test**, positioned immediately after setup. The
very first entry into the loop needs a one-time `jmp` to skip that test (since `cycle_count` has
no meaningful value before any iteration has run) and land directly on `closeButtonClicked`. Every
subsequent iteration re-enters through the `cycle_count` test (falling straight through to
`closeButtonClicked` once `cycle_count != 0`, no jump needed — it's laid out immediately after).
This is a standard GCC loop-rotation optimization for a `for(;;)` loop whose last statement is
itself a small polling loop: the inner loop's latch doubles as the outer loop's.

### What our candidate does instead

The candidate's own disassembly (same offsets) shows no rotation at all: `closeButtonClicked` is
tested first, unconditionally, every iteration, in plain source order (offset 227 is a bare `nop`,
not a `jmp`), and `while (!cycle_count) rest(2);` keeps its own separate, un-merged back-edge at
its natural textual position near the end of the function. Every instruction after this point
shifts relative to history because the rotation never happens, which is why the diff spans nearly
the whole body rather than one cluster.

## Conclusion — located, not fixed

Loop rotation is a compiler decision, and the toolchain is the same compiler that built the
original: given byte-identical source for this loop, it should fire identically. Its absence in
our build means some **earlier** source difference is changing the loop's CFG enough to suppress
the rotation — most likely something in the shape of the `switch (c >> 8) { ... }` block (five
cases, three of them `return`), the `continue` inside `if (!keypressed()) continue;`, or how many
distinct back-edges/exits the loop is left with. This makes the absence a **located question**
(something in the switch/continue/multiple-return control flow) rather than an open mystery, but
I have not identified the specific trigger.

## Why no fix was attempted

The real diff (478 bytes) covers nearly the entire function body, the same scale of "everything
shifts because a single structural decision changed" that `handle_player_input`'s dead ends
already demonstrated is dangerous to guess at: a plausible-looking restructuring there produced a
728->764 byte regression by changing an unrelated allocator decision (the callee-saved register
set). Attempting a blind restructuring here, across nearly the whole body, without first isolating
which part of the switch/continue/return shape suppresses the rotation, would repeat that mistake
at a much larger scale. This is recorded as a located-but-unfixed finding rather than guessed at.

## Status

`get_string` remains `DIFFER`, unchanged (byte-identical retained body), 790/790, 478 real
differing bytes from offset 91 to 789, root cause narrowed to "loop rotation not firing, trigger
somewhere in the switch/continue/return CFG" but not yet pinpointed.
