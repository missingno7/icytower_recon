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

    /* lines 4374..4426: recording gates a small profile play-time update vs. the full
     * gameData stats snapshot + itrcheck-gated XML dump. */
    if (recording) {                                                           /* 4374 */
        diff = endTime - startTime;                                            /* 4375 */
        if (diff > 0)                                                          /* 4376 */
            profile->seconds_spent_playing += diff;                           /* 4377 */
    } else {
        gameData->score = ply[player_id]->level * 10 + ply[player_id]->score;  /* 4389 */
        gameData->floor = ply[player_id]->level;                               /* 4390 */
        gameData->combo = ply[player_id]->best_combo;                          /* 4391 */
        gameData->no_combo_top_floor = ply[player_id]->no_combo_top_floor;     /* 4392 */
        gameData->biggest_lost_combo = ply[player_id]->biggest_lost_combo;     /* 4393 */
        for (i = 0; i < 5; i++)                                                /* 4395 */
            gameData->ccc[i] = ply[player_id]->ccc[i];                        /* 4395 */
        for (i = 0; i < 5; i++)                                                /* 4398 */
            gameData->jc[i] = ply[player_id]->jcTop[i];                       /* 4398 */
        {
            int keys_pressed[7];
            int key_flag[7] = { 16, 1, 2, 4, 8, 32, 128 };                     /* 4403 */
            int last_keys[7];
            int k;

            for (k = 0; k < 7; k++)                                            /* 4402 */
                keys_pressed[k] = time_cheat_count;                            /* 4402 */
            if (demo->size > 0) {                                              /* 4406 */
                for (k = 0; k < 7; k++)                                        /* 4404: rep stos reuses eax
                                                                                    * without reloading it from
                                                                                    * 4402's time_cheat_count
                                                                                    * read (offset 7805, no mov
                                                                                    * before it) -- last_keys is
                                                                                    * seeded with time_cheat_count,
                                                                                    * not a literal 0. */
                    last_keys[k] = time_cheat_count;                           /* 4404 */
                for (i = 0; i < demo->size; i++) {                             /* 4406 */
                    int flags = demo->data[i].key_flags;                       /* 4406 */
                    for (k = 0; k < 7; k++) {                                  /* 4408 */
                        int f = key_flag[k] & flags;                           /* 4409 */
                        if (!last_keys[k] && f)                                /* 4409 */
                            keys_pressed[k]++;                                 /* 4410 */
                        last_keys[k] = f;                                      /* 4412 */
                    }
                }
            }
            gameData->jump = keys_pressed[0];                                  /* 4416 */
            gameData->left = keys_pressed[1];                                  /* 4417 */
            gameData->right = keys_pressed[2];                                 /* 4418 */
        }
        if (itrcheck) {                                                       /* 4421 */
            char *xmlStr = getGameDataXML(gameData);                          /* 4422 */
            printf("%s", xmlStr);                                             /* 4423 */
            free(xmlStr);                                                     /* 4424 */
        }
    }

    /* lines 4456..4458 */
    log2file(" play ended");                                                  /* 4456 */
    fast_forward = 0;                                                         /* 4457 */
    fast_fast_forward = 0;                                                    /* 4458 */

    /* lines 4500..4643: demo/profile stat snapshot (recording && !quit only), then
     * syncProfileFromOptions()/save_profile() unconditionally, then the quit/closeButtonClicked
     * guard around highscore qualification. Traced from three save_profile() call sites all
     * tagged historical line 4641 (offsets 8235, 9307, 10956): the !recording predecessor
     * (offset 8179) calls sync+save BEFORE ever testing quit (offset 8240's test comes after
     * the call, not before it); the recording&&quit predecessor jumps straight past the whole
     * replay-file block to its own sync+save copy (offset 10900, target of the "jne 414494"
     * at offset 8315); the recording&&!quit predecessor falls through the replay-file block
     * into a third sync+save copy (offset 9251) whose *own* trailing test reads
     * closeButtonClicked directly (offset 9312, "cmpl $0x0,closeButtonClicked") rather than
     * quit -- because on that path quit was already resolved false by the earlier test at
     * offset 8308. That is only consistent with sync+save being unconditional statements
     * textually AFTER this whole if/else, not folded into either arm or gated by !quit. */
    if (recording) {                                                          /* 4500 */
        if (!quit) {                                                          /* 4500 */
            demo->score = ply[player_id]->level * 10 + ply[player_id]->score;  /* 4503 */
            demo->floor = ply[player_id]->level;                               /* 4504 */
            demo->combo = ply[player_id]->best_combo;                         /* 4505 */
            demo->rejump = options.jump_hold;                                  /* 4506 */
            demo->no_combo_top_floor = ply[player_id]->no_combo_top_floor;     /* 4507 */
            demo->biggest_lost_combo = ply[player_id]->biggest_lost_combo;     /* 4508 */
            for (i = 0; i < 5; i++)                                            /* 4510 */
                demo->ccc[i] = ply[player_id]->ccc[i];                        /* 4510 */
            for (i = 0; i < 5; i++)                                            /* 4513 */
                demo->jc[i] = ply[player_id]->jcTop[i];                       /* 4513 */

            if (!is_playing_custom_game) {                                    /* 4519 */
                profile->games_played++;                                      /* 4520 */
                profile->total_floors += demo->floor;                         /* 4522 */
                profile->total_score += demo->score;                          /* 4523 */
                profile->total_combos += numComboJumps;                       /* 4524 */
                profile->total_combo_floors += totComboFloors;                /* 4525 */
                for (i = 0; i < 5; i++) {                                      /* 4526 */
                    if (demo->ccc[i] > 0) {                                    /* 4527 */
                        profile->cccNum[i]++;                                  /* 4528 */
                        profile->cccTotal[i] += demo->ccc[i];                  /* 4529 */
                    }
                }
            } else {
                profile->custom_games_played++;                               /* 4534 */
            }

            /* lines 4541..4624: replay directory + per-category replay files */
            if (!file_exists(replay_directory, -1, NULL))                     /* 4541 */
                mkdir(replay_directory);                                      /* 4543 */

            if (!is_playing_custom_game) {                                    /* 4550 */
                int rank;

                if (demo->floor > profile->best_floor) {                      /* 4551 */
                    profile->best_floor = demo->floor;                        /* 4552 */
                    myDeleteFile(replay_directory, profile->best_replay_names[2]);  /* 4553 */
                    sprintf(profile->best_replay_names[2], "%s_best_floor_%d.itr",  /* 4554 */
                            profile->handle, demo->floor);
                    save_replay(replay_directory, profile->best_replay_names[2], demo,  /* 4555 */
                                rec_pos + 2, 1);
                    new_personal_best[2] = 1;                                  /* 4556 */
                }
                if (demo->combo > profile->best_combo) {                      /* 4559 */
                    profile->best_combo = demo->combo;                        /* 4560 */
                    myDeleteFile(replay_directory, profile->best_replay_names[1]);  /* 4561 */
                    sprintf(profile->best_replay_names[1], "%s_best_combo_%d.itr",  /* 4562 */
                            profile->handle, demo->combo);
                    save_replay(replay_directory, profile->best_replay_names[1], demo,  /* 4563 */
                                rec_pos + 2, 1);
                    new_personal_best[1] = 1;                                  /* 4564 */
                }
                if (demo->score > profile->best_score) {                      /* 4567 */
                    profile->best_score = demo->score;                        /* 4568 */
                    myDeleteFile(replay_directory, profile->best_replay_names[0]);  /* 4569 */
                    sprintf(profile->best_replay_names[0], "%s_best_score_%d.itr",  /* 4570 */
                            profile->handle, demo->score);
                    save_replay(replay_directory, profile->best_replay_names[0], demo,  /* 4571 */
                                rec_pos + 2, 1);
                    new_personal_best[0] = 1;                                  /* 4572 */
                }
                if (ply[player_id]->no_combo_top_floor > profile->no_combo_top_floor) {  /* 4575 */
                    profile->no_combo_top_floor = ply[player_id]->no_combo_top_floor;  /* 4576 */
                    myDeleteFile(replay_directory, profile->best_replay_names[4]);  /* 4577 */
                    sprintf(profile->best_replay_names[4], "%s_best_no_combo_%d.itr",  /* 4578 */
                            profile->handle, ply[player_id]->no_combo_top_floor);
                    save_replay(replay_directory, profile->best_replay_names[4], demo,  /* 4579 */
                                rec_pos + 2, 1);
                    new_personal_best[4] = 1;                                  /* 4580 */
                }
                if (ply[player_id]->biggest_lost_combo > profile->biggest_lost_combo) {  /* 4583 */
                    profile->biggest_lost_combo = ply[player_id]->biggest_lost_combo;  /* 4584 */
                    myDeleteFile(replay_directory, profile->best_replay_names[3]);  /* 4585 */
                    sprintf(profile->best_replay_names[3], "%s_best_lost_combo_%d.itr",  /* 4586 */
                            profile->handle, ply[player_id]->biggest_lost_combo);
                    save_replay(replay_directory, profile->best_replay_names[3], demo,  /* 4587 */
                                rec_pos + 2, 1);
                    new_personal_best[3] = 1;                                  /* 4588 */
                }
                for (rank = 1; rank < 6; rank++) {                             /* 4591 */
                    if (ply[player_id]->ccc[rank - 1] > profile->ccc[rank - 1]) {  /* 4592 */
                        profile->ccc[rank - 1] = ply[player_id]->ccc[rank - 1];  /* 4593 */
                        myDeleteFile(replay_directory, profile->best_replay_names[4 + rank]);  /* 4594 */
                        sprintf(profile->best_replay_names[4 + rank], "%s_best_cc%d_%d.itr",  /* 4595 */
                                profile->handle, rank, ply[player_id]->ccc[rank - 1]);
                        save_replay(replay_directory, profile->best_replay_names[4 + rank],  /* 4596 */
                                    demo, rec_pos + 2, 1);
                        new_personal_best[4 + rank] = 1;                       /* 4597 */
                    }
                }
                for (rank = 1; rank < 6; rank++) {                             /* 4601 */
                    if (ply[player_id]->jcTop[rank - 1] > profile->jc[rank - 1]) {  /* 4602 */
                        profile->jc[rank - 1] = ply[player_id]->jcTop[rank - 1];  /* 4603 */
                        myDeleteFile(replay_directory, profile->best_replay_names[9 + rank]);  /* 4604 */
                        sprintf(profile->best_replay_names[9 + rank], "%s_best_jj%d_%d.itr",  /* 4605 */
                                profile->handle, rank, ply[player_id]->jcTop[rank - 1]);
                        save_replay(replay_directory, profile->best_replay_names[9 + rank],  /* 4606 */
                                    demo, rec_pos + 2, 1);
                        new_personal_best[9 + rank] = 1;                       /* 4607 */
                    }
                }
            }

            if (save_replay(replay_directory, "last_game.itr", demo, rec_pos + 2, 1) < 0) {  /* 4613 */
                my_alert("Failed to save replay.", "(last_game.itr)", 0, 1);  /* 4614 */
                uberChecksum = 0;                                             /* 4615 */
            } else {
                char fbuf[2048];
                Treplay *rr;

                sprintf(fbuf, "%slast_game.itr", replay_directory);          /* 4620 */
                rr = load_replay(fbuf);                                      /* 4621 */
                if (rr) {                                                    /* 4622 */
                    uberChecksum = calc_replay_checksum(demo);               /* 4623 */
                    destroy_replay(rr);                                     /* 4624 */
                }
            }
        }
    }

    /* lines 4641..4643: unconditional, reached from all three predecessors above */
    syncProfileFromOptions();                                                /* 4641 */
    save_profile(profile);                                                   /* 4641 */

    /* lines 4643..4683: highscore qualification, guarded by quit && closeButtonClicked */
    if (!quit) {                                                             /* 4643 */
        if (!closeButtonClicked) {                                           /* 4643 */
            int rank;   /* qualify, qualifyValue, gotHigh and gameover_bmp_id live in the enclosing
                         * DWARF block 133269, which opens here and runs into REGION W5 */

            for (i = 0; i < 15; i++)                                         /* 4650 */
                qualify[i] = 0;                                             /* 4650 */
            qualifyValue[0] = ply[player_id]->level * 10 + ply[player_id]->score;  /* 4652 */
            qualifyValue[2] = ply[player_id]->level;                         /* 4653 */
            qualifyValue[1] = ply[player_id]->best_combo;                    /* 4654 */
            qualifyValue[3] = ply[player_id]->biggest_lost_combo;            /* 4655 */
            qualifyValue[4] = ply[player_id]->no_combo_top_floor;            /* 4656 */
            for (i = 0; i < 5; i++) {                                        /* 4657 */
                qualifyValue[5 + i] = ply[player_id]->ccc[i];                /* 4658 */
                qualifyValue[10 + i] = ply[player_id]->jcTop[i];             /* 4659 */
            }
            quit = 0;                                                       /* 4657 */
            gotHigh = 0;                                                    /* 4657 */
            for (rank = 0; rank < 15; rank++) {                              /* 4662 */
                qualify[rank] = qualify_hisc_table(hisc_tables[rank], qualifyValue[rank]);  /* 4663 */
                gotHigh += qualify[rank];                                    /* 4664 */
            }
            quit = gotHigh;                                                 /* 4662: local_slot_trace shows
                                                                                * THREE writes to quit's slot
                                                                                * in this stretch (9446/4657
                                                                                * const 0, 9503/4662 a VALUE,
                                                                                * 9522/4668 const 0 again) and
                                                                                * seven reads after them. At
                                                                                * offset 9503 ("mov %esi,
                                                                                * -0x93c(%ebp)") esi is the
                                                                                * gotHigh accumulator, still
                                                                                * live from "add %eax,%esi"
                                                                                * at offset 9495 (line 4664) --
                                                                                * quit is reused from here on
                                                                                * to carry gotHigh's value
                                                                                * through the rest of the
                                                                                * function; the 4670/4673 tests
                                                                                * below read quit, not gotHigh,
                                                                                * from this point on. */

            if (recording) {                                                /* 4668 */
                gameover_bmp_id = (quit > 0) ? 0x3e : 0x37;                  /* 4670: disasm reads -0x93c
                                                                                * (quit's slot) here, not
                                                                                * gotHigh's esi. */
            } else {
                quit = 0;                                                   /* 4668: second const-0 write to
                                                                                * quit's slot (offset 9522),
                                                                                * distinct from gotHigh (whose
                                                                                * own DW_OP_reg6/esi location
                                                                                * list keeps it separately live
                                                                                * over this same span). */
                gotHigh = 0;                                                /* 4668 */
                gameover_bmp_id = 0x37;                                     /* 4668 */
            }
            if (is_playing_custom_game)                                     /* 4671 */
                gameover_bmp_id = 0x37;                                     /* 4671 */

            if (quit) {                                                     /* 4673: disasm reads -0x93c
                                                                                * (quit) again here, not
                                                                                * gotHigh. */
                if (!is_playing_custom_game) {                              /* 4673 */
                    log2file(" player qualified for highscore");            /* 4674 */
                    play_sound(sounds[7], 0, 0);                            /* 4675 */
                }
            } else {
                log2file(" player did not qualify for highscore");          /* 4678 */
                play_sound(speaker[1], 0, 0);                               /* 4679 */
            }

            if (debug) {                                                    /* 4683 */
                /* continues in REGION W5 */
            }
        }
    }

    /* REGION W5: lines 4687..5021 (results screens, name entry, highscore entry, epilogue, replay menu) */
    }

    return play_again;
}
