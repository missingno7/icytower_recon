# `replay_selector` — recorded finding, with decoded evidence for both draw calls

`replay_selector` (`src/replay.c`, currently lines 602..773) is 1902 of 2845 historical bytes.
Retained body: `docs/attempts/game-replay/bodies/replay_selector.c`, currently a byte-identical
copy (no changes made — not attempted this round, given the regression risk demonstrated on
`draw_replay_selector` from partial implementation; see that finding file). `unused_locals.py`: 16
DWARF locals, 2 never mentioned (`i` — block not resolved to a line range; `p`, char[1024], lines
786-806).

This update replaces the previous version, which only noted that a second `draw_replay_selector`
call site existed. This version decodes both call sites' full argument lists mechanically
(`function_lines --source-view 899 921`).

## The two `draw_replay_selector` calls, decoded and compared

Both calls share the exact same seven-argument slot layout
(`draw_replay_selector(BITMAP *bmp, Treplay *rep, Treplay_post *file_list, int selection, int offset, int max_posts, int x, int y)`),
confirmed by identical stack-store offsets (`0x1c/0x18/0x14/0x10/0xc/0x8/0x4/0`) at both sites —
**but two of the eight arguments differ between the two calls**:

| slot | arg | call @899 (existing, line 756-757 in our source) | call @918 (missing) |
|---|---|---|---|
| 0 | bmp | `swap_screen` | `swap_screen` (same) |
| 4 | rep | `-0x428(%ebp)` (our `rep`) | **literal `0` (NULL)** |
| 8 | file_list | `itr_file_list` | `itr_file_list` (same) |
| 0xc | selection | `-0x430(%ebp)` (our `curr_file_id`) | `-0x424(%ebp)` — a **separate** local, set at line 902 (`894 mov -0x430(%ebp),%edx; 900 mov %edx,-0x424(%ebp)`) to a snapshot of `curr_file_id`'s value *before* the `rest(2)`-based wait loop that follows |
| 0x10 | offset | `-0x438(%ebp)` (our `offset`) | same slot (same) |
| 0x14 | max_posts | `-0x440(%ebp)` (our `page_size`) | same slot (same) |
| 0x18 | x | `0x78` (120) | `0x78` (120, same) |
| 0x1c | y | `%ebx` | `%ebx`, but **recomputed by a different formula between the two calls** (see below) |

So the second call draws with **`rep` forced to NULL** (no info panel, matching
`draw_replay_selector`'s `if (rep) {...}` guard) and a **frozen copy of `curr_file_id` taken before
a wait**, not the live value — consistent with a "draw the previous frame's list while something
animates" second pass, not a duplicate of the first.

## The `y` (`ebx`) recomputation between the two calls (lines 906-908)

Before the second call, `ebx` (the row position) is only updated when a guard passes:
```
906: if (ebx > 0x1f3 /* 499 */) goto skip;        /* cmp $0x1f3,%ebx; jg ... */
907: cycle_count = 0;
908: ebx = (int)(0.2 * (0x1fe /* 510 */ - ebx) + ebx);   /* fldl 0.2; fimul; fiadd; fistp */
```
This is a **different interpolation** from the `pageY -= (pageY - targetY) / 3 + 1;` formula our
current source already has for the *first* call's `y`: a linear-interpolation-toward-510 (with a
guard `ebx <= 499`) rather than a fixed /3+1 step toward `targetY`. This strongly suggests the
second `draw_replay_selector` call animates toward a **different target** than the first (510, not
`targetY`), consistent with a two-layer transition effect (an outgoing panel sliding toward one
position while an incoming one — or the reverse — targets another). The exact source variable this
maps to (is it reusing `pageY` a second time, or a distinct local?) was not resolved this round.

## Surrounding blit/blend sequence (lines 911-916), decoded

```
911 (_blit):            blit(-0x43c(%ebp) /* == bg, per line 892's own blit target */, swap_screen,
                              0, 0, 0, 0, 0x280 /* 640 = SCREEN_W */, 0x1e0 /* 480 = SCREEN_H */);
913 (_set_trans_blender): set_trans_blender(0, 0, 0, (0x1f4 /* 500 */ - ebx) / 3);
914 (_drawing_mode):     drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);
915 (_makecol + gfx_driver test): color = makecol(0, 0, 0);
                              if (gfx_driver) { edi = gfx_driver->w (0x70); esi = gfx_driver->h (0x6c); }
                              else { edi = 0; esi = 0; }
916 (_solid_mode):       solid_mode();
```
Line 915's `edi`/`esi` (driver w/h, or 0/0) are presumably the `rectfill` bounds for the second
blend pass (paralleling the first pass's `rectfill(screen, 0, 0, SCREEN_W, SCREEN_H, makecol(0,0,0))`
at our current line 754) — the actual `rectfill` call using them was not captured in this
source-line range and needs one more `--source-view` pass just past line 916.

## Why not attempted this round

`draw_replay_selector`'s attempt this session showed that implementing *some* of a function's
missing statements while leaving others absent can *regress* the measured byte count (the compiler
shrinks the stack frame once it sees other locals still unused), so a partial implementation here
carries the same risk without more of the surrounding context decoded (particularly: what exactly
`-0x424`, the second `y` target, and the rectfill bounds resolve to in source terms). Recording the
decoded evidence above rather than guessing the remainder.

## Status

`replay_selector` remains unchanged, `DIFFER`, 1902/2845. The second `draw_replay_selector` call's
full argument list is now fully decoded (rep=NULL, selection=a pre-wait snapshot, y=a
0.2-interpolation-toward-510 rather than the existing `/3+1` formula) and is ready to implement in
one pass alongside the surrounding blit/blend/solid_mode sequence, once lines 916 (the second
rectfill) and the still-unlocated `i`/`p` are resolved.
