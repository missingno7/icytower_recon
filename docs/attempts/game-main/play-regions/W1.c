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
    rec_ctrl = ctrl;                                   /* line 3439 */
    if (!itrcheck) {                                   /* line 3441 (else-branch placed inline by -O2) */
        oldUnlockedFloors = profile->best_floor / 100; /* line 3442 */
        current_rank_id = get_rank_id(profile);        /* line 3443; get_rank_id has no visible prototype
                                                          * in main.c (declared in profile.c taking
                                                          * Tprofile_rank *; that type isn't visible here,
                                                          * so the cast used by other callers is omitted) */
    } else {
        current_rank_id = 0;
        oldUnlockedFloors = 0;
    }
    if (recording) {                                   /* line 3473 */
        demo->tc_posts = 0;                             /* line 3474 */
        for (i = 0; i < 100; i++) {                     /* line 3475 */
            demo->tc_c_data[i] = 0.0f;                  /* line 3476 */
            demo->tc_q_data[i] = 0.0f;                  /* line 3477 */
            demo->tc_t_data[i] = 0.0f;                  /* line 3478 */
            demo->tc_s_data[i] = 0.0f;                  /* line 3479 */
            demo->tc_f_data[i] = 0.0f;                  /* line 3480 */
        }
    }
    log2file(" setting up play data");                 /* line 3485 */
    fall_count = 0;                                     /* line 3486 */
    clock_angle = 0;                                    /* line 3487 */
    map.offset = 0;                                     /* line 3488 */
    fast_forward = 0;                                   /* line 3490 */
    fast_fast_forward = 0;                               /* line 3491 */
    update_frame();                                      /* line 3493 */
    if (!itrcheck) {                                     /* line 3494 */
        draw_frame(swap_screen);                         /* line 3495 */
        fadeIn(swap_screen, 16);                         /* line 3497 */
        play_sound(custom.yo, 0, 0);                     /* line 3498 */
        startGameMusic();                                /* line 3499 */
    }
    if (!itrcheck && bg_beat) {                          /* line 3502-3503 (compiled as its own re-test
                                                            * of itrcheck, redundant with the block above) */
        checkMusicVoiceID = play_sample(bg_beat, 0, 128, 1000, 1); /* line 3504 */
    }
    cycle_count = 0;                                     /* line 3510 */
    log2file(" play started");                           /* line 3512 */
    startTime = time(NULL);                              /* line 3513 */
    QueryPerformanceCounter(&li);                        /* line 3519 */
    qpc_start = li.LowPart;                              /* line 3520 */
    totMusics = 0;
    accMusics = 0.0f;
    lastMusicPos = 0;
    musicCounter = 0;
    time_cheat_count = 0;
    lastJumpLength = 0;
    endTime = 0;
    totComboFloors = 0;
    numComboJumps = 0;
    next_floor = -1;
    step_count = 0;
    shake = 0;
    aightScore = 0;
    game_over = 0;
    allow_smpl = 1;
    next_aight = 50;
    next_speed = 0;
    scroll = -1;
    quit = 0;
    QueryPerformanceFrequency(&li);                      /* line 3522; result unused here (its DWARF
                                                            * live range only starts at the second QPF
                                                            * call inside the loop, line 3610) */
    clockTimeStart = clock();                            /* line 3528 */
    timeTimeStart = time(NULL);                          /* line 3530 */
    playing = 1;                                         /* line 3533: the original enters the loop
                                                            * without testing playing (offset 351 jumps
                                                            * straight to the closeButtonClicked test),
                                                            * so it is known non-zero here; the value is
                                                            * constant-folded away and emits no code */

    while (playing && !closeButtonClicked) {   /* 3536 (3534 tests playing; both tests and both loop
                                                 * entry/back-edge copies compile to this one physical
                                                 * line, so its bytes are credited to the larger 3536) */
        /* REGION W1b: lines 3540..3699 (per-frame counters, music sync, debug timing, speed steps) */
        cycle_count = 0;                                 /* line 3540 */
        logic_count++;                                   /* line 3542 */
        step_count++;                                    /* line 3543 */
        fall_count++;                                     /* line 3544 */
        time_cheat_count++;                               /* line 3545 */
        musicCounter++;                                   /* line 3546 */
        if (!itrcheck) {                                  /* line 3549 */
            if (hasFocus != lastFocus) {                  /* line 3550-3551 */
                if (hasFocus) {
                    /* line 3552-3559: gaining focus, restart the background track */
                    if (bg_beat) {
                        checkMusicVoiceID = play_sample(bg_beat, 0, 128, 1000, 1); /* 3553 */
                    }
                    startGameMusic();                                             /* 3559 */
                    totMusics = 0;
                    accMusics = 0.0f;
                    musicCounter = 0;
                } else {
                    /* line 3562-3567: losing focus, stop the background track */
                    if (checkMusicVoiceID >= 0) {
                        voice_stop(checkMusicVoiceID);
                    }
                    checkMusicVoiceID = -1;
                    stopGameMusic();
                }
            }
            lastFocus = hasFocus;                         /* line 3569 */
        }
        if (!itrcheck) {                                  /* line 3574 (compiled as its own re-test of
                                                             * itrcheck, redundant with the block above) */
            if (checkMusicVoiceID >= 0) {                 /* line 3574 */
                int vgp;   /* DWARF block 132257 [760..886]: vgp (int), a (float), b (float) */
                float a, b;

                vgp = voice_get_position(checkMusicVoiceID); /* line 3575 */
                if (vgp < lastMusicPos) {                 /* line 3576 */
                    musicCounter = 0;
                }
                /* lines 3580-3585: running average of a 44000/vgp "speed" ratio into accMusics,
                 * gated on that ratio being > 0.01 (x87 fucompp/fnstsw/test $0x45 idiom); see report
                 * for the derivation of the comparison direction. The two named DWARF temps a/b hold
                 * the ratio and the scaled increment across lines 3580-3584. */
                a = 44000.0f / vgp;                       /* lines 3580-3583 */
                if (a > 0.01f) {                          /* line 3583 */
                    b = a * 50.0f / musicCounter;         /* line 3584 */
                    accMusics += b;
                    totMusics++;                          /* line 3585 */
                }
                lastMusicPos = vgp;                       /* line 3585 (tail) */
            }
        }
        if (recording && map.offset > 100 && !ply[player_id]->dead) { /* line 3595 */
            if (time_cheat_count == 1000) {                          /* 3597 */
                /* lines 3604-3661: periodic clock()/QueryPerformanceCounter()/time() cross-check,
                 * recorded into the demo replay's time-cheat-detection arrays. DWARF lexical block
                 * 134356 (3604..3661) declares three doubles our source previously never named:
                 * clockSpeed, qpcSpeed, timeSpeed -- the per-method rate used to gate/derive each
                 * tot*Times value below. The exact x87 formulas are a best-effort reconstruction
                 * from the instruction stream (see report); the calls and field targets are
                 * evidenced directly. */
                double clockSpeed;  /* DWARF block 134356 [3604..3661] */
                double qpcSpeed;
                double timeSpeed;

                clockTimeEnd = clock();                             /* line 3604 */
                clockElapsed = clockTimeEnd - clockTimeStart;       /* line 3605 */
                clockSpeed = 1000.0 / (50.0 * clockElapsed);        /* line 3605 (tail) */
                if (clockSpeed > 0.0) {                             /* 3606 */
                    totClockTimes = 1000.0 * clockSpeed / clockSpeed / 20.0; /* 3606 */
                } else {
                    totClockTimes = -0.05;                          /* 3606 (fallthrough constant) */
                }
                QueryPerformanceFrequency(&li);                     /* line 3610 */
                qpc_freq = li.LowPart;
                QueryPerformanceCounter(&li);                       /* line 3612 */
                qpc_end = li.LowPart;                               /* line 3612 tail */
                qpc_elapsed = qpc_end - qpc_start;                  /* line 3615 */
                qpcSpeed = 20.0 / (50.0 * qpc_elapsed / qpc_freq);  /* line 3615 (tail) */
                totQPCTimes = qpcSpeed;                             /* line 3615 (tail) */
                timeTimeEnd = time(NULL);                           /* line 3623 */
                timeElapsed = timeTimeEnd - timeTimeStart;          /* line 3638 */
                timeSpeed = 20.0 / (50.0 * timeElapsed);            /* line 3638 (tail) */
                totTimeTimes = timeSpeed;                           /* line 3638 (tail) */
                demo->tc_c_data[demo->tc_posts] = totClockTimes;    /* line 3636 */
                demo->tc_q_data[demo->tc_posts] = totQPCTimes;      /* line 3637 */
                demo->tc_t_data[demo->tc_posts] = totTimeTimes;     /* line 3638 (tail) */
                demo->tc_f_data[demo->tc_posts] = ply[player_id]->level; /* line 3639 */
                if (totMusics != 0) {                               /* line 3640 */
                    demo->tc_s_data[demo->tc_posts] = 50.0 * accMusics / totMusics; /* line 3641 */
                }
                if (demo->tc_posts <= 97) {                         /* line 3643 */
                    demo->tc_posts++;
                }
                clockTimeStart = clock();                           /* line 3654 */
                QueryPerformanceCounter(&li);                       /* line 3656 */
                qpc_start = li.LowPart;                             /* line 3657 */
                timeTimeStart = time(NULL);                         /* line 3661 */
                totMusics = 0;
                accMusics = 0.0f;
                time_cheat_count = 0;
            }
        }
        if (debug) {                                      /* line 3681 */
            /* lines 3682-3691: ten combo-length reward tiers, keyed to the number-row keys */
            if (key[KEY_1]) { if (allow_smpl) start_reward(5); }      /* 3682 */
            if (key[KEY_2]) { if (allow_smpl) start_reward(7); }      /* 3683 */
            if (key[KEY_3]) { if (allow_smpl) start_reward(15); }     /* 3684 */
            if (key[KEY_4]) { if (allow_smpl) start_reward(25); }     /* 3685 */
            if (key[KEY_5]) { if (allow_smpl) start_reward(35); }     /* 3686 */
            if (key[KEY_6]) { if (allow_smpl) start_reward(50); }     /* 3687 */
            if (key[KEY_7]) { if (allow_smpl) start_reward(70); }     /* 3688 */
            if (key[KEY_8]) { if (allow_smpl) start_reward(100); }    /* 3689 */
            if (key[KEY_9]) { if (allow_smpl) start_reward(140); }    /* 3690 */
            if (key[KEY_0]) { if (allow_smpl) start_reward(200); }    /* 3691 */
            /* line 3692 */
            allow_smpl = !(key[KEY_1] || key[KEY_2] || key[KEY_3] ||
                           key[KEY_4] || key[KEY_5] || key[KEY_6] ||
                           key[KEY_7] || key[KEY_8] || key[KEY_9] ||
                           key[KEY_0]);
        }
        midX = (int)ply[player_id]->x;                    /* line 3698 */
        midY = (int)ply[player_id]->y;                    /* line 3699 */

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

    /* REGION W5: lines 4687..5021 (results screens, name entry, highscore entry, epilogue, replay menu) */
    }

    return play_again;
}
