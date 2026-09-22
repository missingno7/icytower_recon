# Annotation gaps in W2/W3/W4/W5 (play-regions)

Produced by a read-only sweep of `docs/attempts/game-main/play-regions/{W2,W3,W4,W5}.c` for the
line_budget.py annotation walker: any statement without its own `/* NNNN */` (or `/* line NNNN */`)
trailing comment inherits the previous statement's number, which can make present code measure as
"missing" (see W1b's `voice_stop` block, which cost ~36 phantom bytes this way) or silently misattribute
bytes to the wrong historical line. No source file listed here was edited -- this is a report only,
for each region's owner to triage. Line numbers below are **file-local** (the line number in that
region's `.c` file, not the historical main.c line).

Two caveats found while compiling this:
- A trailing comment with extra prose after a single number (e.g. `/* 3919: dec+je on diff... */`)
  appears to parse fine elsewhere in the tree (W1 has several and they measured correctly), so those
  are **not** flagged below -- only comments with *no* number, a `?` placeholder, or *two or more*
  numbers (a genuine range) are flagged as malformed.
- W1's `/* line 3692 */` experiment showed a **leading** comment (on its own line, directly above a
  multi-line statement) works, but moving that same annotation to a **trailing** position at the end
  of the statement broke tracking badly (-138 bytes on that one statement). Several of the entries
  below put the annotation on the *first* line of a multi-line statement/condition, trailing on that
  first line rather than leading on its own line -- this is a different, untested placement, flagged
  separately below so owners can decide whether to convert it to the confirmed-working leading form.

---

## W2.c

### No annotation at all
- 83: `if (stars[i].intensity)`
- 84: `update_particle(&stars[i]);`
- 102, 104, 106, 108: `scroll_acc++;` (bodies of the 3722/3723/3724/3725 one-line `if`s)
- 110, 112: `scroll_acc += 2;` (bodies of 3726/3727)
- 114: `scroll_acc += 3;` (body of 3728)
- 118: `tot_scroll = scroll_acc;` -- comment present but has no digit at all (prose only:
  "shares ecx with scroll_acc through the collision switch below...")
