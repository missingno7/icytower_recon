# play() historical call-graph and control-flow census

Original: VA 0x411a00, 17420 bytes (offsets 0..17419). Current reconstruction: 623 bytes.
Full data: `docs/attempts/game-main/play-census.json`.

## Headline numbers

- Historical direct-call sites: 290 (78 unique names) + 18 indirect calls (unresolved symbol,
  best-effort vtable targets noted below) + 1 intra-function indirect `jmp` (switch table,
  excluded from call counts).
- Current (compiled) callees of `play`: 19 unique names, 0 of them absent from the historical set
  (`extra_edges` is empty).
- **Missing edges: 59** historical unique callees that current `play()` never calls.
- Regions identified: 43 (see JSON `regions`); one (2416-2602) is unlabeled `unknown` for lack of
  time to hand-disassemble it (no calls in that span to anchor a label).
- Back-edges (candidate loops): 213 raw `jmp`-to-lower-offset instructions; only a handful
  correspond to real source-level loops (see Loops below), the rest are GCC -O2 jump-threading
  artifacts of if/else chains.

## Top-level structure

- **0-559 `setup_prologue`**: struct copies (two 9-dword blocks from 0x4d6c80/0x5000c8), zero
  per-jump history arrays, `log2file("PLAY")`, `update_frame()`, and (once) a debug timer
  bootstrap (`time`/`QueryPerformanceCounter`/`QueryPerformanceFrequency`/`clock`).
- **560-604 `main_loop`**: `cycle_count = 0;` -- the literal `while(playing && !closeButtonClicked)`
  header (src/main.c:1772-1773).
- **605-1342**: iteration counters + audio-synced FPS math (605-886), a debug/cheat key-scan
  reading `key[]` scancodes 0x5069a3-ac (886-1224), fixed-point player-position prep (1224-1322),
  `handle_player_input` (1322).
- **1342-3183**: `update_player`, 512x `update_particle`, `add_floor`(+error path), reward/combo
  bookkeeping (`start_reward`, `add_combo`, `add_jump_sequence`, `play_sound`, `stop_sample`),
  `update_frame`, `is_pause`/`rest` (pause check -- **later in the frame than the current stub
  places it**, at offset 2698 vs. top-of-loop), then the `collision_type` 5-way switch (jump table
  at offset 2979) dispatching to the five `handle_player_collision_*` variants.
- **3183-4314**: `poll_control` (first appearance -- historically NOT at the top of the loop, flag:
  structural mismatch vs. current source order), `get_level`/`add_jump_sequence`/`play_sound`,
  random-particle burst (`new_rand` x3, `create_particle`).
- **4314-7406 `death_gameover_results`**: the entire death/results flow the current stub is
  missing outright -- music stop, screenshot, two near-identical text-prompt-and-wait pages
  (`textout_centre_ex`, `blit`/`blit_to_screen`, `poll_control`/`is_pause`/`is_any`/`clear_keybuf`/
  `keypressed` wait loops, `draw_frame`), then 10 consecutive `start_reward` calls (end-of-game
  bonus tally).
- **7406-9843**: game-data XML accounting (`getGameDataXML`/`printf`/`free`), `save_profile`
  (already present at the very end of current `play()`, but historically called much earlier and
  more than once), replay file management (`file_exists`/`mkdir`/`myDeleteFile`/`sprintf`/
  `save_replay` x3/`load_replay`/`calc_replay_checksum`/`destroy_replay`), `qualify_hisc_table`,
  `save_config`, `do_replay_menu`.
- **9843-12493**: a fade/restart transition (`fadeIn`, `play_sample`, `get_rank_id`); a restart
  path (10261-10594, `setup_prologue` label) that is the target of back-edges from offsets
  10162/10175/10226 (-> 258) and 10272 (-> 87) -- **`play()` loops back into its own prologue to
  start another round without returning to its caller**; `my_alert`, `stricmp`; more
  `draw_results` rendering.
- **11911-14050 `scrolling_floor_generation`**: `init_scroller`/`scroll_scroller`, a big block
  (12493-13628) of shake-effect blits, `drawing_mode`/`set_trans_blender`/`makecol`
  (alpha-blended HUD meter bar drawn via indirect vline-style vtable calls), `draw_scroller` x2,
  `restart_scroller`; then directional-input polling (`is_fire`/`is_right`/`is_left`).
- **14050-17420**: high-score name entry (`strcpy`, `enter_hisc_table`, `sort_hisc_table`),
  4 more `myDeleteFile`/`sprintf`/`save_replay` triples (per-rank replay files), a fade-out/fade-in
  text sequence (`fadeOut`, `fadeIn`, several `textout_centre_ex`), one more `save_replay`, a
  final `readkey()` "press any key" prompt, and a tail block (17216-17419, no calls) that inlines
  character-by-character name-entry editing similar in shape to the standalone `get_string()` at
  src/main.c:1812.

## Indirect calls (18, best-effort, see JSON `notes`)

- 0x28/0x2c off `swap_screen`'s vtable (offsets 4991,5033,6539,6581): inferred draw calls.
- 0x10/0x14 off `screen`'s vtable (offsets 6205,6303,11693,11807,12734,12861): inferred
  acquire/release around blits (video-bitmap lock convention).
