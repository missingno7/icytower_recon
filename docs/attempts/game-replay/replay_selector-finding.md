# `replay_selector` — recorded finding (not resolved, large gap located)

`replay_selector` (`src/replay.c`, currently lines 602..773) is 1902 of 2845 historical bytes — a
~943-byte deficit. Retained body used for measurement:
`docs/attempts/game-replay/bodies/replay_selector.c` (currently a byte-identical copy of the
current `src/replay.c` definition; no changes made). Measured via `tools/tu_context_probe.py
game-replay src/replay.c rs-2 --order historical --body replay_selector=... --no-dumps`; baseline
reproduces the stated 1902/2845 exactly.

`unused_locals.py` (first command, as instructed):

```
replay_selector: 16 DWARF locals, 2 never mentioned
local   type          block    historical lines
i       int           223501   (block not resolved to a line range by the tool)
p       char [1024]   223966   786..806
```

## The historical function is longer than our reconstruction assumes

`function_lines --calls-by-line` shows real call sites through roughly source line 938 — our
current body ends at line 773 (`return rep; }`), meaning **at least ~165 historical source lines
of real statements are entirely unaccounted for**, not just the two named locals. Concretely:

- **A second, complete draw-and-present sequence.** Our source calls `draw_replay_selector` only
  once (current line ~756-757, inside the main loop). The historical function calls it **twice**:
  once around source line 799 (call chain: `blit` @543, `set_trans_blender` @614, `drawing_mode`
  @667, `makecol` @703, `solid_mode` @794, `draw_replay_selector` @799, `blit_to_screen` @872,
  `rest` @885 — matching our existing single sequence at lines 751-760) and a **second, nearly
  identical sequence** at source lines 911-921 (`blit` @1406, `set_trans_blender` @1477,
  `drawing_mode` @1530, `makecol` @1566, `solid_mode` @1657, `draw_replay_selector` @1662,
  `blit_to_screen` @1733, `rest` @1288). This is not duplication noise (unlike the tail-duplicated
  comparisons seen elsewhere in this project) — it is two textually and semantically distinct call
  sites for the whole draw+present block, meaning the source has an entire second
  draw-and-present pass we have not modeled, most likely tied to the `pageY`/`targetY` scroll
  interpolation already present in our source (lines 749-750): a plausible shape is drawing once
  at the old `pageY` and once at the new, or drawing a second overlay/transition frame — not yet
  confirmed, needs the actual argument lists at both call sites traced.
- **`p` (`char [1024]`, live lines 786-806)** is a second, 1024-byte path/filename buffer separate
  from the existing `fname[512]`. Given the K EY_F5 handler already uses `fname` for
  `file_select_ex`/`replace_filename`/`strcpy`, and the KEY_ENTER directory-descend handler uses
  `fname` too (current lines 679-681), `p` is most likely a *third* buffer used somewhere in this
  same file-navigation logic that our current reconstruction folds into `fname` alone, or is used
  in a block we're missing entirely (e.g. a rename/copy path not yet modeled — `ok_to_rename` is
  declared and cast to `(void)` in our source at line 761, suggesting a whole rename feature this
  function is supposed to implement but currently doesn't).
- **`i` (`int`)** has no resolved line range from `unused_locals.py` (block PC range not decoded),
  so its usage site is not yet located at all — would need direct DWARF block inspection beyond
  what this pass covered.

## Why not attempted this round

A second complete draw-and-present block (8+ call sites) and an unlocated third string buffer are
a much larger reconstruction than a missing statement or two — this is closer in scope to
`draw_replay_selector`'s gap than to any of the single-cluster fixes done this session. Given the
"don't invent code" rule and that even the *shape* of the second draw pass (what differs about its
arguments from the first) is not yet traced, I did not attempt a source change. Recording the
location and the concrete evidence (two `draw_replay_selector` call sites, the untraced `p`
buffer, the unresolved `i`) for a focused follow-up pass.

## Status

`replay_selector` remains `DIFFER`, unchanged (byte-identical retained body), 1902/2845. The
second `draw_replay_selector` call site is the highest-value next lead — tracing its exact
arguments against the first would likely explain a large fraction of the 943-byte deficit in one
pass.
