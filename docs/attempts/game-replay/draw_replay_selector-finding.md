# `draw_replay_selector` — recorded finding, with decoded call-site evidence

`draw_replay_selector` (`src/replay.c`, currently lines 431..514) is 2347 of 3726 historical
bytes. Retained body: `docs/attempts/game-replay/bodies/draw_replay_selector.c` — reverted to a
byte-identical copy of `src/replay.c` after this round's attempt regressed the measured size (see
"What was tried" below); **no change is currently in the body file**. `unused_locals.py`: 15 DWARF
locals, 2 never mentioned (`is_dir`, int, lines 460-538; `rbuf`, char[129], lines 589-599).

This update replaces the previous version of this file: that version only located the gap by
string literal and call name. This version decodes the actual arguments of every call site from
`460` through `559` mechanically (stack-store reads immediately before each `call`, resolved
through `function_data_refs.py`), per the coordinator's method. Lines `562` through `605` are
listed with call names only — not yet decoded to exact arguments — and are the next work.

## Decoded call sites, in historical line order

Struct layout used below (from `src/replay.c:27-36`):
`Treplay_post { char *full_path; char directory; char parent; char reserved[2]; int version; int score; int floor; int combo; }` — `directory` at offset 4, `parent` at offset 5, matching `add_itr_file`'s existing use of both fields.

- **462**: `fh = text_height(font);` — already correct in current source.
- **465/466**: `fg = makecol(25,25,25); mg = makecol(85,85,85);` — already correct.
- **467**: `view_percentage` clamp — already correct (the `fld1`/`fucom` sequence is the `> 1.0f` clamp fused with the division).
- **473**: `if (data && data[86].dat)` test — already correct (`0x560/0x10 = 86`, confirms the index).
- **476/477**: `set_trans_blender(0,0,0,150); drawing_mode(DRAW_MODE_TRANS,0,0,0);` — already correct.
- **479**: the two `rect()` calls — already correct.
- **487**: `solid_mode();` — already correct.
- **490** (offset 685-756, `_textout_ex`): `textout_ex(bmp, data[51].dat, "SELECT REPLAY", x + 10, y - 12, -1, -1);`
  Slots: `0=bmp, 4=data[51].dat (0x330/0x10=51), 8="SELECT REPLAY", 0xc=x+10, 0x10=y-12, 0x14=-1, 0x18=-1`.
  Not present in current source at all.
- **491/492/493/495/498/501/504**: a `sort_method` (global at `0x4bdd60`, declared `src/replay.c:25`)
  switch selecting between four (x,y)-pairs read from `data[N].dat` at offsets `0x730/0x720/0x740/0x710`
  (i.e. `data[115]/data[114]/data[116]/data[113]`, since `0x730/0x10=115` etc.) — almost certainly
  positioning a "which column is the active sort" highlight box under the NAME/SCORE/FLOOR/COMBO
  header (decoded below at 555-559). **Not decoded to a specific statement** — the four cases'
  exact x/y pairing to the header columns needs one more pass; flagging rather than guessing.
- **509** (offset 915-976, `_set_clip_rect`): `set_clip_rect(bmp, x + 6, 0, x + 290, bmp->h - 1);`
  Slots: `0=bmp, 4(x1)=x+6, 8(y1)=0, 0xc(x2)=x+0x122=x+290, 0x10(y2)=bmp->h-1` (bmp->h read via `0x4(edx)`).
  Current source has `set_clip_rect(bmp, x+10, y+35, x+185, y+300)` — **wrong on all four
  arguments**, confirmed by direct comparison of the constants.
- **510/514**: loop bounds (`i < num_itr_files && i < offset + max_posts`) — matches current
  source's shape reasonably; not re-verified in detail this round.
- **516** (offset 1312-1331): `Treplay_post *post = &file_list[i];` then `if (post->parent)` —
  `cmpb $0,0x5(edx)` tests offset 5 = `parent`, **not** `directory` as current source assumes.
- **517** (offset 1128-1146, `rep movsb`): `strcpy(dest, ".. (parent directory)")` — a raw 22-byte
  copy into the buffer at `-0x42c(%ebp)`, later proven (via its reuse at 591/594/597, offset
  `-0x418(%ebp)`) to be `rbuf`.
