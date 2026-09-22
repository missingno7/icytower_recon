# `handle_player_collision_combo` geometry-recovery finding (dead end, reverted)

Target: `handle_player_collision_combo` (`src/main.c`, historical `0x408358..0x4088c8`, 1390 bytes).
Body file: `docs/attempts/game-main/bodies/handle_player_collision_combo.c`, currently reverted to the
1381-byte baseline (9 under target, unchanged from before this investigation). No `src/**` edited, no
commits made.

## What `unused_locals.py` flagged

Nine DWARF locals never named in our source: `fy2`, `plx1`, `ply1`, `plx2`, `ply2`, `prx1`, `pry1`,
`prx2`, `pry2`.

## The four with real evidence

Decoded directly from `docs/current/function-evidence/main/handle_player_collision_combo.json` and the
original disassembly (`function_lines.py --source-view`):

- `plx1` = `DW_OP_breg5 -96` = `-0x60(%ebp)`
- `plx2` = `DW_OP_breg5 -88` = `-0x58(%ebp)`
- `prx1` = `DW_OP_breg5 -80` = `-0x50(%ebp)`
- `prx2` = `DW_OP_breg5 -68` = `-0x44(%ebp)`

All four are fixed stack slots (not location lists), each written exactly once, at function-relative
offset 423-497 — right after the floor-data retry block (line ~3207) and before the `debug` check
(line 3211). The write instructions read from **doubles cached at function entry**: `(double)ply[player_id]->x`
is loaded and stored to `-0x58(%ebp)` at offset 12-26 (tagged source line 3160), and
`(double)ply[player_id]->y` to `-0x50(%ebp)` at offset 29-32 (line 3161) — long before `makecol`/`is_solid`
run. The actual int conversion (fistpl through the FPU control-word dance) and the `-11`/`+11` arithmetic
happen much later, reusing those cached doubles. This is a genuine deferred-conversion idiom, not an
artifact of our reconstruction: **evidenced**, not inferred.

Values: `plx1 = (int)ply[player_id]->x - 11`, `ply1 = (int)ply[player_id]->y + 1`,
`plx2 = lastX - 11`, `prx1 = (int)ply[player_id]->x + 11`, `prx2 = lastX + 11`.

## The four with no evidence

`fy2`, `ply2`, `pry1`, `pry2` carry **no `DW_AT_location` at all** in the original — same "abbrev
without a location" pattern documented for `handle_player_collision_old`'s `dX` (see that body file's
header comment). A missing location means the debug info records nothing about where the value lived;
it does **not** mean the value equals another named variable. I initially inferred
`fy2 = fy1`, `ply2 = lastY`, `pry1 = ply1`, `pry2 = lastY` (trivial copies) purely from the fact that
`getFloorData`'s real signature (`src/map.c:105`, `void getFloorData(Tmap*, int cy, int*fy, int*fx1, int*fx2)`)
only produces one `fy`, so a level floor segment made `fy2 = fy1` look inevitable, and the right-edge
ray plausibly shares the left edge's `y` values. That was a guess from the names, not from the object —
see the update below.

**Update, from `handle_player_collision_vector` (same DWARF-name family, same missing four):** traced
the actual `line_intersect` call-argument construction there instruction by instruction instead of
inferring from names, and it answers this exact question. In `_vector`'s two `line_intersect` calls,
`by` (arg4) is built with `mov %ebx,0xc(esp)` and `ay` (arg2) with `mov %ebx,%eax` / `mov %eax,0x4(esp)`
— **the same `ebx` register, holding `fy1`, used twice with no intervening write anywhere in the
function**. `cy` (arg6) for both calls is the same `edi`, holding `ply1`. `dy` (arg8) for both calls is
`esi`, holding `lastY` straight from the prologue cache. So in `_vector`, `fy2`/`ply2`/`pry1`/`pry2` are
not separate written values at all, trivial-copy or otherwise — they are the call sites reusing
`fy1`/`ply1`/`lastY`'s existing registers directly, which is exactly why they have no `DW_AT_location`:
there is nothing to locate. This is very likely the same answer for `_combo` (same names, same
`getFloorData`/`line_intersect` shape), but it was not re-verified against `_combo`'s own disassembly
in this session — that verification, and testing it (removing the `fy2`/`ply2`/`pry1`/`pry2` locals
while reusing `fy1`/`ply1`/`lastY` directly in the `line_intersect` argument list rather than through
copy variables), is the next concrete step here rather than a fourth guess.

## Measurements (all with fresh `tu_context_probe.py` labels, `--order historical`, empty `losses` throughout — the pre-existing baseline noise `check_beta_tester, line_alert, show_instructions, start_reward, stopGameMusic, uninit_game` never changed across any variant in this file)

