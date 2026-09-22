# `handle_player_collision_vector` geometry-recovery finding (parked: register-scheduling class)

Target: `handle_player_collision_vector` (`src/main.c`, historical `0x408d08..0x409137`, 1071 bytes).
Body file: `docs/attempts/game-main/bodies/handle_player_collision_vector.c`, left in the evidenced,
renamed state described below (1007 bytes, 64 under target). No `src/**` edited, no commits made.
`_vector_2` was not started.

## What `unused_locals.py` flagged, and what confirmed `line_intersect` gave for free

Sixteen DWARF locals initially unnamed. `function_lines.py game-main handle_player_collision_vector
--calls-by-line` confirmed two `line_intersect` calls (source lines 3056/3057) — its own function
definition is real (`src/main.c:2987`), not inlined. `ilx`/`ily`/`irx`/`iry` are directly the `&ix`/`&iy`
out-params of those two calls (`ilx`/`ily` from the first, `irx`/`iry` from the second) — read off the
call sites, not inferred.

## The evidenced locals, same shape as `handle_player_collision_combo`

`docs/current/function-evidence/main/handle_player_collision_vector.json`:

- `plx1` = fixed slot `-0x54(%ebp)` — `(int)ply[player_id]->x - 11`
- `plx2` = location list (register-resident, `edx` over its live range) — `lastX - 11`
- `prx1` = fixed slot `-0x50(%ebp)` — `(int)ply[player_id]->x + 11`
- `prx2` = fixed slot `-0x44(%ebp)` — `lastX + 11`
- `ply1` = location list, `DW_OP_reg7` (`edi`) — see below, this is the register-scheduling lead

Same deferred-conversion idiom as `_combo`: `(double)ply[player_id]->x` is loaded and cached
(`fstpl -0x50(%ebp)`, function-offset 29-46) long before `plx1`/`prx1` are actually computed by
converting that cached double (offset 151-195, after the `getFloorData` retry block). `ply[player_id]`
itself has no DWARF location either (same as `_combo`'s `p`) — every field access is a fresh
`ply[player_id]->` dereference, no cached pointer.

## The four with no location — resolved by reading, not guessing

`fy2`, `ply2`, `pry1`, `pry2` carry no `DW_AT_location`, matching `_combo`'s same four names. Traced
the two `line_intersect` call-argument builds directly (raw instruction dump, function-offset
222-276 and 283-346):

- `by` (arg4, call 1) = `mov %ebx,0xc(esp)`; `ay` (arg2, call 1) = `mov %ebx,%eax` then
  `mov %eax,0x4(esp)` — **the same `ebx`**, which holds `fy1` (set at offset 127 right after the
  `getFloorData` sentinel check), used twice with zero intervening writes anywhere in the function.
- `cy` (arg6) for **both** calls is the same `edi`, holding `ply1`.
- `dy` (arg8) for **both** calls is the same `esi`, holding the `lastY` parameter cached once in the
  prologue (`mov 0xc(%ebp),%esi`, offset 12).

So `fy2`/`ply2`/`pry1`/`pry2` are not separate writes at all — the calls reuse `fy1`/`ply1`/`lastY`'s
existing registers directly, which is exactly why there is no location to record. Implemented this way
(no copy variables, direct reuse in the call argument lists) and it is reflected in the current body
file. This same proof almost certainly applies to `_combo`'s identical four names; noted in
`handle_player_collision_combo-finding.md` as the next concrete step there.

## Measurements (fresh `tu_context_probe.py` labels each run, `--order historical`, `losses` clean/unchanged throughout — same pre-existing baseline set as every other function measured this session)

| variant | candidate size | delta from 1071 |
|---|---|---|
| baseline (unnamed: `floor_y`/`floor_x1`/`floor_x2`/`left_x`/`left_y`/`right_x`/`right_y`/`current_x`/`current_y`, cached `Tplayer *p`) | 1021 | -50 |
| renamed to DWARF names, `p` removed, `plx1`/`ply1`/`plx2`/`prx1`/`prx2` materialized at their evidenced position, `fy2`/`ply2`/`pry1`/`pry2` reused directly (no copies) | 1000 | -71 |
| + `ply1` computed once early (`ply1 = (int)ply[player_id]->y;` before `getFloorData`, then reused as `getFloorData`'s argument, then `ply1 = ply1 + 1;` after) instead of two separate casts | 1007 | -64 |

Same "more correct, fewer bytes" shape the coordinator identified in `_combo` — not read as evidence
the renaming/evidence work is wrong.

## The register-scheduling lead (the one attempt made, did not close)

Diffing 1000-byte variant against the original showed our candidate doing a full inline
float-to-int conversion for `(int)ply[player_id]->y` directly at the `getFloorData` argument-building
site, discarding the converted value, and presumably reconverting fresh later for `ply1`'s `+1`. The
original instead converts `y` once, early, into a register that survives unclobbered across the
`getFloorData` call and is reused for `ply1` later — confirmed by decoding `ply1`'s own DWARF location
list directly: `DW_OP_reg7` (`edi`) across two ranges, function-offset `[186,426)` and `[428,985)` (CU
base `0x406960`, function VA `0x408d08`, entries from `docs/current/function-evidence/...json`'s
`location_list`) — i.e. `edi` carries `ply1` for nearly the entire rest of the function, starting right
at the `inc %edi` that finalizes the `+1`. The earlier, pre-increment use of that same physical register
(as `getFloorData`'s `cy` argument, offset 102) is anonymous in DWARF — it belongs to `ply1`'s value but
before `ply1`'s own recorded range begins.

Tried writing this as a single named value computed once and reused (`ply1 = (int)ply[player_id]->y;`
before the `getFloorData` call, `getFloorData(&map, ply1, ...)`, then `ply1 = ply1 + 1;` afterward,
reusing `ply1` itself as both the raw and incremented value since it is the only DWARF name available
for it) instead of two independent `(int)ply[player_id]->y` casts. This moved the size from 1000 to
1007 — a small improvement, not a close. Did not chase further variants (e.g. a genuinely separate
unnamed local for the pre-increment value, which DWARF doesn't evidence and which the rules disallow
inventing) — one attempt was the budget for this lead, per instruction, and it did not resolve the gap.

## Prologue check

Confirmed before measuring byte counts, both variants: `push %ebp; mov %esp,%ebp; push %edi; push
%esi; push %ebx; sub $0x8c,%esp` (baseline) narrowing to `sub $0x7c,%esp` in the renamed variant purely
from fewer locals needing stack space — same callee-saved set (`edi, esi, ebx`) as the original in
every variant. Not the cause of the remaining gap.

## Current state and disposition

Left at the 1007-byte state (renamed to DWARF names, all 16 evidenced locals either given real slots
or proven-and-reused via register-argument tracing, no invented copies). `unused_locals.py` reports
only the same 4 no-location names as "unmentioned" — expected, since they are correctly represented by
direct reuse rather than a redundant statement, matching the original's own shape.

This is the third function this session landed in the same class as `load_character` and
`handle_player_input`'s prior parked issues, and the fourth overall counting `_combo`: **a
register-scheduling / value-lifetime difference (GCC deciding whether to cache a converted value across
a call site versus reconverting) that source-level statement shape alone did not close in one
attempt.** Per instruction, stopping here rather than grinding further; `_vector_2` (same family plus
`line_intersect`'s intersection points, which should carry over directly from this file's proof
technique) was not started this session.