- **519** (offset 1331-1371, `_get_filename` + `_strcpy`): `strcpy(rbuf, get_filename(post->full_path));`
  — confirms `rbuf` (not a bare `char *name`) holds the display name; current source uses
  `char *name = get_filename(...)` directly, which is the wrong shape (no buffer, no `is_dir`).
- **521** (offset 1146-1150/1371-1375, `movsbl 0x4(%edx),%esi`): `is_dir = post->directory;`
  (offset 4, sign-extended byte) — this is the named-but-missing local.
- **523** (offset 1150-1159/1375-1384): `if (i == selection)` selects between the two textprintf_ex
  calls below (525 unselected / 534 selected) — does **not** gate a `rectfill` highlight; no
  `rectfill` call appears anywhere in the loop's instruction range, so the current source's
  `if (i == selection) rectfill(...)` selection-highlight statement does not correspond to any real
  instruction and should be removed, not kept.
- **525** (offset 1159-1252 + 2940-2956, `_textprintf_ex`, unselected row): two predecessors, one
  hardcoding `'}'` + color `mg` (is_dir true), one hardcoding `'{'` + color `fg` (is_dir false),
  merging into one call: `textprintf_ex(bmp, font, x+8, row, is_dir ? mg : fg, -1, "  %c %s", is_dir ? '}' : '{', rbuf);`
  Slots: `0=bmp,4=font,8=x+8 (-0x43c, set once at function start to x+8),0xc=row (-0x428, a running
  accumulator incremented by fh each iteration — not verified to have exactly the same base
  constant as the current `y + 40 + (i-offset)*fh` formula, but no counter-evidence either),
  0x10=color,0x14=-1,0x18=fmt,0x1c=marker char,0x20=rbuf`.
- **534** (offset 1532-1618, `_textprintf_ex`, selected row): always color `mg` regardless of
  `is_dir`: `textprintf_ex(bmp, font, x+8, row, mg, -1, "> %c %s", is_dir ? '}' : '{', rbuf);`
  Same slot layout as 525.
- **546** (offset 1726-1737): `if (rep) {` — matches current source.
- **547** (offset 1737-1754, `_is_custom_replay`): `isCustom = is_custom_replay(rep);` — matches
  current source.
- **551** (offset 1754-1846 + 2956-2996, `_text_length` + `_set_clip_rect`): two predecessors
  merge into `set_clip_rect(bmp, x+6, 0, x+390 - (isCustom ? text_length(font, "CUSTOM GAME  ") : 0), bmp->h-1);`
  (`x+390` from `-0x460`, set at line 486 to `x+0x190=x+400`, minus 10; the isCustom arm measures
  `text_length(font, "CUSTOM GAME  ")` and subtracts it from that same x2 before calling
  `set_clip_rect`; the non-custom arm subtracts 0). Not present in current source.
- **552** (offset 1846-1945 + 3572-3587, `_textprintf_ex`): `rep->comment` (tested at `-0x448`) is
  printed via `"%s"`, falling back to the literal `"n/a"` when falsy — the assignment site of
  `-0x448` to `rep->comment` itself was not directly captured in this pass (only its later test and
  the `"n/a"` fallback are confirmed); `textprintf_ex(bmp, font, x+10, y+315, fg, -1, "%s", rep->comment_or_na);`
  Slots: `0=bmp,4=font,8=x+10(-0x444, set once at 490 to x+10),0xc=y+315(-0x430, set at 552's own
  head to y+0x13b=y+315),0x10=fg,0x14=-1,0x18="%s",0x1c=comment-or-"n/a"`.
- **555-559** (`_textout_ex`/`_textout_right_ex` × 5): a column header row, all at `y+335`
  (`-0x438` slot reused as the row's own y here — actually a **fresh** `ebx = y+0x14f = y+335` set
  at 555's own head, not the same slot as 551's clip bound):
  - 555: `textout_ex(bmp, font, "NAME", x+10, y+335, fg, -1);`
  - 556: `textout_right_ex(bmp, font, "SCORE", x+180, y+335, fg, -1);` (`x+0xb4`)
  - 557: `textout_right_ex(bmp, font, "FLOOR", x+230, y+335, fg, -1);` (`x+0xe6`)
  - 558: `textout_right_ex(bmp, font, "COMBO", x+280, y+335, fg, -1);` (`x+0x118`, also cached for
    reuse — see 569 below)
  - 559: `textout_ex(bmp, font, "DATE ", x+300, y+335, fg, -1);` (`x+0x12c`, also cached — see 573)
  None of these five calls, nor the table they head, exist in current source at all.

