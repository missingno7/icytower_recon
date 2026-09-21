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
    int speeds[9] = { 1500, 3000, 4500, 6000, 7500, 9000, 10500, 12000, 13500 };
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
    if (recording) {
        diff = endTime - startTime;
        if (diff > 0)
            profile->seconds_spent_playing += diff;
    } else {
        gameData->score = ply[player_id]->level * 10 + ply[player_id]->score;
        gameData->floor = ply[player_id]->level;
        gameData->combo = ply[player_id]->best_combo;
        gameData->no_combo_top_floor = ply[player_id]->no_combo_top_floor;
        gameData->biggest_lost_combo = ply[player_id]->biggest_lost_combo;
        for (i = 0; i < 5; i++)
            gameData->ccc[i] = ply[player_id]->ccc[i];
        for (i = 0; i < 5; i++)
            gameData->jc[i] = ply[player_id]->jcTop[i];
        {
            int keys_pressed[7];
            int key_flag[7] = { 16, 1, 2, 4, 8, 32, 128 };
            int last_keys[7];
            int k;

            for (k = 0; k < 7; k++)
                keys_pressed[k] = time_cheat_count;
            if (demo->size > 0) {
                for (k = 0; k < 7; k++)
                    last_keys[k] = 0;
                for (i = 0; i < demo->size; i++) {
                    int flags = demo->data[i].key_flags;
                    for (k = 0; k < 7; k++) {
                        int f = key_flag[k] & flags;
                        if (!last_keys[k] && f)
                            keys_pressed[k]++;
                        last_keys[k] = f;
                    }
                }
            }
            gameData->jump = keys_pressed[0];
            gameData->left = keys_pressed[1];
            gameData->right = keys_pressed[2];
        }
        if (itrcheck) {
            char *xmlStr = getGameDataXML(gameData);
            printf("%s", xmlStr);
            free(xmlStr);
        }
    }

    /* lines 4456..4458 */
    log2file(" play ended");
    fast_forward = 0;
    fast_fast_forward = 0;

    /* lines 4500..4534: demo/profile stat snapshot, only when recording && !quit */
    if (recording) {
        if (!quit) {
            demo->score = ply[player_id]->level * 10 + ply[player_id]->score;
            demo->floor = ply[player_id]->level;
            demo->combo = ply[player_id]->best_combo;
            demo->rejump = options.jump_hold;
            demo->no_combo_top_floor = ply[player_id]->no_combo_top_floor;
            demo->biggest_lost_combo = ply[player_id]->biggest_lost_combo;
            for (i = 0; i < 5; i++)
                demo->ccc[i] = ply[player_id]->ccc[i];
            for (i = 0; i < 5; i++)
                demo->jc[i] = ply[player_id]->jcTop[i];

            if (!is_playing_custom_game) {
                profile->games_played++;
                profile->total_floors += demo->floor;
                profile->total_score += demo->score;
                profile->total_combos += numComboJumps;
                profile->total_combo_floors += totComboFloors;
                for (i = 0; i < 5; i++) {
                    if (demo->ccc[i] > 0) {
                        profile->cccNum[i]++;
                        profile->cccTotal[i] += demo->ccc[i];
                    }
                }
            } else {
                profile->custom_games_played++;
            }

            /* lines 4541..4624: replay directory + per-category replay files */
            if (!file_exists(replay_directory, -1, NULL))
                mkdir(replay_directory);

            if (!is_playing_custom_game) {
                int rank;

                if (demo->floor > profile->best_floor) {
                    profile->best_floor = demo->floor;
                    myDeleteFile(replay_directory, profile->best_replay_names[2]);
                    sprintf(profile->best_replay_names[2], "%s_best_floor_%d.itr",
                            profile->handle, demo->floor);
                    save_replay(replay_directory, profile->best_replay_names[2], demo,
                                rec_pos + 2, 1);
                    new_personal_best[2] = 1;
                }
                if (demo->combo > profile->best_combo) {
                    profile->best_combo = demo->combo;
                    myDeleteFile(replay_directory, profile->best_replay_names[1]);
                    sprintf(profile->best_replay_names[1], "%s_best_combo_%d.itr",
                            profile->handle, demo->combo);
                    save_replay(replay_directory, profile->best_replay_names[1], demo,
                                rec_pos + 2, 1);
                    new_personal_best[1] = 1;
                }
                if (demo->score > profile->best_score) {
                    profile->best_score = demo->score;
                    myDeleteFile(replay_directory, profile->best_replay_names[0]);
                    sprintf(profile->best_replay_names[0], "%s_best_score_%d.itr",
                            profile->handle, demo->score);
                    save_replay(replay_directory, profile->best_replay_names[0], demo,
                                rec_pos + 2, 1);
                    new_personal_best[0] = 1;
                }
                if (ply[player_id]->no_combo_top_floor > profile->no_combo_top_floor) {
                    profile->no_combo_top_floor = ply[player_id]->no_combo_top_floor;
                    myDeleteFile(replay_directory, profile->best_replay_names[4]);
                    sprintf(profile->best_replay_names[4], "%s_best_no_combo_%d.itr",
                            profile->handle, ply[player_id]->no_combo_top_floor);
                    save_replay(replay_directory, profile->best_replay_names[4], demo,
                                rec_pos + 2, 1);
                    new_personal_best[4] = 1;
                }
                if (ply[player_id]->biggest_lost_combo > profile->biggest_lost_combo) {
                    profile->biggest_lost_combo = ply[player_id]->biggest_lost_combo;
                    myDeleteFile(replay_directory, profile->best_replay_names[3]);
                    sprintf(profile->best_replay_names[3], "%s_best_lost_combo_%d.itr",
                            profile->handle, ply[player_id]->biggest_lost_combo);
                    save_replay(replay_directory, profile->best_replay_names[3], demo,
                                rec_pos + 2, 1);
                    new_personal_best[3] = 1;
                }
                for (rank = 1; rank < 6; rank++) {
                    if (ply[player_id]->ccc[rank - 1] > profile->ccc[rank - 1]) {
                        profile->ccc[rank - 1] = ply[player_id]->ccc[rank - 1];
                        myDeleteFile(replay_directory, profile->best_replay_names[4 + rank]);
                        sprintf(profile->best_replay_names[4 + rank], "%s_best_cc%d_%d.itr",
                                profile->handle, rank, ply[player_id]->ccc[rank - 1]);
                        save_replay(replay_directory, profile->best_replay_names[4 + rank],
                                    demo, rec_pos + 2, 1);
                        new_personal_best[4 + rank] = 1;
                    }
                }
                for (rank = 1; rank < 6; rank++) {
                    if (ply[player_id]->jcTop[rank - 1] > profile->jc[rank - 1]) {
                        profile->jc[rank - 1] = ply[player_id]->jcTop[rank - 1];
                        myDeleteFile(replay_directory, profile->best_replay_names[9 + rank]);
                        sprintf(profile->best_replay_names[9 + rank], "%s_best_jj%d_%d.itr",
                                profile->handle, rank, ply[player_id]->jcTop[rank - 1]);
                        save_replay(replay_directory, profile->best_replay_names[9 + rank],
                                    demo, rec_pos + 2, 1);
                        new_personal_best[9 + rank] = 1;
                    }
                }
            }

            if (save_replay(replay_directory, "last_game.itr", demo, rec_pos + 2, 1) < 0) {
                my_alert("Failed to save replay.", "(last_game.itr)", 0, 1);
                uberChecksum = 0;
            } else {
                char fbuf[2048];
                Treplay *rr;

                sprintf(fbuf, "%slast_game.itr", replay_directory);
                rr = load_replay(fbuf);
                if (rr) {
                    uberChecksum = calc_replay_checksum(demo);
                    destroy_replay(rr);
                }
            }
        }
    } else {
        syncProfileFromOptions();
    }

    /* lines 4641..4643 */
    if (!quit) {
        save_profile(profile);

        /* lines 4650..4683: highscore qualification */
        if (!closeButtonClicked) {
            int rank;   /* qualify, qualifyValue, gotHigh and gameover_bmp_id live in the enclosing
                         * DWARF block 133269, which opens here and runs into REGION W5 */

            for (i = 0; i < 15; i++)
                qualify[i] = 0;
            qualifyValue[0] = ply[player_id]->level * 10 + ply[player_id]->score;
            qualifyValue[2] = ply[player_id]->level;
            qualifyValue[1] = ply[player_id]->best_combo;
            qualifyValue[3] = ply[player_id]->biggest_lost_combo;
            qualifyValue[4] = ply[player_id]->no_combo_top_floor;
            for (i = 0; i < 5; i++) {
                qualifyValue[5 + i] = ply[player_id]->ccc[i];
                qualifyValue[10 + i] = ply[player_id]->jcTop[i];
            }
            quit = 0;
            gotHigh = 0;
            for (rank = 0; rank < 15; rank++) {
                qualify[rank] = qualify_hisc_table(hisc_tables[rank], qualifyValue[rank]);
                gotHigh += qualify[rank];
            }

            if (recording) {
                gameover_bmp_id = (gotHigh > 0) ? 0x3e : 0x37;
            } else {
                gotHigh = 0;
                gameover_bmp_id = 0x37;
            }
            if (is_playing_custom_game)
                gameover_bmp_id = 0x37;

            if (gotHigh) {
                if (!is_playing_custom_game) {
                    log2file(" player qualified for highscore");
                    play_sound(sounds[7], 0, 0);
                }
            } else {
                log2file(" player did not qualify for highscore");
                play_sound(speaker[1], 0, 0);
            }

            if (debug) {
                /* continues in REGION W5 */
            }
        }
    }

    /* REGION W5: lines 4687..5021 (results screens, name entry, highscore entry, epilogue, replay menu) */
    }

    return play_again;
}