| variant | description | candidate size | delta from 1390 |
|---|---|---|---|
| baseline | no geometry locals named at all (inline expressions throughout) | 1381 | -9 |
| +4 evidenced, +4 inferred, geometry reused in both debug-draw and intersect calls | 1281 | -109 |
| +4 evidenced, +4 inferred, geometry only in intersect calls (debug block reverted to inline exprs) | 1337 | -53 |
| same, geometry placed at its true disassembly position (after floor retry, before debug check) | 1345 | -45 |
| same + `Tplayer *p` removed entirely (DWARF confirms `p` has no location either) | 1473 | +83 |
| same as 1345-variant + `if (solid1\|\|solid2){...return;}` rewritten as `goto solid_return;` to a block moved to function end | 1345 (not byte-identical: 364 vs 365 instructions) | -45 |
| **4 evidenced kept, 4 inferred REMOVED** (their use sites replaced with `fy1`/`lastY`/`ply1`/`lastY` directly) | **1325** | **-65** |

Removing the four inferred locals made the regression *worse*, not better — it did not recover the
1381 baseline, let alone approach 1390. This falsifies the specific "provable equality lets GCC fold a
branch" mechanism as I applied it (there is no `ply2 < pry2`-shaped comparison anywhere in this
function's source; the values only ever feed as opaque arguments into real, non-inlined function calls
— `line()` via an Allegro vtable indirect call, and `line_intersect()` via a normal direct call — so
there is no comparison for GCC to fold across in the first place). The deeper "never land a partial
write set" lesson (doc section 13) likely still applies, but not through that specific mechanism here:
whatever the four real writers of `fy2`/`ply2`/`pry1`/`pry2` are, they are not simple copies, and
guessing at them (with or without a copy) moves the function further from target either way.

**Read the three measurements together, not the reverted one in isolation.** 1381 with no geometry
locals named, 1345 with all eight (four evidenced + four inferred), 1325 with only the four evidenced
— fewer bytes as more correct statements are added, monotonically. That is not the geometry causing a
regression; it is the geometry removing duplicated inline computation (the same `(int)ply[player_id]->x
- 11` etc. recomputed at each of several call sites) that the unnamed-locals baseline was performing by
accident. The original computes each of these once too, and is nonetheless 1390 bytes. So the 45-to-65
byte gap was never explained by the baseline's duplication — that duplication was only standing in for
whatever code is genuinely still missing, and made 1381 look closer to 1390 by luck, not by
correctness. **The reverted 1381 state below is not a better reconstruction than the 1325 one; it is
only a luckier-looking byte count.** The real gap is elsewhere in the function (most likely inside
whatever `fy2`/`ply2`/`pry1`/`pry2` actually are, and/or the block-placement difference below), and it
should be chased from there, not papered over by reverting the correct geometry work.

## Block-placement attempt (`if` vs `goto`)

Rewrote `if (solid1 || solid2) { ...; return; }` as `if (solid1 || solid2) goto solid_return;` with
the body relocated to a label at the end of the function — the same shape (one physical block reached
by a forward jump) that fixed `handle_player_collision_old`'s duplicated-tail regression (961→910
there). Measured **no net size change** (1345 either way) and confirmed via raw instruction dump that
the two forms are not byte-identical (364 vs 365 instructions) — so the rewrite is not a no-op, but it
does not reproduce the original's layout. In the original, the `jne` at offset 287 (deciding whether
`solid1 + solid2 != 0`) jumps to offset 738 — the block's body is emitted nowhere near the branch site,
and the branch's fallthrough (the "no solid" path) continues immediately into the floor-data code with
nothing in between. In every candidate variant measured (both `if`-inline and `goto` forms), the block's
full body — including its own copy of the function epilogue (`add $0x9c,%esp; pop %ebx; pop %esi; pop
%edi; leave; ret`) — is emitted immediately after the branch, never relocated. The `if`-vs-`goto`
surface distinction controlled placement for `_old` because it eliminated real *duplication* (two
textually-identical blocks merging into one physical copy via a shared forward jump); here there was
never any duplication, so there was nothing for the rewrite to merge, and whatever heuristic (likely a
GCC static-branch-prediction / block-layout decision, not proven) drives the original's placement is
still unidentified.

## Prologue check (done first, as instructed)

Confirmed before measuring byte counts in every variant: prologue `push %ebp; mov %esp,%ebp; push
%edi; push %esi; push %ebx; sub $0x9c,%esp` — same callee-saved register set (`edi, esi, ebx`) and
same frame size (`0x9c`) as the original in every variant tried, including the reverted baseline. Ruled
out as a cause of any of the above deltas.

## Current state

Body file reverted to the exact 1381-byte baseline (verified via a fresh `combo-9` probe:
`orig 1390, cand 1381`, `status: DIFFER`, `compile: OK`, `losses` unchanged/clean). No locals named,
matching the state before this investigation began. `unused_locals.py` still reports the original 9
missing names. This is a documented dead end, not a fix: the four evidenced stack-slot locals
(`plx1`/`plx2`/`prx1`/`prx2`) and their deferred-conversion origin are solid and should transfer
directly to `handle_player_collision_vector`/`_vector_2` (same family). The four with no location
(`fy2`/`ply2`/`pry1`/`pry2`) remain unrecovered — their real definitions are still missing, and the
next attempt should look for what *reads* their registers/slots in the original rather than inferring
values from their names.