## Not yet decoded (call names only, from `function_lines --calls-by-line`)

- **562-569**: `set_clip_rect`, then a `textprintf_ex("%s", ...)` for a name-like column value, then
  `set_clip_rect` again, then three `textprintf_right_ex` calls reading `rep` at struct offsets
  `0x50/0x54/0x58` with formats `"%6d"/"%4d"/"%3d"` (score/floor/combo values under the 556-558
  headers), then a final `textprintf_ex` with `"%s "`. The x-positions for 566/567/568/569 reuse
  the cached `-0x428`/`-0x424` slots from 558/559 above (confirmed by inspection, not yet reduced
  to exact expressions).
- **572/573**: a test (`-0x42c`, reused yet again) selecting between the plain per-row table and a
  `"CUSTOM GAME"` (no trailing spaces, different literal from the 551 label) via
  `textprintf_right_ex`.
- **576/577**: `rep->comment` displayed a second way (`0xa8(%ecx)` field test, `textprintf_ex("%s", ...)`)
  — possibly a per-*entry* comment in the table rather than the single `rep`'s comment at 552;
  needs its own trace.
- **583-599**: three status/warning messages sharing the `rbuf` buffer (`-0x418`/`-0x42c` again,
  confirming `rbuf` is reused a third time here, not just for loop rows and not just for one
  message): `"You need Icy Tower 1.2 to view this replay."`, `"You need Icy Tower 1.3 to view this
  replay."`, `"Replay is broken."`, selected by comparing a stored value at `-0x450` against `1`
  and `0x82` (both from `get_replay_property`-style version codes, plausibly `selected_version`).
  The third (`"Replay is broken."`) is drawn via `textout_ex` with a `makecol(20,20,80)` (an
  additional color not yet named) rather than `fg`.
- **585**: `"This is a folder. Press ENTER to open it."` — separate hint, own `textout_ex` call,
  color `fg`.

## What was tried this round, and why it was reverted

Implemented lines 490, 509, 516/517/519/521/523/525/534, 546/547/551/552, 555-559 exactly as
decoded above, removed the current source's three statements that don't correspond to any real
instruction (the `"REPLAY SELECTOR: %s"` header — that string does not exist anywhere in
`function_data_refs`' output; the `"Select a folder or replay"` line; the `"Enter: select   Del:
delete   Esc: back"` line — none of these three literals appear in the function's real string
table at all). Measured incrementally (`rs-3` through `rs-6`): the total went **2347 → 2308 → 2268
→ 1926**, a regression, not an improvement, even though every individual statement added is
directly evidenced. Per-line `--annotations` measurement showed the newly-added lines landing
close to their historical byte counts (e.g. 517, 546, 490, 509, 556, 557 exact or near-exact), but
the function's overall stack frame collapsed from `sub $0x49c,%esp` (1180 bytes, matching history)
to `sub $0x11c,%esp` (284 bytes) — GCC eliminated `curr_filename[1024]` and large amounts of
surrounding stack once it saw those bytes were provably unused by the (now smaller) function,
which is expected but means **partial implementation actively regresses this function**: adding
correct pieces while leaving other real locals (the not-yet-decoded 562-577 table and 583-599
warnings) completely absent lets the compiler shrink the frame in a way that won't happen once the
missing statements are filled in too. Reverted to the byte-identical baseline (`rs-6`: confirmed
2347/3726) rather than leave a worse-measuring state, per the project's standing rule against
leaving regressions in place.

## Recommendation for the next pass

Implement the "not yet decoded" section (562-599) using the same mechanical method before
re-measuring — the frame-collapse problem means partial credit doesn't show up in the byte count
until the whole function's real locals are back in use, so the next attempt should decode the
remaining ~40 lines fully, write everything in one pass, and only then measure. All of the
groundwork (stack slot roles: `-0x42c`/`-0x418` = `rbuf`'s two aliases, `-0x428`/`-0x424` = cached
column x-positions from the header row, `-0x448` = `rep->comment`-or-"n/a", `-0x450` = the
version-code selector for the three warning messages) is recorded above.
