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
            /* 3717..3732: fall-height "shake" accumulator. old_map_pos captures map.offset
             * before this update (ebx, live only in a register -- DWARF gives it no stack
             * slot, matching "never written" in the skeleton check: it is read once, right
             * back out). The bracket ladder (thresholds 160/140/120/100/80/60/40/20/0) builds
             * scroll_acc (DW_OP_reg1/ecx across this whole span) as a running total, not a
             * mutually-exclusive choice: each of the lower 7 thresholds (jne skip-just-the-
             * add-and-fall-through, evidenced at 3722..3728) adds its delta on top of
             * whichever base the first (140) test picked, and the y>=0 test (fldz/fucompp,
             * 3728) is unconditionally true for a valid y -- kept literal per the evidenced
             * compare, see report. map.offset, y and level are then updated once from
             * old_map_pos + scroll_acc (the single store at 3729/3731/3732), not per bracket. */
            if (ply[player_id]->y < 160.0) {                            /* 3719 */
                old_map_pos = map.offset;                                /* 3717 (evidence: read here) */
                scroll_acc = (ply[player_id]->y >= 140.0) ? 2 : 1;       /* 3721 */
                if (ply[player_id]->y >= 120.0)                         /* 3722 */
                    scroll_acc++;
                if (ply[player_id]->y >= 100.0)                         /* 3723 */
                    scroll_acc++;
                if (ply[player_id]->y >= 80.0)                          /* 3724 */
                    scroll_acc++;
                if (ply[player_id]->y >= 60.0)                          /* 3725 */
                    scroll_acc++;
                if (ply[player_id]->y >= 40.0)                          /* 3726 */
                    scroll_acc += 2;
                if (ply[player_id]->y >= 20.0)                          /* 3727 */
                    scroll_acc += 2;
                if (ply[player_id]->y >= 0.0)                           /* 3728; ? always true for a valid y */
                    scroll_acc += 3;
                map.offset = old_map_pos + scroll_acc;                  /* 3729 */
                ply[player_id]->y += scroll_acc;                        /* 3731 */
                level += scroll_acc;                                    /* 3732 */
                tot_scroll = scroll_acc;                                /* shares ecx with scroll_acc through
                                                                          * the collision switch below (evidence:
                                                                          * DW_OP_reg1 live range extends to 3823) */
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

        /* lastY shares level's stack slot (-0x92c(%ebp)/-2348 in the DWARF dump); no
         * separate store to that address exists between the level updates above and
         * the switch below, so the switch's second argument is simply level's
         * current value carried over under a different DWARF name. */
        lastY = level;                                                  /* ? evidence: shared slot, no distinct write found */

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
