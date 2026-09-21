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
    /* UNRESOLVED: a compiler stack temp at -0x928(%ebp) is also zeroed here as part of the same
     * reset block (line 3520); it matches no DWARF local in play.json (locals + nested-block locals
     * all checked) and no global at that PC -- no statement emitted for it. */
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

    while (playing && !closeButtonClicked) {   /* lines 3534..3536 */
        cycle_count = 0;                                 /* line 3540 */
        logic_count++;                                   /* line 3542 */
        step_count++;                                    /* line 3543 */
        fall_count++;                                     /* line 3544 */
        time_cheat_count++;                               /* line 3545 */
        musicCounter++;                                   /* line 3546 */
        if (!itrcheck) {                                  /* line 3549 */
            if (hasFocus != lastFocus) {                  /* line 3550-3551 */
                if (!hasFocus) {
                    /* line 3562-3567: losing focus, stop the background track */
                    if (checkMusicVoiceID >= 0) {
                        voice_stop(checkMusicVoiceID);
                    }
                    checkMusicVoiceID = -1;
                    stopGameMusic();
                } else {
                    /* line 3552-3559: gaining focus, restart the background track */
                    if (bg_beat) {
                        checkMusicVoiceID = play_sample(bg_beat, 0, 128, 1000, 1);
                    }
                    startGameMusic();
                    totMusics = 0;
                    accMusics = 0.0f;
                    musicCounter = 0;
                }
            }
            lastFocus = hasFocus;                         /* line 3569 */
        }
        if (!itrcheck) {                                  /* line 3574 (compiled as its own re-test of
                                                             * itrcheck, redundant with the block above) */
            if (checkMusicVoiceID >= 0) {                 /* line 3574 */
                int pos = voice_get_position(checkMusicVoiceID); /* line 3575; "pos" is a block-scoped
                                                             * temp with no DWARF location at this PC --
                                                             * introduced here only to hold the single
                                                             * call's result for reuse, matching the
                                                             * single voice_get_position call in evidence */
                if (pos < lastMusicPos) {                 /* line 3576 */
                    musicCounter = 0;
                }
                /* lines 3580-3585: running average of a 44000/pos "speed" ratio into accMusics,
                 * gated on that ratio being > 0.01 (x87 fucompp/fnstsw/test $0x45 idiom); see report
                 * for the derivation of the comparison direction. */
                if (44000.0 / pos > 0.01) {               /* line 3583 */
                    totMusics++;                          /* line 3585 */
                    accMusics += (44000.0 / pos) * 50.0 / musicCounter; /* line 3584 */
                }
                lastMusicPos = pos;                       /* line 3585 (tail) */
            }
        }
        if (recording && map.offset > 100 && !ply[player_id]->dead) { /* line 3595-3597 */
            if (time_cheat_count == 1000) {
                /* lines 3604-3661: periodic clock()/QueryPerformanceCounter()/time() cross-check,
                 * recorded into the demo replay's time-cheat-detection arrays. The exact x87 formulas
                 * below are a best-effort reconstruction (see report); the calls and field targets are
                 * evidenced directly. */
                double clockSpeed;
                double qpcSpeed;
                int clockDelta = clock() - clockTimeStart;         /* line 3604-3605 */
                if (clockDelta > 0) {
                    clockSpeed = 1.0 / clockDelta;
                } else {
                    clockSpeed = -0.05;                             /* line 3610 (fallthrough constant) */
                }
                QueryPerformanceFrequency(&li);                     /* line 3610 */
                qpc_freq = li.LowPart;
                QueryPerformanceCounter(&li);                       /* line 3612 */
                qpcSpeed = qpc_freq / (1000.0 * (li.LowPart - qpc_start)); /* line 3615 */
                timeTimeEnd = time(NULL);                           /* line 3623 */
                demo->tc_c_data[demo->tc_posts] = clockSpeed;       /* line 3636 */
                demo->tc_q_data[demo->tc_posts] = qpcSpeed;         /* line 3637 */
                demo->tc_t_data[demo->tc_posts] =
                    20.0 / (50.0 * (timeTimeEnd - timeTimeStart));  /* line 3638 */
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
            if (key[KEY_1]) { if (allow_smpl) start_reward(5); }
            if (key[KEY_2]) { if (allow_smpl) start_reward(7); }
            if (key[KEY_3]) { if (allow_smpl) start_reward(15); }
            if (key[KEY_4]) { if (allow_smpl) start_reward(25); }
            if (key[KEY_5]) { if (allow_smpl) start_reward(35); }
            if (key[KEY_6]) { if (allow_smpl) start_reward(50); }
            if (key[KEY_7]) { if (allow_smpl) start_reward(70); }
            if (key[KEY_8]) { if (allow_smpl) start_reward(100); }
            if (key[KEY_9]) { if (allow_smpl) start_reward(140); }
            if (key[KEY_0]) { if (allow_smpl) start_reward(200); }
            /* line 3692 */
            allow_smpl = !(key[KEY_1] || key[KEY_2] || key[KEY_3] ||
                           key[KEY_4] || key[KEY_5] || key[KEY_6] ||
                           key[KEY_7] || key[KEY_8] || key[KEY_9] ||
                           key[KEY_0]);
        }
        midX = (int)ply[player_id]->x;                    /* line 3698 */
        midY = (int)ply[player_id]->y;                    /* line 3699 */

        handle_player_input(&ctrl);                                    /* 3702 */
        update_player(ply[player_id]);                                 /* 3703 */
        if (!itrcheck) {                                                /* 3706 */
            if (ply[player_id]->rotate && ply[player_id]->in_combo && options.flash) {  /* 3707 */
                create_particle(stars, (int)ply[player_id]->x, (int)ply[player_id]->y - 16);  /* 3708 */
            } else {
                for (i = 0; i < 512; i++) {                             /* 3711 */
                    if (stars[i].intensity)
                        update_particle(&stars[i]);
                }
            }
            /* 3717..3732: fall-height "shake" accumulator kept in map.offset;
             * bracket boundaries (160/140/120/100/80/60/40/20/0) and per-bracket
             * deltas (1,1,1,1,1,2,2,3) are evidenced by the fucom cascade; the exact
             * >= vs > edges on each threshold are approximate. */
            if (ply[player_id]->y < 160.0) {                            /* 3719 */
                if (ply[player_id]->y >= 140.0)                         /* 3721 */
                    map.offset = 1;
                else if (ply[player_id]->y >= 120.0)                    /* 3722 */
                    map.offset++;
                else if (ply[player_id]->y >= 100.0)                    /* 3723 */
                    map.offset++;
                else if (ply[player_id]->y >= 80.0)                     /* 3724 */
                    map.offset++;
                else if (ply[player_id]->y >= 60.0)                     /* 3725 */
                    map.offset++;
                else if (ply[player_id]->y >= 40.0)                     /* 3726 */
                    map.offset += 2;
                else if (ply[player_id]->y >= 20.0)                     /* 3727 */
                    map.offset += 2;
                else                                                    /* 3728 */
                    map.offset += 3;
                ply[player_id]->y += map.offset;                        /* 3731 */
                level += map.offset;                                    /* 3732 */
            }
            if (!ply[player_id]->dead)                                  /* 3736 */
                clock_angle++;
            /* 3738..3758: proceed only once the shake accumulator has built up and the
             * player is alive; otherwise reset clock_angle/fall_count (only while alive). */
            if (map.offset <= 100 || ply[player_id]->dead) {            /* 3738 */
                if (!ply[player_id]->dead) {                            /* 3757 */
                    clock_angle = 0;                                    /* 3758 */
                    fall_count = 0;
                }
            } else {
                if (scroll == -1)                                       /* 3739 */
                    scroll = start_speeds[demo->start_speed];           /* 3740 */
                if (scroll) {                                            /* 3742 */
                    map.offset += scroll;                               /* 3751 */
                    ply[player_id]->y += scroll;                        /* 3753 */
                    level += scroll;                                    /* 3754 */
                } else if (step_count & 1) {                            /* 3743 */
                    map.offset++;                                       /* 3744 */
                    ply[player_id]->y += 1.0;                           /* 3746 */
                    level++;                                            /* 3747 */
                }
            }
            any13 = map.offset;                                         /* 3763 */
            if (hurry_y + 99 <= 578)                                    /* 3765 */
                hurry_y -= 2;
            if (demo->speed_increase) {                                 /* 3766 */
                if (!ply[player_id]->dead &&                            /* 3767 */
                    speeds[next_speed] < fall_count &&
                    scroll > 4) {
                    ply[player_id]->ccc[next_speed] = ply[player_id]->level;  /* 3768 */
                    next_speed++;                                       /* 3770 */
                    scroll++;                                           /* 3771 */
                    hurry_y = 477;                                      /* 3772 */
                    play_sound(speaker[0], 0, 0);                       /* 3773 */
                    play_sound(sounds[4], 0, 0);                        /* 3774 */
                }
            }
            if (scroll == 5) {                                          /* 3778 */
                fall_count -= 45;                                       /* 3779 */
                if (!ply[player_id]->dead)                              /* 3780 */
                    clock_angle -= 45;
            }
            /* 3783..3788: a signed-mod-16 cadence check between step_count and the
             * map.offset accumulator gates the floor add on the historical
             * evidence, but every traced predecessor of 3789 converges on the call, so
             * it is written here as effectively unconditional; predicate not fully
             * resolved. */
            add_floor(&map);                                            /* 3789 */
        }

        switch (collision_type) {                                       /* 3814 */
        case 3:
            handle_player_collision_original(midX, lastY);               /* 3815 */
            break;
        case 2:
            handle_player_collision_old(midX, lastY);                    /* 3817 */
            break;
        case 1:
            handle_player_collision_vector(midX, lastY);                 /* 3819 */
            break;
        case 0:
            handle_player_collision_vector_2(midX, lastY);               /* 3821 */
            break;
        case 4:
            handle_player_collision_combo(midX, lastY);                  /* 3823 */
            break;
        default:
            allegro_message("unknown collision type");                  /* 3826 */
            break;
        }

        if (ply[player_id]->rotate)                                     /* 3833 */
            ply[player_id]->angle += 0x80000;
        if (ply[player_id]->in_combo) {                                 /* 3837 */
            ply[player_id]->in_combo--;                                 /* 3838 */
            if (!ply[player_id]->in_combo && ply[player_id]->acc_jumps > 1) {  /* 3839..3840 */
                int rewResult;
                Tgd_combo c;

                ply[player_id]->score += ply[player_id]->acc_level * ply[player_id]->acc_level;  /* 3841 */
                rewResult = start_reward(ply[player_id]->acc_level);     /* 3842 */
                if (recording && !is_playing_custom_game)                /* 3843 */
                    profile->rewards[rewResult]++;
                totComboFloors += ply[player_id]->acc_level;             /* 3844 */
                numComboJumps++;                                         /* 3845 */
                c.length = ply[player_id]->acc_level;                    /* 3848 */
                c.start = gdComboStart;                                  /* 3849 */
                c.end = gdComboStart + ply[player_id]->acc_level;        /* 3850 */
                add_combo(gameData, &c);                                 /* 3851 */
                ply[player_id]->latest_combo = ply[player_id]->acc_level;  /* 3853 */
                if (ply[player_id]->acc_level > ply[player_id]->best_combo)  /* 3854 */
                    ply[player_id]->best_combo = ply[player_id]->acc_level;  /* 3855 */
            }
        }

        if (ply[player_id]->status) {                                   /* 3862 */
            level = (get_level(&map, (int)ply[player_id]->y) - 1) / 10;  /* 3864..3868 */
            diff = level - ply[player_id]->level;                       /* 3869..3870 */
            if (diff != 0) {                                             /* 3870 */
                if (diff == gdLastJumpDiff) {                            /* 3871 */
                    jumpSequence.num++;                                  /* 3882 */
                } else {
                    jumpSequence.dist = gdLastJumpDiff;                  /* 3874 */
                    add_jump_sequence(gameData, &jumpSequence);          /* 3875 */
                    jumpSequence.num = 1;                                /* 3878 */
                    jumpSequence.start = ply[player_id]->level;          /* 3879 */
                }
                gdLastJumpDiff = diff;                                  /* 3885 */
            }
            if (level >= ply[player_id]->level) {                       /* 3891 */
                diff = level - ply[player_id]->level;                   /* 3893 */
                if (diff != lastJumpLength)                             /* 3896 */
                    lastJumpLength = 0;                                 /* 3897 */
                for (i = 0; i < 5; i++) {                                /* 3897..3904 */
                    if (ply[player_id]->jc[i] > ply[player_id]->jcTop[i])
                        ply[player_id]->jcTop[i] = ply[player_id]->jc[i];
                    ply[player_id]->jc[i] = 0;
                }
                if (diff > 0) {                                          /* 3911 */
                    if (diff <= 5)                                       /* 3912 */
                        ply[player_id]->jc[diff - 1]++;                  /* 3913 */
                    if (diff != 1) {                                     /* 3919 */
                        if (ply[player_id]->in_combo) {                  /* 3920 */
                            ply[player_id]->acc_level += diff;           /* 3921 */
                            ply[player_id]->acc_jumps++;                 /* 3922 */
                        } else {
                            ply[player_id]->acc_level = diff;            /* 3926 */
                            ply[player_id]->acc_jumps = 1;               /* 3927 */
                        }
                        ply[player_id]->in_combo = 100;                  /* 3923/3928 */
                        lastJumpLength = diff;                          /* 3928 tail */
                    } else if (!ply[player_id]->in_combo) {              /* 3932 */
                        lastJumpLength = diff;
                    }
                }
                ply[player_id]->in_combo = 1;  /* 3933; ? overwrites the in_combo=100 set just above, evidenced as-is */
                if (!ply[player_id]->in_combo)                           /* 3936 */
                    gdComboStart = level;                                /* 3937 */
            }

            if (ply[player_id]->in_combo) {                              /* 3943 */
                ply[player_id]->in_combo = 1;
                for (i = 0; i < 5; i++) {                                /* 3945..3952 */
                    if (ply[player_id]->jc[i] > ply[player_id]->jcTop[i])
                        ply[player_id]->jcTop[i] = ply[player_id]->jc[i];
                    ply[player_id]->jc[i] = 0;
                }
                ply[player_id]->level = level;                          /* 3962 */
                if (!numComboJumps &&                                    /* 3967 */
                    ply[player_id]->no_combo_top_floor < ply[player_id]->level)
                    ply[player_id]->no_combo_top_floor = gdComboStart;   /* 3969 */
            }
        }

        /* 3976..3999: rank-up / top-of-screen handling */
        if (ply[player_id]->y < 540.0 && !ply[player_id]->dead &&        /* 3976 */
            ply[player_id]->in_combo && ply[player_id]->acc_jumps > 1) { /* 3978 */
            flash = (itrcheck < 1) ? -1 : 0;  /* 3977; ? consumer of this mask is outside W2 */
            ply[player_id]->biggest_lost_combo = ply[player_id]->acc_level;  /* 3979 */
            ply[player_id]->in_combo = 0;                                /* 3981 */
            ply[player_id]->dead = 1;                                    /* 3982 */
            play_sound(custom.falling, 0, 1);                            /* 3983 */
            endTime = time(0);                                           /* 3985 */
            for (i = 0; i < 5; i++) {                                    /* 3988..3995 */
                if (ply[player_id]->jc[i] <= ply[player_id]->jcTop[i])
                    ply[player_id]->jcTop[i] = ply[player_id]->jc[i];
                ply[player_id]->jc[i] = 0;
            }
            jumpSequence.dist = gdLastJumpDiff;                          /* 3999 */
        }

        add_jump_sequence(gameData, &jumpSequence);                             /* 4000 */
        {
            /* aightScore: compiler-only stack temp (-0x928(%ebp)), no DWARF local covers it;
             * comboActive: synthetic gate reconstructing the tail-merged machine code. See report. */
            int aightScore;
            int comboActive = 0;

            if (numComboJumps) {                                               /* 4003 */
                lastJumpLength = 0;
                aightScore = 1;
                comboActive = 1;
            } else if (ply[player_id]->no_combo_top_floor < ply[player_id]->level) { /* 4003/4004 */
                ply[player_id]->no_combo_top_floor = ply[player_id]->level;
                lastJumpLength = 0;
                aightScore = 1;
                comboActive = 1;
            }
            if (comboActive) {
                if (ply[player_id]->y < 900.0 && !game_over) {                  /* 4010 */
                    play_sound(speaker[1], 0, 0);                               /* 4012 */
                    game_over = 2;
                }
                aightScore++;                                                   /* 4015 */
                if (aightScore > 250 && aightScore <= ply[player_id]->level * 5) { /* 4016 */
                    play_sound(sounds[6], 1, 0);                                /* 4017 */
                    if (custom.falling)                                        /* 4018 */
                        stop_sample(custom.falling);                           /* 4019 */
                }
                ply[player_id]->shake = 0x18;                                   /* 4022 */
                aightScore = 0;
                if (next_aight > ply[player_id]->level) {                       /* 4027 */
                    play_sound(sounds[2], 0, 0);                                /* 4028 */
                }
            }
        }
        if (!options.flash) {                                                  /* 4029 */
            midX = next_aight / 2;                                             /* 4031 */
            for (i = 0; i < midX; i++) {                                       /* 4029/4123 */
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
            ply[player_id]->edge_drawn = 0;
        if (ply[player_id]->edge_drawn != 0) {                                 /* 4043 */
            if (ply[player_id]->edge_drawn == 11 && ply[player_id]->status == 0) /* 4044 */
                play_sound(custom.edge, 1, 1);                                 /* 4044 tail */
            if (ply[player_id]->edge_drawn == 50)                              /* 4045 */
                ply[player_id]->edge_drawn = 0;                                /* 4046 */
        }
        if (debug && ply[player_id]->dead > 99) {                              /* 4049/4050 */
            if (recording && ply[player_id]->dead > 100)                       /* 4056 */
                playing = 0;
        } else if (!debug) {
            if (recording && ply[player_id]->dead > 100)                       /* 4056 */
                playing = 0;
        }
        if (!itrcheck && key[KEY_F1]) {                                        /* 4062 */
            int t0, t1;
            t0 = time(NULL);                                                   /* 4063 */
            take_screenshot(swap_screen);                                      /* 4064 */
            if (key[KEY_F1]) {                                                 /* 4065 (see report: odd self-target) */
                t1 = time(NULL);                                               /* 4066 */
                if (t1 - t0 > 0)                                               /* 4067 */
                    startTime += t1 - t0;                                      /* 4068 */
            }
            if (gameMusicVoiceID >= 0)                                        /* 4075 */
                musicCounter = (int)(voice_get_position(gameMusicVoiceID) * 50.0 / 44000.0); /* 4077 */
            clockTimeStart = clock();                                          /* 4083 */
            QueryPerformanceCounter(&li);                                      /* 4085 */
            qpc_start = li.LowPart;                                            /* 4086 */
            timeTimeStart = time(NULL);                                        /* 4090 */
            lastMusicPos = 0;
            accMusics = 0.0;
        }
        if (ply[player_id]->shake) {                                          /* 4094 */
            ply[player_id]->shake--;                                          /* 4095 */
            shake = new_rand() % 8;                                           /* 4097 */
        }
        update_frame();                                                       /* 4100 */
        if (!quit && closeButtonClicked) {                                    /* 4104 */
            quit = 1;
            playing = 0;
        }
        if (recording) {                                                      /* 4109 */
            if (key[KEY_ESC]) {                                               /* 4110 */
                if (ply[player_id]->dead) {                                   /* 4111 */
                    log2file("  player quit after dying");                    /* 4112 */
                    playing = 0;
                } else {
                    /* REGION W3a: ESC pause screen, lines 4117..4182 */
                    int pauseTime, fc, ca; /* block-scoped DWARF locals (block 132596), not in the 52-local skeleton */

                    pauseTime = time(NULL);                                   /* 4117 */
                    fc = fall_count;                                          /* 4118 */
                    ca = clock_angle;                                         /* 4119 */
                    log2file("  game paused with esc");                      /* 4120 */
                    for (i = 0; i < 640; i += 2) {                            /* 4122 */
                        vline(swap_screen, i, 0, 480, 0);                     /* draw.inl:46 */
                        hline(swap_screen, 0, i, 640, 0);                     /* draw.inl:54 */
                    }
                    textout_centre_ex(swap_screen, data[50].dat,
                                       "DO YOU REALLY WANT TO EXIT?", 320, 160, -1, -1); /* 4126 */
                    textout_centre_ex(swap_screen, data[52].dat,
                                       "Press any key to resume", 320, 210, -1, -1);     /* 4127 */
                    textout_centre_ex(swap_screen, data[52].dat,
                                       "Press ESC to exit", 320, 240, -1, -1);            /* 4128 */
                    blit_to_screen(swap_screen);                              /* 4129 */
                    play_sound(custom.wazup, 0, 1);                           /* 4130 */
                    poll_control(&ctrl, 0);                                   /* 4132 */
                    while (1) {                                               /* 4133..4144 (see report: simplified) */
                        while (key[KEY_ESC]) {                                /* ESC held */
                            poll_control(&ctrl, 0);
                            rest(2);
                        }
                        if (is_any(&ctrl) || is_pause(&ctrl))
                            break;
                        if (closeButtonClicked) {                             /* 4142 */
                            clear_keybuf();                                   /* 4137 */
                            break;
                        }
                        poll_control(&ctrl, 0);                               /* 4139 */
                        rest(2);                                              /* 4140 */
                        if (keypressed())                                    /* 4138 */
                            break;
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
                    if (time(NULL) - pauseTime > 0)                           /* 4159/4160 */
                        startTime += time(NULL) - pauseTime;                  /* 4161 */
                    if (gameMusicVoiceID >= 0)                                /* 4168 */
                        musicCounter = (int)(voice_get_position(gameMusicVoiceID) * 50.0 / 44000.0); /* 4170 */
                    clockTimeStart = clock();                                 /* 4175 */
                    QueryPerformanceCounter(&li);                             /* 4177 */
                    qpc_start = li.LowPart;                                   /* 4178 */
                    timeTimeStart = time(NULL);                               /* 4182 */
                    lastMusicPos = 0;
                    accMusics = 0.0;
                }
            }
            if (is_pause(&ctrl) && ply[player_id]->dead == 0) {               /* 4186 */
                /* REGION W3b: pause-key screen, lines 4187..4245 (near-identical to W3a) */
                int pauseTime, fc, ca; /* block-scoped DWARF locals (block 132838), not in the 52-local skeleton */

                pauseTime = time(NULL);                                       /* 4187 */
                fc = fall_count;                                              /* 4188 */
                ca = clock_angle;                                             /* 4189 */
                log2file("  game paused with pause key");                     /* 4190 */
                for (i = 0; i < 640; i += 2) {                                /* 4192 */
                    vline(swap_screen, i, 0, 480, 0);                         /* draw.inl:46 */
                    hline(swap_screen, 0, i, 640, 0);                         /* draw.inl:54 */
                }
                textout_centre_ex(swap_screen, data[50].dat,
                                   "Game Paused", 320, 160, -1, -1);           /* 4196 */
                textout_centre_ex(swap_screen, data[52].dat,
                                   "Press any key to resume", 320, 210, -1, -1); /* 4197 */
                blit_to_screen(swap_screen);                                  /* 4198 */
                play_sound(custom.wazup, 0, 1);                               /* 4199 */
                poll_control(&ctrl, 0);                                       /* 4200 */
                while (1) {                                                   /* 4201..4209 (see report: simplified) */
                    if (is_any(&ctrl) || is_pause(&ctrl))
                        break;
                    if (key[KEY_ESC]) {                                       /* ESC */
                        clear_keybuf();                                       /* 4206 */
                        break;
                    }
                    poll_control(&ctrl, 0);                                   /* 4208 */
                    rest(2);                                                  /* 4209 */
                    if (keypressed())                                        /* 4207 */
                        break;
                }
                poll_control(&ctrl, 0);                                       /* 4212 */
                while (is_pause(&ctrl)) {                                     /* 4213 */
                    if (key[KEY_ESC])
                        break;
                    poll_control(&ctrl, 0);                                   /* 4214 */
                    rest(2);                                                  /* 4215 */
                }
                fall_count = fc;                                              /* 4219 */
                clock_angle = ca;                                             /* 4220 */
                log2file("  game unpaused");                                  /* 4221 */
                if (time(NULL) - pauseTime > 0)                               /* 4222/4223 */
                    startTime += time(NULL) - pauseTime;                      /* 4224 */
                if (gameMusicVoiceID >= 0)                                    /* 4231 */
                    musicCounter = (int)(voice_get_position(gameMusicVoiceID) * 50.0 / 44000.0); /* 4233 */
                clockTimeStart = clock();                                     /* 4238 */
                QueryPerformanceCounter(&li);                                 /* 4240 */
                qpc_start = li.LowPart;                                       /* 4241 */
                timeTimeStart = time(NULL);                                   /* 4245 */
                lastMusicPos = 0;
                accMusics = 0.0;
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
                        if (key[KEY_SPACE])                                   /* 4273 */
                            poll_control(&rec_ctrl, 1);
                        if (!key[KEY_SPACE] && !key[KEY_RIGHT] &&
                            !key[KEY_ESC] && !key[KEY_UP]) {                  /* 4274 */
                            poll_control(&rec_ctrl, 1);                       /* 4275 */
                            if (key[KEY_F1])                                  /* 4276 */
                                take_screenshot(swap_screen);                 /* 4277 */
                        }
                    }
                } else {
                    if (key[KEY_RIGHT]) {                                    /* 4287 */
                        fast_forward++;                                       /* 4288 */
                        fast_fast_forward = 0;                                /* 4289 */
                    } else if (key[KEY_UP]) {                                /* 4295 */
                        if (ply[player_id]->dead == 0 &&
                            ply[player_id]->level < demo->floor - 10) {       /* 4296 */
                            fast_fast_forward++;                              /* 4297 */
                            fast_forward = 0;                                 /* 4298 */
                            next_floor = ((ply[player_id]->level + 100) / 100) * 100; /* 4299 */
                            if (next_floor > demo->floor - 10)                /* 4301 */
                                next_floor = demo->floor - 10;
                        }
                    }
                    if (ply[player_id]->level >= next_floor) {                /* 4309 */
                        fast_fast_forward = 0;                                /* 4310 */
                        next_floor = -1;
                    }
                }
            }
        }
        if (!itrcheck) {                                                     /* 4319 */
            static int someCounter;
            int comboSpeedDiv;

            someCounter++;                                                    /* 4324 */
            comboSpeedDiv = fast_forward ? 4 : 1;                             /* 4327 */
            if (fast_fast_forward)                                            /* 4330 */
                comboSpeedDiv = 32;
            if (!quit && someCounter % comboSpeedDiv == 0) {                  /* 4337 */
                draw_frame(swap_screen);                                      /* 4338 */
                if (ply[player_id]->shake) {                                  /* 4346 */
                    acquire_screen();                                          /* gfx.inl:221/203 */
                    blit(swap_screen, swap_screen, 0, shake, 0, 0,
                         swap_screen->w, swap_screen->h);                      /* 4348 */
                    blit_to_screen(swap_screen);                              /* 4349 */
                    release_screen();                                         /* gfx.inl:227/212 */
                } else {
                    blit_to_screen(swap_screen);                              /* 4353 */
                }
                if (!debug) {                                                 /* 4356 */
                    while (cycle_count == 0)                                  /* 4357 */
                        rest(2);
                } else if (key[KEY_TAB] && key[KEY_LSHIFT]) {                  /* 4360 */
                    while (cycle_count <= 7)                                  /* 4361/4363 */
                        rest(2);
                }
            }
        }
        rest(2);                                                             /* 4369 */
    }

    /* lines 4374..4426: recording gates a small profile play-time update vs. the full
     * gameData stats snapshot + itrcheck-gated XML dump. */
    if (recording) {
        diff = endTime - startTime;
        if (diff > 0)
            profile->seconds_spent_playing += diff;
    } else {
        gameData->score = ply[player_id]->level * 10 + ply[player_id]->score;
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
                keys_pressed[k] = time_cheat_count; /* ? the fill value traces to
                                                       * time_cheat_count's fixed stack slot;
                                                       * a plain 0-fill was expected -- see report */
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
            gameData->left = keys_pressed[0];
            gameData->right = keys_pressed[1];
            gameData->jump = keys_pressed[2];
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
            demo->rejump = 0; /* UNRESOLVED: 0x4fe530 used as demo->rejump source, unnamed in
                                * evidence (thematically resembles global `rejump` at 0x4fdcd8,
                                * but that DWARF address does not match -- see report) */
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
            int qualify[15];
            int qualifyValue[15];
            int gotHigh;
            int gameover_bmp_id;
            int rank;

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
                    play_sound(NULL, 0, 0); /* UNRESOLVED: 0x4dd2fc used as SAMPLE*, unnamed
                                              * in evidence -- see report */
                }
            } else {
                log2file(" player did not qualify for highscore");
                play_sound(NULL, 0, 0); /* UNRESOLVED: 0x4dd2c0 used as SAMPLE*, unnamed
                                          * in evidence -- see report */
            }

            if (debug) {
                /* continues in REGION W5 */
            }
        }
    }

    {
        /* DWARF block (outer, shared with REGION W4): results-panel/highscore state. */
        float hy;
        int gotHigh;
        int qualify[15];
        int qualifyValue[15];
        int alpha_pos;
        char *initials;

        {
            /* DWARF block (inner): name-entry / rank-up state. */
            int pos;
            char letters[31] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ .\244";
            int len;
            char buf[8] = { '.', 0, '.', 0, '.', 0, 0, 0 };
            int skip_keys;
            int isGuest;
            int scrollerY;
            int new_rank_id;
            int rank_bmp_id;
            int rank_y;
            int k;
            char guestName[4];
            char postName[32];

            len = strlen(letters) - 1;                                              /* 4688 */
            isGuest = !stricmp(profile->handle, "guest");                           /* 4692 */

            /* results screen: slide the results panel in and wait for the
             * highscore chime / fade timer (4695..4737). */
            for (;;) {
                if (hy < 140.0)                                                     /* 4695 */
                    scrollerY = rank_bmp_id;  /* ? unresolved -0x928 slot, best effort */
                cycle_count = 0;                                                     /* 4696 */
                ply[player_id]->dead -= 16;                                          /* 4697 */
                hy = hy + (136.0 - hy) * 0.1;                                        /* 4699 */
                update_frame();                                                      /* 4700 */
                for (i = 0; i < 512; i++)                                            /* 4701 */
                    update_particle(&stars[i]);  /* ? original also walks characters[] as the loop bound */
                if (hurry_y + 99 <= 578)                                             /* 4702 */
                    hurry_y -= 2;
                draw_frame(swap_screen);                                             /* 4703 */
                draw_results(swap_screen, data[alpha_pos].dat, 480, qualify,
                             qualifyValue,
                             *(int *)0x4dd188 ? 0 : recording);   /* is_playing_custom_game, undeclared in TU; 4704 */
                if (isGuest && gotHigh && !*(int *)0x4dd188 && !recording) {    /* is_playing_custom_game; 4705 */
                    textout_centre_ex(swap_screen, data[52].dat, "Enter your initials",
                                       320, (int)(hy * 2.0 + 80.0), -1, -1);          /* 4706 */
                }
                scrollerY++;  /* ? cmp/sbb idiom on the wait counter, simplified, 4709 */
                if (scrollerY <= ply[player_id]->level * 5 && scrollerY <= 250) {     /* 4710 */
                    play_sound(*(SAMPLE **)0x4dd2f8, 0, 1);      /* UNRESOLVED SAMPLE* global 0x4dd2f8; 4711 */
                    if (*(SAMPLE **)0x4fac00)                                         /* 4712 */
                        stop_sample(*(SAMPLE **)0x4fac00);        /* UNRESOLVED SAMPLE* global 0x4fac00 */
                    ply[player_id]->shake = 24;                                       /* 4714 */
                }
                if (ply[player_id]->shake) {                                          /* 4716 */
                    blit(swap_screen, *(BITMAP **)0x4dda8c, 0, new_rand() % 8, 0, 0,
                         swap_screen->w, swap_screen->h);   /* UNRESOLVED BITMAP* global 0x4dda8c; 4718 */
                    ply[player_id]->shake--;                                          /* 4720 */
                }
                blit_to_screen(swap_screen);                                          /* 4722 */
                if (*(char *)0x5069b7) {                        /* UNRESOLVED flag (key[KEY_PRTSCR]-style); 4725 */
                    take_screenshot(swap_screen);                                     /* 4726 */
                }
                if (*(char *)0x5069c8 && *(char *)0x5069fb) {    /* UNRESOLVED flags; 4729..4731 */
                    rest(2);                                                          /* 4734 */
                    if (cycle_count == 0)
                        continue;
                }
                if (ply[player_id]->shake == 0 && scrollerY > 0)  /* ? approximated loop-exit predicate */
                    break;
            }
            ply[player_id]->dead = 0;                                                 /* 4737 */
            clear_keybuf();                                                           /* 4738 */

            /* summary scroller message: custom/guest/personal-record tip (4742..4775). */
            if (!recording) {
                summary_scroller_message[0] = 0;                                      /* 4743 */
                if ((*(int *)0x4dd188)) {
                    memcpy(summary_scroller_message,
                           "Custom mode is crazy fun but does not add to your profile. "
                           "Play Classic Mode to compete in the highscore lists and "
                           "climb in rank!", 0x82);                                    /* 4746 */
                } else if (gotHigh) {
                    memcpy(summary_scroller_message, "New personal records!    ", 0x1a); /* 4753 */
                } else {
                    char *tip = "You're playing in guest mode. Start a profile and "
                                "record your progress!";
                    if (!isGuest)
                        tip = *(char **)(0x4bc0c0 + (new_rand() % 45) * 4);
                        /* UNRESOLVED: 0x4bc0c0 is DWARF global "hints" (main.c:142,
                         * char*[45]), not declared in this TU; 4770 */
                    strcpy(summary_scroller_message, tip);                              /* 4775 */
                }
            }

            /* name entry loop: scroller/rank banner setup and per-frame draw + input
             * (4781..4923). */
            init_scroller(&summary_scroller, data[54].dat, summary_scroller_message,
                           640, 30, -1);                                              /* 4781 */
            scroll_scroller(&summary_scroller, -150);                                  /* 4782 */
            new_rank_id = get_rank_id(profile);                                        /* 4787 */

            for (;;) {
                if (skip_keys == 20)                    /* ? approximated loop-exit predicate, 4792 */
                    break;
                if (closeButtonClicked)                                                /* 4793 */
                    break;
                cycle_count = 0;                                                       /* 4797 */
                step_count++;                                                          /* 4798 */
                update_frame();                                                        /* 4800 */
                if (*(char *)0x5069b7)                  /* UNRESOLVED flag; 4802 */
                    take_screenshot(swap_screen);                                      /* 4803 */
                if (hurry_y + 99 <= 578)                                               /* 4808 */
                    hurry_y -= 2;
                draw_frame(swap_screen);                                               /* 4809 */
                draw_results(swap_screen, data[alpha_pos].dat, 480, qualify,
                             qualifyValue, (*(int *)0x4dd188) ? 0 : recording);     /* 4810 */
                if (isGuest && gotHigh && !(*(int *)0x4dd188) && !recording) {      /* 4811 */
                    textout_centre_ex(swap_screen, data[52].dat, "Enter your initials",
                                       320, (int)(hy * 2.0 + 80.0), -1, -1);            /* 4812 */
                    if (pos >= 1)                                                       /* 4814 */
                        textout_centre_ex(swap_screen, data[52].dat, &buf[0],
                                           300, (int)(hy * 2.0 + 120.0), -1, -1);
                    if (pos >= 2)                                                       /* 4815 */
                        textout_centre_ex(swap_screen, data[52].dat, &buf[2],
                                           320, (int)(hy * 2.0 + 120.0), -1, -1);
                    if (pos >= 3)                                                       /* 4816 */
                        textout_centre_ex(swap_screen, data[52].dat, &buf[4],
                                           340, (int)(hy * 2.0 + 120.0), -1, -1);
                    if (pos >= 3)                                                       /* 4817 */
                        textout_centre_ex(swap_screen, data[52].dat, "%",
                                           360, (int)(hy * 2.0 + 120.0), -1, -1);
                }
                if (new_rank_id != current_rank_id) {                                   /* 4820 */
                    alpha_pos = 0;                                                       /* 4821 */
                    rank_y = 0x244;
                    skip_keys = 20;
                    pos = 0;
                    rank_bmp_id = new_rank_id + 0x4a;
                    draw_sprite(swap_screen, data[rank_bmp_id].dat, 20, rank_y);         /* 4821 (inlined) */
                    textout_ex(swap_screen, data[52].dat, "rank up!",
                               rank_y + 0x46, 20, -1, -1);                               /* 4822 */
                    rank_y = rank_y + (int)((320 - rank_y) * 0.1);                       /* 4823 */
                }
                if (summary_scroller_message[0]) {                                       /* 4827 */
                    scroll_scroller(&summary_scroller, -2);                              /* 4828 */
                    drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);                              /* 4829 */
                    set_trans_blender(0, 0, 0, 110);                                     /* 4830 */
                    rectfill(swap_screen, 0, 0, 639, 20, makecol(0, 0, 0));              /* 4831 */
                    rectfill(swap_screen, 0, 0, 639, 18, makecol(0, 0, 0));              /* 4832 */
                    rectfill(swap_screen, 0, 0, 639, 16, makecol(0, 0, 0));              /* 4833 */
                    solid_mode();                                                         /* 4834 */
                    draw_scroller(&summary_scroller, swap_screen, 1, alpha_pos,
                                   makecol(150, 150, 150));                               /* 4835 */
                    if (!draw_scroller(&summary_scroller, swap_screen, 0, alpha_pos,
                                        makecol(200, 200, 200)))                          /* 4836 */
                        restart_scroller(&summary_scroller);
                }
                alpha_pos = (int)(alpha_pos - alpha_pos * 0.1);   /* ? decay approximation, 4838 */

                if (scrollerY <= ply[player_id]->level * 5 && scrollerY <= 250) {         /* 4844 */
                    play_sound(*(SAMPLE **)0x4dd2f8, 0, 1);       /* UNRESOLVED SAMPLE* global; 4845 */
                    if (*(SAMPLE **)0x4fac00)                                             /* 4846 */
                        stop_sample(*(SAMPLE **)0x4fac00);
                    ply[player_id]->shake = 24;                                           /* 4850 */
                    scrollerY = 0;
                }
                if (ply[player_id]->shake) {                                              /* 4852 */
                    blit(swap_screen, *(BITMAP **)0x4dda8c, 0, new_rand() % 8, 0, 0,
                         swap_screen->w, swap_screen->h);        /* UNRESOLVED BITMAP* global; 4855 */
                    ply[player_id]->shake--;                                              /* 4857 */
                }
                blit_to_screen(swap_screen);                                              /* 4860 */

                if (isGuest && gotHigh && !(*(int *)0x4dd188) && !recording) {         /* 4863 */
                    poll_control(&ctrl, 0);                                                /* 4864 */
                    if (is_right(&ctrl)) {                                                 /* 4884 */
                        pos++;                                                             /* 4885 */
                        if (pos >= len)                                                    /* 4886 */
                            pos = 0;
                    }
                    if (is_left(&ctrl)) {                                                  /* 4889 */
                        pos--;                                                             /* 4891 */
                        if (pos < 0)
                            pos = len;
                    }
                    if (is_fire(&ctrl)) {                                                  /* 4894 */
                        if (letters[pos] != (char)0xa4) {                                  /* 4895 */
                            if (pos != 0)
                                pos++;
                            else
                                pos--;                       /* ? mirrors 4899's esi<=1 special case */
                        }
                    }
                    if (!is_any(&ctrl) && !*(char *)0x5069d5 && *(char *)0x5069c7) {        /* 4913 */
                        if (pos <= 2)
                            buf[pos * 2] = letters[pos];                                    /* 4915 */
                    }
                } else {
                    poll_control(&ctrl, 0);                                                 /* 4920 */
                    if (skip_keys != 20)                                                    /* 4923 */
                        skip_keys--;
                    if (isGuest && gotHigh && !(*(int *)0x4dd188)) {                    /* 4921 */
                        if (keypressed()) {                                                 /* 4922 */
                            if (skip_keys != 20) {
                                k = readkey() & 0xff;                                        /* 4866 */
                                k -= 0x20;
                                if (k >= 0 && k < len) {                                     /* 4871 */
                                    buf[pos * 2] = letters[k];                               /* 4875 */
                                    pos++;                                                    /* 4876 */
                                    if (pos == 3)
                                        skip_keys = 20;                                       /* 4877 */
                                }
                            }
                        }
                    }
                }
                if (*(char *)0x5069c8 && *(char *)0x5069fb) {   /* UNRESOLVED flags; 4929..4931 */
                    rest(2);                                                                 /* 4932 */
                    if (cycle_count == 0)
                        continue;
                }
            }

            /* highscore entry: commit the typed initials into every qualified table
             * (4940..4951). */
            if (!(*(int *)0x4dd188) && recording) {                                     /* 4940 */
                guestName[0] = buf[0];                                                       /* 4941 */
                guestName[1] = buf[2];
                guestName[2] = buf[4];
                guestName[3] = 0;
                if (isGuest) {                                                               /* 4943 */
                    initials = guestName;
                } else {
                    strcpy(postName, profile->handle);
                    initials = postName;
                }
                for (k = 0; k < 15; k++) {                                                   /* 4948 */
                    if (qualify[k] > 0) {                                                    /* 4949 */
                        enter_hisc_table(hisc_tables[k], qualifyValue[k], initials);          /* 4950 */
                        sort_hisc_table(hisc_tables[k]);                                      /* 4951 */
                    }
                }
            }

            /* post-game "new start floor unlocked" message (4963..4987). */
            if (recording && !debug && !(*(int *)0x4dd188)) {                            /* 4963 */
                int f = ply[player_id]->level / 100;                                          /* 4964 */
                if (f > oldUnlockedFloors && f <= 9) {                                        /* 4966 */
                    fadeOut(16);                                                              /* 4968 */
                    blit(data[126].dat, swap_screen, 0, 0, 0, 0, 640, 480);                   /* 4971 */
                    set_trans_blender(0, 0, 0, 158);                                          /* 4974 */
                    drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);                                   /* 4975 */
                    if (gfx_driver)    /* ? unresolved global 0x4dda84, assumed gfx_driver */  /* 4976 */
                        rectfill(swap_screen, 0, 0, gfx_driver->w, gfx_driver->h,
                                 makecol(0, 0, 0));
                    solid_mode();                                                             /* 4977 */
                    draw_sprite(swap_screen, data[58].dat,
                                320 - ((BITMAP *)data[58].dat)->w / 2, 20);                    /* 4980 (inlined) */
                    textout_centre_ex(swap_screen, data[54].dat, "A new start floor",
                                       320, 0x12c, -1, -1);                                    /* 4981 */
                    textout_centre_ex(swap_screen, data[54].dat, "has been unlocked!",
                                       320, 0x15e, -1, -1);                                    /* 4982 */
                    textout_centre_ex(swap_screen, data[54].dat,
                                       "(Get it in the options menu)",
                                       320, 0x1b8, -1, -1);                                    /* 4983 */
                    play_sound(*(SAMPLE **)0x4dd2e8, 0, 0);   /* UNRESOLVED SAMPLE* global; 4984 */
                    fadeIn(swap_screen, 16);                                                   /* 4985 */
                }
            }
        }

        /* epilogue: save config, stop music, offer the replay menu (4994..5021). */
        save_config();                                                                        /* 4994 */
        stopGameMusic();                                                                       /* 4997 */
        if (gameMusicVoiceID >= 0)                                                             /* 4998 */
            voice_stop(gameMusicVoiceID);                                                      /* 4999 */

        play_again = 0;                                                                        /* 5002 */
        if (recording) {                                                                        /* 5002 */
            if (debug) {                                                                        /* 5002 */
                play_sound(*(SAMPLE **)0x4dd2c4, 0, 0);      /* UNRESOLVED SAMPLE* global; 5011 */
            } else {
                in_replay_menu = 1;                                                              /* 5003 */
                play_again = do_replay_menu();                                                   /* 5004 */
                in_replay_menu = 0;                                                              /* 5005 */
                if (recording)                                                                   /* 5011 */
                    play_sound(*(SAMPLE **)0x4dd2c4, 0, 0);
            }
            stopGameMusic();                                                                     /* 5013 */
            if (gameMusicVoiceID >= 0)                                                            /* 5014 */
                voice_stop(gameMusicVoiceID);                                                     /* 5015 */
            clear_bitmap(*(BITMAP **)0x4dda8c);      /* UNRESOLVED BITMAP* global 0x4dda8c; inlined */
        }
    }

    return play_again;
}
