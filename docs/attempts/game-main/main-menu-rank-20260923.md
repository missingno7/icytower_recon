# Main menu presentation recovery experiment

The production `main_menu_callback` contains an explicitly labeled invented welcome block and approximated head movement. The retained body in `main_menu_callback-rank-candidate.c` changes only those regions and the previously omitted mouse cursor selection. It is an evidence-backed candidate, not a match or a production replacement.

Original `main.c` line table and disassembly establish:

- Lines 5231–5232 call `textprintf_ex` twice with format `v%s %s`, version `1.5.1`, a suffix selected by `debug` (` FUN MODE` or empty string), positions `(5,3)` and `(4,2)`, and colors `(100,21,20)` and `(162,90,51)`.
- Lines 5236–5241 compare `profile->handle` with `guest`, call `get_rank_id`, build `Welcome, %s!` with the optional `Your rank is %s.` suffix, then call `get_rank` for each of four shadowed `textprintf_right_ex` draws. Lines 5244–5248 copy the 58-character guest welcome text and draw it four times. The exact strings are resolved from the original `.rdata` references.
- Lines 5176–5179 call `LoadCursorA(NULL, IDC_HAND/IDC_ARROW)` and store the result in Allegro's `_win_hcursor`. The overlay adds the vendored `aintwin.h` declaration without changing maintained headers.
- At line 5212 the first `_cos_tbl` lookup is `fixsin(itofix(count*3)+10)`. The second is `fixsin(itofix(count*5))`; its result is multiplied by 10 and rounded through `fixtoi`, then 16 is added. The former is multiplied by 5 for `rotate_sprite`'s angle. The first plane rotates `data[61]` into a 640×320 temporary bitmap at x=402, draws it translucently, and destroys it. The second plane repeats the lookups and rotates `data[58+face]` onto `swap_screen` at x=400 with a y offset of 12. These identities follow the actual `fmaths.inl` and `draw.inl` expansions and bitmap references.
- At function offsets 34–54, the face increment is conditional but the `face==3` reset is outside that condition. Moving the reset outside in the candidate reproduces the original initial instruction sequence through offset 72. The current production body incorrectly nests the reset.

Combined probe command, from the repository root:

`python tools/tu_context_probe.py game-main src/main.c takeover-rank-face-20260923 --order historical --body draw_frame=docs/attempts/game-main/draw_frame-merged.c --body play=docs/attempts/game-main/play-merged.c --body main_menu_callback=docs/attempts/game-main/main_menu_callback-rank-candidate.c --declarations docs/attempts/game-main/rank-declarations.json --focus main_menu_callback --focus run_demo --no-dumps`

The retained menu body compiles to 3,775 bytes against 3,741 original (production was 2,903). All historical direct call edges are present. It remains `DIFFER`; the frame allocation now agrees at `0x26c`, and the first differing byte is a relocation/data-layout field at offset 14. The first clear non-relocation instruction difference is near offset 72: the original keeps `pFLDAd` in `esi`, while the candidate initially uses `eax`. The whole TU still loses `run_demo`, so no integration was attempted. Earlier probes without cursor, fixed-point head motion, corrected bitmap planes, and face-reset ordering remain in the adjacent JSON records as negative evidence. The next useful pass should inspect the ad focus branch, declaration types, and remaining data ownership, then test whole-TU context again; changing downstream `run_demo` or manipulating the peephole cursor has no basis.

The overlay declares `get_rank(Tprofile *)` because that pointer type is available in `main.c`; `profile.c` defines it with `Tprofile_rank *`. Their argument ABI agrees, but this interface declaration is a candidate and still needs a type/topology reconciliation before production integration.