- 0x3c off `screen`'s vtable (offsets 13331,13405,13479,15235): inferred HUD meter-bar line draws.
- 0x44/0x48 off a FONT-like vtable (offsets 12422,13787,15313,15687): inferred text rendering.
- One intra-function `jmp *0x4d60c4(,%eax,4)` at offset 2979 is the `collision_type` switch's
  jump table (excluded from call counts per the exclude-intra-function-jumps rule).

## Loops

- Outer per-frame loop: `main_loop` header at offset 560; back edge cluster targeting offset 2804
  (near the collision switch, from offsets 6321/6349/6380/6396/6425) is the compiled, block-
  reordered continuation edge. **Inference** -- GCC -O2 layout scattered the literal loop-closing
  edge; no single back edge cleanly maps to "jump to offset 560."
- Outer "restart game" loop: back edges 10162/10175/10226 -> 258 and 10272 -> 87 (into
  `setup_prologue`). High confidence.
- Inner pause/wait busy-loops: short back edges near offsets 5316-5560 and 6372-6948 (nesting
  level 1 under the outer loop). **Inference**, grouped by proximity only.
- Remaining ~195 back edges (full list in JSON `loops.back_edges`): short-range, consistent with
  if/else jump-threading, not classified individually.

## Proposed reconstruction order (earliest = most edges, least ambiguity)

1. **setup_prologue timer bootstrap** (0-559, 10261-10594): restores `time`,
   `QueryPerformanceCounter`, `QueryPerformanceFrequency`, `clock`. Mechanical (struct copies,
   zero loops, four single-purpose calls).
2. **scrolling_floor_generation basics** (1760-1880): `add_floor`, `allegro_message`. Two calls,
   one error path.
3. **scoring_combo** (1880-2416, 3700-3982): `start_reward`, `add_combo`, `play_sound`,
   `add_jump_sequence`, `get_level`, `stop_sample`. Medium ambiguity -- needs the combo/jump-
   sequence locals (`numComboJumps`/`len` at -0x950, `next_aight` at -0x94c per DWARF).
4. **gamedata_itr_accounting audio hookup** (605-886): `play_sample`, `voice_get_position`.
   Low ambiguity, single call sites.
5. **player_update particle burst** (3982-4314): `new_rand`, `create_particle`. Low-medium
   ambiguity (exact random-range semantics not verified).
6. **death trigger** (4314-4944): `voice_stop`, `take_screenshot`. Only 2 new edges but this is
   the entry point for the entire missing death/results subsystem -- landing this unblocks all
   later chunks.
7. **profile/hiscore utilities** (7406-9843, 9246-9766, 10890-11085, 14050-14314): `getGameDataXML`,
   `printf`, `free`, `save_config`, `qualify_hisc_table`, `my_alert`, `enter_hisc_table`,
   `sort_hisc_table`, `strcpy`, `stricmp`. Medium ambiguity, self-contained utility calls.
8. **replay recording/playback** (8298-9246, 9766-9843, 14355-14910, 16282-16383):
   `file_exists`, `mkdir`, `myDeleteFile`, `sprintf`, `save_replay`, `load_replay`,
   `calc_replay_checksum`, `destroy_replay`, `do_replay_menu`. Medium-high ambiguity -- the
   `sprintf` format strings (filenames) were not resolved (15-minute literal budget).
9. **death/results screen rendering** (4944-7406, 11384-12493): `textout_centre_ex`,
   `textout_ex`, `blit`, `is_any`, `keypressed`, `clear_keybuf`, `draw_results`, `fadeIn`,
   `fadeOut`, `readkey`. High ambiguity -- depends on the 12 indirect vtable calls above and on
   exact on-screen text/layout, which was not verified against string literals.
10. **scrolling_floor_generation HUD block** (11911-13628): `init_scroller`, `scroll_scroller`,
    `draw_scroller`, `restart_scroller`, `drawing_mode`, `set_trans_blender`, `makecol`,
    `solid_mode`. Highest ambiguity -- alpha-blended meter bar drawn through indirect vtable
    calls whose exact vtable slot names were inferred, not confirmed.
11. **input menu polling** (13628-14050): `is_fire`, `is_right`, `is_left`. Low-medium, can be
    folded into chunk 9 or done standalone.

## Flagged as unclear

- Region 2416-2602 (`unknown`): no calls to anchor a label; not manually disassembled.
- Pause-check placement: historically at offset 2698 (after collision handling), not at the top
  of the loop as the current stub has it -- reconstructing chunk order faithfully may require
  moving this later than intuition suggests.
- `poll_control`'s first historical call site is offset 3183, not near the loop top; the 500-byte
  gap after it (3183-3700) was not disassembled in detail.
- All 18 indirect-call target identifications are inferences from operand/vtable-offset patterns,
  not confirmed against Allegro's `GFX_VTABLE`/`FONT_VTABLE` field layout.
- 102 of 145 distinct absolute data addresses referenced by `play()` are unnamed in the JSON
  (`data_references[].note`); most are in the 0x4d5xxx-0x4d6xxx literal-constant range.
