# `do_replay_menu` progress: 8/9 locals evidenced and named; the real 502-byte gap located but not yet safely fixed

Target: `do_replay_menu` (`src/main.c:2397`, historical `0x410f98..0x4119fd`, 2661 bytes). Body file:
`docs/attempts/game-main/bodies/do_replay_menu.c`. No `src/**` edited, nothing committed.

## Locals resolved (8 of 9, all decoded from DWARF, not guessed)

Decoded every location list directly (CU base `0x406960`, function VA `0x410f98`, entries from
`docs/current/function-evidence/main/do_replay_menu.json`):

- `fname`=`-0x218(%ebp)`, `pname`=`-0x418(%ebp)`, `fpath`=`-0x818(%ebp)`, `buffer`=`-0x1018(%ebp)`,
  `lastGameFile`=`-0x1818(%ebp)` (its second DWARF entry reuses `buffer`'s `-0x1018` slot in a later,
  non-overlapping scope) — all fixed-slot matches to our pre-existing `filename`/`player_name`/
  `full_filename`/`replay_filename`/`temporary_filename`. `comment` already matched DWARF's own name
  (not flagged missing). Renamed accordingly; **`buffer` resized from `[2048]` to `[1024]`** to match
  its DWARF type exactly (it only ever holds `replace_extension()`'s output, bounded by `fname`).
- `status` — register `edi`, live almost the entire function (func-offset `[101,2661)` with gaps) —
  the save-dialog state machine (0/1/2/3/`'*'`), previously our `state`.
  `action` — register `edi`/`eax`, short bursts right after each `get_string()` call
  (`[1164,1181)`, `[1578,1595)`, `[1606,1634)`, `[1862,1874)`, `[2015,2040)`, `[2302,2315)`) — the
  **separate** captured return value of `get_string()`, distinct from `status`. Our prior source
  reused `state` itself as that temporary (`state=get_string(...); ...; state++;`), collapsing two
  DWARF-distinct values into one. Fixed: introduced `action`, used it for all three `get_string()`
  calls (`status==0`, `status==1`, `status==2` cases) instead of overloading `status`, and fixed the
  `status==0` completion to match the actual instructions (`action++; if (!action) status='*'; else
  status=1;` — the original hard-codes `1` there via `mov $0x1,%edi`, not a copy of `action`, which I
  had wrong in an earlier draft and corrected).
- `thisChecksum` — register `eax`, right after `calc_replay_checksum()`. Was inlined
  (`if (calc_replay_checksum(demo)!=uberChecksum)`); now captured explicitly.

`lets_save` (int) has **no `DW_AT_location`** — same no-evidence class documented for `_combo`'s
`fy2`/`ply2`/`pry1`/`pry2` and `init_game`'s `black`. It almost certainly names the
`!my_alert("The file exists.","Do you want to overwrite it?",1,0)` result already inlined in the
`if (exists(fpath) && !my_alert(...))` condition, but there is no register/slot evidence for a
materialized value, so — per this session's established rule — I did not invent a variable for it.
It's named only in this file's prose and the body's header comment, not as a declared C local.

`unused_locals.py`: 9/9 "mentioned" (8 as real declared locals with evidence, `lets_save` only in
comment text — flagged as a caveat, not claimed as fixed).

## Measurement: renames cost nothing, as every time before

Fresh `tu_context_probe.py` labels (`drm-1` baseline, `drm-2` after all renames + `action`/
`thisChecksum` introduced), `--order historical`, `losses` clean/unchanged throughout.

| variant | candidate size | delta from 2661 |
|---|---|---|
| baseline (unnamed) | 2159 | -502 |
| all 8 evidenced locals renamed/introduced correctly | 2159 | -502 |

Zero byte movement, consistent with every rename this session — expected, and per your caution about
intermediate reads, I did not stop here assuming it meant the renames were wrong; I went looking for
the actual missing statements next.

## The real gap, located: the original draws the three save-dialog slots nine times, ours draws them three

Counted `drawSlot` calls directly in both objects: **original has 9, candidate has 3** (one call per
slot — "Your name"/"Filename"/"Comment: (optional)" — times three separate compiled locations in the
original, versus our single top-of-loop draw call site producing one compiled instance of each, run
repeatedly by the loop). `blit_to_screen` appears twice in the original (not three times), and
`stretch_sprite` once.

Traced where the two extra copies live and what reaches them (raw instruction dump, function-relative
offsets, `objdump`/`original_slice`):

- Copy 2 (historical lines ~5537-5539, offsets 1192-1424): reached by **direct fallthrough**, not a
  jump, from the end of the `status==0` (`get_string` on `pname`) handling. The instruction sequence
  is `inc %edi; je 0x4116d4 (offset 1852, sets edi='*' and jumps to offset 1856); mov $0x1,%edi` and
  then falls straight into copy 2's `makecol`/`drawSlot` sequence with no intervening jump. Copy 2
  ends with `jmp 0x41116c` (offset 468) — the outer loop's **condition check** (`closeButtonClicked`
  / `status=='*'` test), not the exit path.
- Copy 3 (historical lines ~5581-5584, offsets 1606-1852): ends the same way, `jmp 0x41116c` after its
  own `blit_to_screen`, following a comparable "just finished handling one state" completion (evidence
  gathered but the exact trigger point — which state's completion reaches copy 3 rather than copy 2 —
  I did not nail down with full confidence before time ran out on this pass).

Both copies jump back to the **loop-condition check**, not straight to the loop's normal top-of-body
draw block (which sits just after that check, at offset 490). If the condition still holds, control
falls through into the normal top-of-body draw again immediately afterward — meaning, at face value,
these extra copies redraw the *pre-transition* slot contents once, are immediately overwritten by the
next natural iteration's draw, and produce a visible frame that most likely reads as one blit
double-buffered before the "real" redraw. I could not conclusively determine from the disassembly
alone whether this is a genuine, deliberate one-frame-early redraw in the original source (matching a
`status`-transition-triggered explicit redraw pattern I have not fully reconstructed) or a mechanical
compiler duplication unrelated to source-level intent — and additional instances of the same
constructs elsewhere in this session's collision-handler and `_mangled_main` work turned out to be the
latter class, not statements to add.

**I did not attempt to add these draw calls to the source.** Getting the trigger condition wrong would
add invented statements that happen to move the byte count without being what the original actually
does — precisely the failure mode you flagged this session (`draw_replay_selector`, the fourteen-
statement block removed from `play`). This is reported as a located, high-confidence lead (9 vs 3
`drawSlot` calls is unambiguous, mechanical evidence of missing statements, not scheduling) rather than
a completed fix. The next step is pinning down exactly which `status` transition's completion reaches
copy 3 (I have copy 2's trigger nailed down; copy 3's is not yet confirmed) before writing the
duplicated draw calls into source.

## Current state

Body file left with 8/9 locals correctly evidenced and renamed (`status`/`action` separated correctly,
`buffer` resized to its true DWARF size, `thisChecksum` captured), `lets_save` documented but not
invented. Compiles clean, `2159/2661` unchanged from baseline (as expected for a pure-naming pass),
`losses` clean, nothing committed, `src/**` untouched.