- 123: `clock_angle++;` (body of 3736's one-line `if`)
- 129: `fall_count = 0;` (sibling of line 128's annotated `clock_angle = 0; /* 3758 */`)
- 150: `hurry_y -= 2;` (body of 3765's one-line `if`)
- 166: `clock_angle -= 45;` (body of 3780's one-line `if`)
- 190: `lastY = level;` -- comment is `/* ? evidence: shared slot, no distinct write found */`,
  a `?` placeholder instead of a number
- 214: `ply[player_id]->angle += 0x80000;` (body of 3833's one-line `if`)
- 224: `profile->rewards[rewResult]++;` (body of 3843's one-line `if`)

### Range / malformed comments (two numbers, not a single token)
- 217: `if (...) {                                               /* 3839..3840 */`
- 238: `level = (...)                                              /* 3864..3868 */`
- 239: `diff = level - ...;                                        /* 3869..3870 */`
- 274: `ply[player_id]->in_combo = 100;                            /* 3923/3928 */`

### Placement worth a second look (trailing annotation on the first line of a multi-line statement)
- 152-154: `if (!ply[player_id]->dead &&                            /* 3767 */` continues over two
  more lines with no annotation of their own -- same shape as the W1 3692 case that broke when
  trailing; this one is trailing on the *first* line rather than the *last*, which is untested.

---

## W3.c

### No annotation at all
- 109: `game_over = 2;` (body of the `if` on line 107, annotated `/* 4010 */`)
- 147: `ply[player_id]->edge_drawn = 0;` (body of 4042's one-line `if`)
- 156: `playing = 0;` (body of 4056's one-line `if`)
- 195: `quit = 1;`
- 196: `playing = 0;` (both bodies of the `if` on 194, annotated `/* 4104 */`)
- 202: `playing = 0;` (sibling of line 201's annotated `log2file(...) /* 4112 */`)
- 251: `break;` (body of the one-line `if` on 249-250)
- 263: `quit = 1;`
- 264: `playing = 0;` (both follow line 262's `/* 4152 */` with no number of their own)
- 349: `playing = 0;` (sibling of line 348's annotated `log2file(...) /* 4255 */`)
- 353: `quit = 1;`
- 354: `playing = 0;` (both follow line 352's `/* 4265 */`)
- 398: `next_floor = demo->floor - 10;` (body of 4301's one-line `if`)
- 421: `ffstep = 32;` (body of 4330's one-line `if`)
- 445: `rest(2);` (body of 4357's one-line `while`)

### Range / malformed comments
- 136: `for (i = 0, midX = next_aight / 2; i < midX; i++) {                 /* 4029/4123 */`
- 172: `addTime = time(NULL) - pauseTime;                              /* 4066-4067 */`

### Note (not a gap, flagging for awareness)
- 212-213, 294-295, 425, 439: comments cite `draw.inl`/`gfx.inl` line numbers instead of `main.c`
  (e.g. `/* draw.inl:46 */`). This looks deliberate (Allegro inline functions genuinely attribute
  bytes to their own header under `-g`), but since it's a different convention from every other
  annotation in the tree, flagging it so the owner can confirm it is intentional rather than another
  parse-failure case.

---

## W4.c

### No annotation at all
- 103: `gameData->ccc[i] = ply[player_id]->ccc[i];` (body of the `for` on 102, `/* 4395 */`)
- 105: `gameData->jc[i] = ply[player_id]->jcTop[i];` (body of the `for` on 104, `/* 4398 */`)
- 113: `keys_pressed[k] = time_cheat_count;` (body of the `for` on 112, `/* 4402 */`)
- 122: `last_keys[k] = time_cheat_count;` (body of the `for` on 115-121, annotated only via a long
  prose comment on the `for` line itself with a `4404:` prefix -- the body has nothing)
- 171: `demo->ccc[i] = ply[player_id]->ccc[i];` (body of the `for` on 170, `/* 4510 */`)
- 173: `demo->jc[i] = ply[player_id]->jcTop[i];` (body of the `for` on 172, `/* 4513 */`)
- 193: `mkdir(replay_directory);` (body of 4541's one-line `if`; the block comment above mentions
  4543 but that number is never attached to this statement)
- 285: `syncProfileFromOptions();` -- no annotation at all; only a block header comment two lines
  above (`/* lines 4641..4643: unconditional... */`) which is itself a range, not a token on this
  statement. This is a real, isolated call statement, worth checking first.
- 295: `qualify[i] = 0;` (body of the `for` on 294, `/* 4650 */`)
- 306: `gotHigh = 0;` (sibling of line 305's annotated `quit = 0; /* 4657 */`)
- 344: `gameover_bmp_id = 0x37;` (body of 4671's one-line `if`)

### Range / malformed comments
- (none found beyond the block-header prose already listed as fine in the general note above)

---

## W5.c

### No annotation at all -- large block
- 125-140: the entire highscore-qualification recompute (`for (i = 0; i < 15; i++) qualify[i] = 0;`
  through `gotHigh += qualify[i];` at line 139) has **zero** annotations on any of its ~14
  statements. This duplicates W4's already-annotated 4650-4664 block (the comment at 143-147
  explains *why* it's recomputed here, but never attaches line numbers to the recompute itself).
- 142: `gotHigh = 0;` (body of the `if` on 141)

### No annotation at all -- scattered
- 153: `falling = 0;` (body of 4695's one-line `if`, has its own explanatory comment but no digit)
- 162: `update_particle(&stars[i]);` -- comment is `/* ? original also walks characters[]... */`, a
  `?` placeholder, not a number
- 164: `hurry_y -= 2;` (body of 4702's one-line `if`)
- 177: `stop_sample(custom.falling);` (body of 4712's one-line `if`)
- 192: `continue;` (body of the `if` on 191, itself unannotated -- see below)
- 195: `if (ply[player_id]->shake == 0 && falling > 0)` -- comment is `/* ? approximated loop-exit
  predicate */`, a `?` placeholder
- 319: `falling = 0;` (sibling of line 318's annotated `ply[player_id]->shake = 24; /* 4850 */`)
- 333: `alpha_pos = 0;` (body of 4886's one-line `if`)
- 338: `alpha_pos = len;` (body of the `if` on 337, itself unannotated)
- 344, 346, 350, 352: `alpha_pos--;` / `alpha_pos++;` (the whole 4899-4902/else-chain from
  343 through 353 has only one number, on line 343 `/* 4899 */`, covering a 6-line if/else-if/else)
- 275: `current_rank_id = new_rank_id; /* ? */` -- `?` placeholder instead of a number
- 337: `if (alpha_pos < 0)` (body continuation, no annotation; paired with 338 above)
- 349: `} else if (alpha_pos != 0) {         /* ? best-effort for the non-blank confirm case */` --
  `?` placeholder
- 356-357: `if (alpha_pos <= 2)` / `buf[alpha_pos * 2] = letters[alpha_pos];` -- only 357 has
  `/* 4915 */`; 356's condition itself is unannotated
- 362: `skip_keys--;` (body of 4923's one-line `if`, itself untagged as a gap since 361 has
  `/* 4923 */` -- but see placement note, the annotation is on the `if` for `skip_keys != 20`
  starting a *different* physical construct than the trailing `if (isGuest...)` at 363)
- 419-420: `strcpy(postName, profile->handle); initials = postName;` (else-branch of 4943's `if`,
  no annotation on either statement)

### Range / malformed comments
- 189: `if (key[KEY_LSHIFT] && key[KEY_TAB]) {           /* 4929..4931: operand order swapped */`
  (this is actually at file line 399, see below -- listing both occurrences of this exact pattern)
- 381: `for (i = 0; i < len; i++) {                              /* 4871..4872: scan letters[] */`
- 399: `if (key[KEY_LSHIFT] && key[KEY_TAB]) {           /* 4929..4931: operand order swapped`
- 453: `while (!key[KEY_ESC] && !key[KEY_ENTER] && !key[KEY_SPACE]) {  /* 4986..4987 */`

### Placement worth a second look (trailing on first line of multi-line statement, untested form)
- 166-168: `/* 4704 */ draw_results(swap_screen, ...` -- annotation is a **leading inline** comment
  immediately before the call on the same physical line, not on its own line above; this reads more
  like the "trailing on first line" case than the confirmed-working "own line above" case.
- 170-171, 181-182, 224-225, 243-244, 246-247, 249-250, 251-252, 254-256, 257-259, 272-273, 300-301,
  302-304, 322-323, 439-440, 444-450: same `/* NNNN */ call(...)` leading-inline-on-same-line pattern
  repeated throughout for every multi-line call. Given how many of these there are, and that this
  file's own header comment (204-206) explicitly documents the *problem* this solves (an unannotated
  opening line inheriting the previous statement's number) without confirming this exact placement
  against the walker, it is worth one targeted check: does `/* NNNN */ foo(a,\n b, c);` on the same
  line as the call's opening actually credit `foo`'s bytes to NNNN, or does it need to be a genuinely
  separate leading-comment line the way the working W1 3692 fix was?

---

## Not in scope here (already handed off separately)

- **midY at historical 3699 (W1b)**: confirmed by the coordinator as a real cross-region issue, not
  an annotation gap -- the original keeps it in `%edi` (fldl/fldcw/fistpl -0x924/mov -0x924,%edi) but
  its only readers are in W2's collision handling, so the write is legitimately dead in the current
  build until W2 is complete enough to read it back. Filed here under W2 for its owner's awareness,
  not as an annotation-gap action item.
