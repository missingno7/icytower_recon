# `draw_replay_selector` — recorded finding (not resolved, large gap located)

`draw_replay_selector` (`src/replay.c`, currently lines 431..514) is 2347 of 3726 historical
bytes — a ~1379-byte deficit, the largest of any function currently worked. Retained body used
for measurement: `docs/attempts/game-replay/bodies/draw_replay_selector.c` (currently a
byte-identical copy of the current `src/replay.c` definition; no changes made). Measured via
`tools/tu_context_probe.py game-replay src/replay.c rs-1 --order historical --body
draw_replay_selector=... --no-dumps`; baseline reproduces the stated 2347/3726 exactly.

`unused_locals.py` (first command, as instructed):

```
draw_replay_selector: 15 DWARF locals, 2 never mentioned
local     type          block    historical lines
is_dir    int           222934   460..538
rbuf      char [129]    223109   589..599
```

## This is not a one- or two-statement gap

`function_lines --calls-by-line` for the whole function shows the true historical function
extends through roughly source line 605, with call sites the current reconstruction has **no
equivalent of at all**:

- Lines 2025/2085/2145/2214/2283: `textout_ex`/`textout_right_ex` printing column headers
  **"NAME"**, **"SCORE"**, **"FLOOR"**, **"COMBO"**, **"DATE "** — a header row for a results
  table our current reconstruction does not draw.
- Lines 2502/2566/2627/2696: `"%6d"`, `"%4d"`, `"%3d"`, `"%s "` — per-column value formatting,
  presumably for a per-replay results table (score/floor/combo/date columns) that isn't in our
  source at all.
- Line 1780 / 552/553: `"CUSTOM GAME  "` text length measurement feeding a `set_clip_rect` call,
  and (offsets 3572-3587) an `"n/a"` fallback string assigned when some condition is false —
  none of this exists in our current body.
- Lines 3420/3328: `"CUSTOM GAME"` (no trailing spaces) and further `textprintf_ex`/
  `textprintf_right_ex` calls, past where our reconstruction ends.
- Lines 3554/3634/3051/3693 (string literals, not yet mapped to specific source lines):
  `"You need Icy Tower 1.2 to view this replay."`, `"You need Icy Tower 1.3 to view this
  replay."`, `"Replay is broken."`, `"This is a folder. Press ENTER to open it."` — status/error
  messages for the info panel, entirely unimplemented.

`rbuf` (`char [129]`, live lines 589-599) is almost certainly the buffer used to format one of
these status/error strings before display (129 bytes matches a message buffer, not a filename).
`is_dir` (`int`, live lines 460-538) is used across the directory-listing loop — a boolean/marker
distinguishing directory entries, most likely tied to the `"  %c %s"` / `"> %c %s"` format
strings at lines 525/534 (the marker character `%c` is very likely derived from `is_dir` and/or
selection state), not simply `post->directory` as currently modeled.

## A structural warning, not just a size gap

Spot-checking one call our current source *does* already have an equivalent for shows the
**arguments themselves differ**, not just presence/absence: our line ~460 calls
`set_clip_rect(bmp, x + 10, y + 35, x + 185, y + 300)`, but the historical call at source line 509
(offset 915) decodes to `set_clip_rect(bmp, x + 6, 0, x + 290, bmp->h - 1)` — different constants
entirely. This means the existing partial reconstruction is not simply missing statements; parts
of what it already has may be approximated/wrong, not just incomplete. A correct fix needs a
line-by-line rebuild against the evidence above, not a patch of the two named locals alone.

## Why not attempted this round

The scope (roughly 1379 bytes, an entire results-table header/row-formatting block plus several
status messages, plus at least one already-present call with wrong constants) is substantially
larger than any single statement-level fix done this session, and mis-transcribing any of the
many `textout_ex`/`textprintf_ex` argument lists here (12+ new call sites, several string
literals, unresolved field offsets for the results columns) risks writing confidently-wrong code
rather than a real fix. Recording the location and evidence here rather than guessing, per the
project's "don't invent code" rule.

## Status

`draw_replay_selector` remains `DIFFER`, unchanged (byte-identical retained body), 2347/3726.
Both missing locals (`is_dir`, `rbuf`) are now located to specific line ranges and cross-referenced
against concrete call sites/string literals above, ready for a focused reconstruction pass.
