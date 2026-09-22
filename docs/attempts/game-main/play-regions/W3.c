/* Reconstruction of play() (historical main.c lines 3405..5021, 17420 bytes at 0x411a00).
 * Skeleton: function-level locals from DWARF (52); outer structure from the line table and the
 * loop back-edge 2842->560 (while (playing && !closeButtonClicked) over lines 3540..4369); the
 * function returns play_again (line 5021), set by do_replay_menu at line 5004.
 * Regions are filled from the historical line table, one coherent source region at a time;
 * every call is a historical call site (tools/function_lines.py game-main play --lines).
 * Retained evidence body for the TU_CONTEXT overlay; production only through the strict gate. */
int play(void)
{
    int playing;
    int old_map_pos;
    int level;
    int diff;
    int i;
    int quit;
    int scroll_acc;
    int scroll;
    int max_scroll;
    int speeds[9] = { 1500, 3000, 4500, 6000, 7500, 9000, 10500, 1800000, 9000000 };
    int next_speed;
    int next_aight;
    int allow_smpl;
    int game_over;
    int falling;
    int shake;
    int flash;
    int step_count;
    int next_floor;
    int play_again;
    int tot_scroll;
    int lastX;
    int lastY;
    int midX;
    int midY;
    int numComboJumps;
    int totComboFloors;
    int startTime;
    int endTime;
    int lastJumpLength;
    int oldUnlockedFloors;
    int current_rank_id;
    Tcontrol rec_ctrl;
    int time_cheat_count;
    clock_t clockTimeStart;
    clock_t clockTimeEnd;
    double clockElapsed;
    double totClockTimes;
    int qpc_start;
    int qpc_end;
    double qpc_elapsed;
    double totQPCTimes;
    int timeTimeStart;
    int timeTimeEnd;
    int timeElapsed;
    double totTimeTimes;
    int musicCounter;
    int lastMusicPos;
    float accMusics;
    int totMusics;
    LARGE_INTEGER li;
    int qpc_freq;
    /* The reset block at line 3520 also zeroes ebp-0x928, a slot no DWARF local claims:
     * every other slot that burst writes maps to a named function-level local, and the
     * twelve function-scope locals whose DWARF location was optimized away are the only
     * candidates.  Its lifetime (0 at 3520, 1 at 4003/4004, a conditional increment at
     * 4015, compared with 250 at 4016, 0 at 4022) spans the whole game loop, so it is a
     * function-level local and not a block local; the name here is provisional. */
    int aightScore;

    /* REGION W1a: lines 3405..3530 (locals init, rank, recording setup, first frame, music, timers) */

    while (playing && !closeButtonClicked) {   /* lines 3534..3536 */
        /* REGION W1b: lines 3540..3699 (per-frame counters, music sync, debug timing, speed steps) */

        /* REGION W2: lines 3700..3999 (input, player/particles, collision switch, floors, rewards, combos, level) */

        /* REGION W3: lines 4000..4369 (combo sounds, quit/pause screens, screenshots, frame draw and pacing) */
            add_jump_sequence(gameData, &jumpSequence);                             /* 4000 */
                /* aightScore lives in the function-level slot ebp-0x928 that the line-3520 reset
                 * block zeroes, so it is declared with play's other locals, not here: as a block
                 * local re-initialised every iteration GCC could prove it never passed 250 and
                 * deleted the whole 4016..4019 body.  Both arms fall through unconditionally into
                 * the y<900 combo body below (traced from the tail-duplicated machine code at
                 * offsets 2266..2304 / 5797..5848: the "lastJumpLength = 0; aightScore = 1;" pair
                 * is machine-duplicated into BOTH arms -- the no_combo_top_floor update is the
                 * only part actually gated). */

                if (numComboJumps) {                                               /* 4003 */
                    lastJumpLength = 0;                                             /* 4003 */
                    aightScore = 1;                                                 /* 4003 */
                } else {
                    if (ply[player_id]->no_combo_top_floor < ply[player_id]->level) /* 4003 */
                        ply[player_id]->no_combo_top_floor = ply[player_id]->level; /* 4004 */
                    lastJumpLength = 0;                                             /* 4004 */
                    aightScore = 1;                                                 /* 4004 */
                }
            /* The `if (y < 540.0 && !dead)` opened in W2 at line 3976 closes here: both of its
             * `jne`s jump to offset 2940, `mov $0xffffffff,%esi; jmp 412300`, and 0x412300 is
             * offset 2304, the first instruction of line 4010.  So `add_jump_sequence` and the
             * 4003/4004 block are inside that `if`, the else arm is this single store, and 4010 is
             * where the two paths merge.  With this edge in place `aightScore` is no longer 1 on
             * every path into 4015, which is what let GCC prove 4016's `> 250` test false and
             * delete 4016..4019 outright. */
        } else {
            playing = -1;                                                       /* 4004 */
        }
        if (ply[player_id]->y < 900.0 && !game_over) {                      /* 4010 */
            play_sound(speaker[1], 0, 0);                                   /* 4012 */
            game_over = 2;                                                  /* 4012 */
        }
        if (aightScore)                                                     /* 4015 */
            aightScore++;                                                   /* 4015 */
        if (aightScore > 250 && aightScore <= ply[player_id]->level * 5) {   /* 4016 */
            play_sound(sounds[6], 1, 0);                                    /* 4017 */
            if (custom.falling)                                            /* 4018 */
                stop_sample(custom.falling);                               /* 4019 */
            /* 4022 is INSIDE this block, not after it: line 4016's own `jle` at offset
             * 2373 jumps to offset 2453, past both of these stores, while 4018's `je` at
             * 2411 jumps to 2421, the first of them.  With the reset conditional the
             * counter accumulates across frames, which is what makes the `> 250` test
             * reachable at all; with it unconditional the counter is 0 or 2 on every path
             * and GCC deletes 4016..4022 outright. */
            ply[player_id]->shake = 0x18;                                   /* 4022 */
            aightScore = 0;                                                 /* 4022 */
        }
        if (next_aight > ply[player_id]->level) {                           /* 4027 */
            play_sound(sounds[2], 0, 0);                                    /* 4028 */
        }
        if (!options.flash) {                                                  /* 4029 */
            /* midX = next_aight / 2 is evaluated as the loop bound: the shr/add/sar division
             * (rounding toward zero) is credited to main.c:4029 itself (the compiler folds it
             * into the for-init/condition), while the spill store to midX's own stack slot
             * (DWARF -0x940(%ebp)) lands on main.c:4031, the loop body's first real statement
             * (source-view 4000..4055: fragments 3987..4024 tagged 4029, 4024..4036 tagged
             * 4031) -- so the assignment and the loop share one combined-init statement. */
            for (i = 0, midX = next_aight / 2; i < midX; i++) {                 /* 4029/4123 */
                int p;                                                          /* 4031 block-local */
                p = create_particle(stars, (new_rand() % 600) + 20, 480);       /* 4030 */
                stars[p].sy = -(((new_rand() % 200) << 16) / 5);                /* 4031 */
            }
        }
        if (next_aight > 999)                                                  /* 4033 */
            next_aight += 500;                                                 /* 4034 */
        else
            next_aight += 50;                                                  /* 4037 */
        if (ply[player_id]->edge == 0)                                        /* 4042 */
            ply[player_id]->edge_drawn = 0;                                   /* 4042 */
        if (ply[player_id]->edge_drawn != 0) {                                 /* 4043 */
            if (ply[player_id]->edge_drawn == 11 && ply[player_id]->status == 0) /* 4044 */
                play_sound(custom.edge, 1, 1);                                 /* 4044 tail */
            if (ply[player_id]->edge_drawn == 50)                              /* 4045 */
                ply[player_id]->edge_drawn = 0;                                /* 4046 */
        }
        if (!debug) {                                                          /* 4049 */
            if (recording && ply[player_id]->dead > 100)                       /* 4056 */
                playing = 0;                                                  /* 4056 */
        } else if (ply[player_id]->dead <= 99) {                               /* 4050 */
            /* esi is confirmed as `playing` here (its DWARF range covers offsets 2860..2903,
             * exactly this store). Re-measured after `playing` gained its first real assignments
             * this round (the y<540/dead edge and the KEY_SPACE/KEY_RIGHT restructure): 4050 now
             * measures 29 of 22 historical bytes and 4056 32 of 44 -- together 61 of 66, so the
             * two `playing = 0;` epilogues (this one and 4056's) are no longer degenerate; the
             * remaining spread is consistent with the two still sharing code the historical
             * binary kept separate, not a missing statement. */
            playing = 0;                                                     /* 4050 */
        }
        if (!itrcheck && key[KEY_F1]) {                                        /* 4062 */
            int pauseTime, addTime; /* DWARF block 132550 [4560..4780]: pauseTime, addTime */
            pauseTime = time(NULL);                                            /* 4063 */
            take_screenshot(swap_screen);                                      /* 4064 */
            if (key[KEY_F1]) {                                                 /* 4065 (see report: odd self-target) */
                addTime = time(NULL) - pauseTime;                              /* 4066-4067 */
                if (addTime > 0)                                               /* 4067 */
                    startTime += addTime;                                      /* 4068 */
            }
            if (gameMusicVoiceID >= 0)                                        /* 4075 */
                musicCounter = (int)(voice_get_position(gameMusicVoiceID) * 50.0 / 44000.0); /* 4077 */
            clockTimeStart = clock();                                          /* 4083 */
            QueryPerformanceCounter(&li);                                      /* 4085 */
            qpc_start = li.LowPart;                                            /* 4086 */
            timeTimeStart = time(NULL);                                        /* 4090 */
            lastMusicPos = 0;                                                  /* 4077: folded into the
                                                                                   musicCounter statement's own
                                                                                   fragment (offsets 4697..4709,
                                                                                   right after the fistpl), not a
                                                                                   separate line-table row */
            accMusics = 0.0;                                                   /* 4077 */
        }
        if (ply[player_id]->shake) {                                          /* 4094 */
            ply[player_id]->shake--;                                          /* 4095 */
            shake = new_rand() % 8;                                           /* 4097 */
        }
        update_frame();                                                       /* 4100 */
        if (!quit && closeButtonClicked) {                                    /* 4104 */
            quit = 1;                                                        /* 4104 */
            playing = 0;                                                     /* 4104 */
        }
        if (recording) {                                                      /* 4109 */
            if (key[KEY_ESC]) {                                               /* 4110 */
                if (ply[player_id]->dead) {                                   /* 4111 */
                    log2file("  player quit after dying");                    /* 4112 */
                    playing = 0;                                              /* 4112 */
                } else {
                    /* REGION W3a: ESC pause screen, lines 4117..4182 */
                    int pauseTime, fc, ca, addTime; /* block-scoped DWARF locals (block 132596), not in the 52-local skeleton */

                    pauseTime = time(NULL);                                   /* 4117 */
                    fc = fall_count;                                          /* 4118 */
                    ca = clock_angle;                                         /* 4119 */
                    log2file("  game paused with esc");                      /* 4120 */
                    for (i = 0; i < 640; i += 2) {                            /* 4122 */
                        vline(swap_screen, i, 0, 480, 0);                     /* draw.inl:46 */
                        hline(swap_screen, 0, i, 640, 0);                     /* draw.inl:54 */
                    }
                    textout_centre_ex(swap_screen, data[50].dat,               /* 4126: GCC attributes a call's
                                                                                  bytes to its opening line, so the
                                                                                  annotation moves here (was on the
                                                                                  closing line, which left the
                                                                                  line_budget tool crediting each
                                                                                  call's bytes to the call above it
                                                                                  and showing 4128 as 0 bytes even
                                                                                  though the call is present). */
                                       "DO YOU REALLY WANT TO EXIT?", 320, 160, -1, -1);
                    textout_centre_ex(swap_screen, data[52].dat,               /* 4127 */
                                       "Press any key to resume", 320, 210, -1, -1);
                    textout_centre_ex(swap_screen, data[52].dat,               /* 4128 */
                                       "Press ESC to exit", 320, 240, -1, -1);
                    blit_to_screen(swap_screen);                              /* 4129 */
                    play_sound(custom.wazup, 0, 1);                           /* 4130 */
                    /* Two-loop wait, re-derived from the assembly (source-view 4117..4182):
                     * outer loop's entry jmp lands on its is_any/is_pause/ESC compound test
                     * (offsets 1717.. no -- offsets 5357/5316 etc, see function_lines source-view),
                     * a plain bottom-tested `while (cond) body`; the inner "key still held" loop's
                     * entry jmp lands on keypressed() alone (offset 5490), meaning keypressed() is
                     * the sole loop condition and the is_any/is_pause/closeButtonClicked/key[ESC]
                     * checks are an if-break inside its body -- GCC then thread the break's three
                     * different truth cases into different entry points of the loop that follows
                     * (closeButtonClicked jumps straight past that loop's own redundant
                     * closeButtonClicked test; key[ESC] jumps into its is_pause call for the same
                     * reason), which is why the reconstruction only needs three plain loops. */
                    poll_control(&ctrl, 0);                                    /* 4132 */
                    while (is_any(&ctrl) || is_pause(&ctrl)                    /* 4133 */
                           || (!closeButtonClicked && key[KEY_ESC])) {         /* 4133 */
                        poll_control(&ctrl, 0);                                /* 4134 */
                        rest(2);                                               /* 4135 */
                    }
                    clear_keybuf();                                            /* 4137 */
                    while (!keypressed()) {                                    /* 4138 */
                        if (is_any(&ctrl) || is_pause(&ctrl) ||
                            closeButtonClicked || key[KEY_ESC])                /* 4138 */
                            break;
                        poll_control(&ctrl, 0);                                /* 4139 */
                        rest(2);                                               /* 4140 */
                    }
                    while (!closeButtonClicked && is_pause(&ctrl)) {           /* 4142 */
                        poll_control(&ctrl, 0);                                /* 4143 */
                        rest(2);                                               /* 4144 */
                    }
                    if (key[KEY_ESC]) {                                       /* 4146 */
                        log2file("  game quit from esc pause");               /* 4150 */
                        profile->games_quit++;                                /* 4151 */
                        endTime = time(NULL);                                 /* 4152 */
                        quit = 1;
                        playing = 0;
                    }
                    clear_keybuf();                                           /* 4154 */
                    fall_count = fc;                                          /* 4156 */
                    clock_angle = ca;                                         /* 4157 */
                    log2file("  game unpaused");                              /* 4158 */
                    addTime = time(NULL) - pauseTime;                         /* 4159 */
                    if (addTime > 0)                                          /* 4160 */
                        startTime += addTime;                                 /* 4161 */
                    if (gameMusicVoiceID >= 0)                                /* 4168 */
                        musicCounter = (int)(voice_get_position(gameMusicVoiceID) * 50.0 / 44000.0); /* 4170 */
                    clockTimeStart = clock();                                 /* 4175 */
                    QueryPerformanceCounter(&li);                             /* 4177 */
                    qpc_start = li.LowPart;                                   /* 4178 */
                    timeTimeStart = time(NULL);                               /* 4182 */
                    lastMusicPos = 0;                                         /* 4170: folded into the
                                                                                  musicCounter statement's own
                                                                                  fragment, same shape as 4077 */
                    accMusics = 0.0;                                          /* 4170 */
                }
            }
            if (is_pause(&ctrl) && ply[player_id]->dead == 0) {               /* 4186 */
                /* REGION W3b: pause-key screen, lines 4187..4245 (near-identical to W3a) */
                int pauseTime, fc, ca, addTime; /* block-scoped DWARF locals (block 132838), not in the 52-local skeleton */

                pauseTime = time(NULL);                                       /* 4187 */
                fc = fall_count;                                              /* 4188 */
                ca = clock_angle;                                             /* 4189 */
                log2file("  game paused with pause key");                     /* 4190 */
                for (i = 0; i < 640; i += 2) {                                /* 4192 */
                    vline(swap_screen, i, 0, 480, 0);                         /* draw.inl:46 */
                    hline(swap_screen, 0, i, 640, 0);                         /* draw.inl:54 */
                }
                textout_centre_ex(swap_screen, data[50].dat,                  /* 4196 (annotation kept on the
                                                                                  opening line; see the note above
                                                                                  the ESC screen's identical calls) */
                                   "Game Paused", 320, 160, -1, -1);
                textout_centre_ex(swap_screen, data[52].dat,                  /* 4197 */
                                   "Press any key to resume", 320, 210, -1, -1);
                blit_to_screen(swap_screen);                                  /* 4198 */
                play_sound(custom.wazup, 0, 1);                               /* 4199 */
                /* Same three-loop shape as the ESC screen (W3a above), but this screen's
                 * outer wait has no closeButtonClicked term (source-view 4186..4245 never
                 * loads it before is_any/is_pause/ESC), and its final loop tests
                 * is_pause() || key[KEY_ESC] directly (continues on either, offset
                 * 7018/7027 both jump back to the poll_control/rest body) rather than the
                 * negated-AND the ESC screen's closing loop uses. */
                poll_control(&ctrl, 0);                                       /* 4200 */
                while (is_any(&ctrl) || is_pause(&ctrl)) {                    /* 4201 */
                    poll_control(&ctrl, 0);                                   /* 4202 */
                    rest(2);                                                  /* 4203 */
                }
                clear_keybuf();                                               /* 4206 */
                while (!keypressed()) {                                       /* 4207 */
                    if (is_any(&ctrl) || is_pause(&ctrl) || key[KEY_ESC])      /* 4207 */
                        break;
                    poll_control(&ctrl, 0);                                   /* 4208 */
                    rest(2);                                                  /* 4209 */
                }
                poll_control(&ctrl, 0);                                       /* 4212 */
                while (is_pause(&ctrl) || key[KEY_ESC]) {                     /* 4213 */
                    poll_control(&ctrl, 0);                                   /* 4214 */
                    rest(2);                                                  /* 4215 */
                }
                fall_count = fc;                                              /* 4219 */
                clock_angle = ca;                                             /* 4220 */
                log2file("  game unpaused");                                  /* 4221 */
                addTime = time(NULL) - pauseTime;                             /* 4222 */
                if (addTime > 0)                                              /* 4223 */
                    startTime += addTime;                                     /* 4224 */
                if (gameMusicVoiceID >= 0)                                    /* 4231 */
                    musicCounter = (int)(voice_get_position(gameMusicVoiceID) * 50.0 / 44000.0); /* 4233 */
                clockTimeStart = clock();                                     /* 4238 */
                QueryPerformanceCounter(&li);                                 /* 4240 */
                qpc_start = li.LowPart;                                       /* 4241 */
                timeTimeStart = time(NULL);                                   /* 4245 */
                lastMusicPos = 0;                                             /* 4233: folded into the
                                                                                  musicCounter statement's own
                                                                                  fragment, same shape as 4077 */
                accMusics = 0.0;                                              /* 4233 */
            }
            if (!itrcheck) {                                                 /* 4249 */
                poll_control(&rec_ctrl, 0);                                   /* 4251 */
                if (ply[player_id]->dead) {                                   /* 4253 */
                    log2file("  replay ended after death");                   /* 4255 */
                    playing = 0;
                }
                if (key[KEY_ESC]) {                                           /* 4264 */
                    log2file("  quit from replay");                           /* 4265 */
                    quit = 1;
                    playing = 0;
                }
                if (key[KEY_SPACE]) {                                        /* 4271 */
                    if (ply[player_id]->dead == 0) {
                        log2file("  replay paused");                          /* 4272 */
                        while (key[KEY_SPACE])                                /* 4273: debounce-wait loop */
                            poll_control(&rec_ctrl, 1);
                        while (!key[KEY_SPACE] && !key[KEY_RIGHT] &&          /* 4274: pause-wait loop */
                               !key[KEY_ESC] && !key[KEY_UP]) {               /* 4274: pause-wait loop */
                            poll_control(&rec_ctrl, 1);                       /* 4275 */
                            if (key[KEY_F1])                                  /* 4276 */
                                take_screenshot(swap_screen);                 /* 4277 */
                        }
                        while (key[KEY_SPACE])                                /* 4281: debounce-wait loop */
                            poll_control(&rec_ctrl, 1);
                        fast_forward = 0;                                     /* 4282 */
                        fast_fast_forward = 0;                                /* 4283 */
                        log2file("  replay unpaused");                       /* 4284 */
                    }
                }
                /* NOT an else: main.c:4271's own je (SPACE not pressed) lands at offset 5965,
                 * exactly the reload that starts main.c:4284's tail; the dead!=0 fallthrough at
                 * offset 3262 lands exactly at 4287's own first fragment; and 4284's own tail
                 * falls straight into 4287's SECOND fragment (offsets 5971..5984) after finishing
                 * the pause/unpause sequence. All three paths -- space not pressed, space pressed
                 * while dead, and space pressed-and-unpaused -- converge on the same KEY_RIGHT
                 * test, so 4287..4310 run unconditionally after the block above, not only when it
                 * was skipped. */
                if (key[KEY_RIGHT]) {                                    /* 4287 */
                    fast_forward++;                                       /* 4288 */
                    fast_fast_forward = 0;                                /* 4289 */
                } else {
                    /* main.c:4287's own je (KEY_RIGHT false) and the post-unpause path's second
                     * KEY_RIGHT test both land at offset 5984, `movl $0,fast_forward`, tagged
                     * main.c:4292 -- a real reset shared by both paths, not just the debounce
                     * tail, missing from this branch until now. */
                    fast_forward = 0;                                     /* 4292 */
                    if (key[KEY_UP]) {                                    /* 4295 */
                        if (ply[player_id]->dead == 0 &&
                            ply[player_id]->level < demo->floor - 10) {       /* 4296 */
                            fast_fast_forward++;                              /* 4297 */
                            fast_forward = 0;                                 /* 4298 */
                            next_floor = ((ply[player_id]->level + 100) / 100) * 100; /* 4299 */
                            if (next_floor > demo->floor - 10)                /* 4301 */
                                next_floor = demo->floor - 10;
                        }
                    }
                }
                /* source-view 4270..4320: the level>=next_floor test (fragments 3390..3412)
                 * falls straight into the reset; the level<next_floor case instead jumps to
                 * a second, out-of-line test of ply[player_id]->dead (fragments 7984..7999)
                 * that also reaches the reset when dead != 0 -- one condition, two tested
                 * terms ORed, not just the level compare. */
                if (ply[player_id]->level >= next_floor ||
                    ply[player_id]->dead) {                              /* 4309 */
                    fast_fast_forward = 0;                                /* 4310 */
                    next_floor = -1;
                }
            }
        }
        if (!itrcheck) {                                                     /* 4319 */
            static int someCounter;
            int ffstep; /* DWARF block 132354 [2740..2804 6150..6448]: someCounter, ffstep, drew, skipDrawing */

            someCounter++;                                                    /* 4324 */
            ffstep = fast_forward ? 4 : 1;                                   /* 4327 */
            if (fast_fast_forward)                                            /* 4330 */
                ffstep = 32;
            if (!quit && someCounter % ffstep == 0) {                        /* 4337 */
                draw_frame(swap_screen);                                      /* 4338 */
                if (ply[player_id]->shake) {                                  /* 4346 */
                    acquire_screen();                                          /* gfx.inl:221/203 */
                    blit(swap_screen, swap_screen, 0, shake, 0, 0,             /* 4348: args from
                                                                                    fragments 6207..6271 (source-view
                                                                                    4340 4352) -- src=dst=swap_screen,
                                                                                    src_x=0, src_y=shake (ebp-0x96c),
                                                                                    dst_x=dst_y=0, w/h read back from
                                                                                    swap_screen's own struct fields
                                                                                    (mov (%eax),%edx / mov 0x4(%eax));
                                                                                    annotation moved to the opening
                                                                                    line for the same reason as 4126
                                                                                    above (GCC attributes a call's
                                                                                    bytes to where it opens). */
                         swap_screen->w, swap_screen->h);
                    blit_to_screen(swap_screen);                              /* 4349 */
                    release_screen();                                         /* gfx.inl:227/212 */
                } else {
                    blit_to_screen(swap_screen);                              /* 4353 */
                }
                if (!debug) {                                                 /* 4356 */
                    while (cycle_count == 0)                                  /* 4357 */
                        rest(2);
                } else if (key[KEY_TAB] && key[KEY_LSHIFT]) {                  /* 4360 */
                    while (cycle_count <= 7)                                  /* 4361 */
                        rest(2);                                              /* 4363 */
                }
            }
        }
        rest(2);                                                             /* 4369 */
    }

    /* REGION W4: lines 4374..4683 (post-game accounting, gameData XML, replay files, profile, highscore qualification) */
    {
        /* DWARF block 133269 opens at main.c:4650 and runs to the end of the function, so the
         * highscore/results state is one scope that spans regions W4 and W5. */
        float hy;
        int gotHigh;
        int qualify[15];
        int qualifyValue[15];
        int gameover_bmp_id;

    /* REGION W5: lines 4687..5021 (results screens, name entry, highscore entry, epilogue, replay menu) */
    }

    return play_again;
}
