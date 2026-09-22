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

    /* REGION W5: lines 4687..5021 (results screens, name entry, highscore entry, epilogue, replay menu) */
    {
        /* hy, gotHigh, qualify and qualifyValue are declared in the enclosing DWARF block 133269,
         * which opens in REGION W4 at main.c:4650 and runs to the end of the function. */
        hy = 0.0f;         /* slides in toward 136.0 */
        int alpha_pos = 0; /* first read is data[alpha_pos].dat in the loop below */
        char *initials = NULL;

        {
            /* DWARF block (inner): name-entry / rank-up state. */
            int pos;
            char letters[31] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ .\244";
            int len;
            char buf[8] = { '.', 0, '.', 0, '.', 0, 0, 0 };
            int skip_keys;
            int isGuest;
            int new_rank_id;
            int rank_bmp_id;
            int rank_y;
            int k;
            char guestName[4];
            char postName[32];

            len = strlen(letters) - 1;                                              /* 4688 */
            isGuest = !stricmp(profile->handle, "guest");                           /* 4692 */

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
            gotHigh = 0;
            for (i = 0; i < 15; i++) {
                qualify[i] = qualify_hisc_table(hisc_tables[i], qualifyValue[i]);
                gotHigh += qualify[i];
            }
            if (!recording || is_playing_custom_game)
                gotHigh = 0;
            /* the three tables above live in DWARF block 133269 (main.c:4650..end), the same
             * lexical block as REGION W4's highscore accounting; that region's own copies go
             * out of scope at its closing brace right before this marker, so this region
             * cannot see the values its own draw_results()/enter_hisc_table() calls need and
             * recomputes them identically to main.c:4650..4679 (out of this region's reach) */

            /* results screen: slide the results panel in and wait for the
             * highscore chime / fade timer (4695..4737). */
            for (;;) {
                if (hy < 140.0)                                                     /* 4695 */
                    falling = 0;  /* offset 11886 stores esi (0 here) while the panel is
                                     * still sliding in, pinning the shake counter until hy
                                     * settles past 140; an earlier pass misread this as a
                                     * store into the rank sprite id, which is not yet set */
                cycle_count = 0;                                                     /* 4696 */
                ply[player_id]->dead -= 16;                                          /* 4697 */
                hy = hy + (136.0 - hy) * 0.1;                                        /* 4699 */
                update_frame();                                                      /* 4700 */
                for (i = 0; i < 512; i++)                                            /* 4701 */
                    update_particle(&stars[i]);  /* ? original also walks characters[] as the loop bound */
                if (hurry_y + 99 <= 578)                                             /* 4702 */
                    hurry_y -= 2;
                draw_frame(swap_screen);                                             /* 4703 */
                /* 4704 */ draw_results(swap_screen, data[alpha_pos].dat, 480, qualify,
                             qualifyValue,
                             is_playing_custom_game ? 0 : recording);
                if (isGuest && gotHigh && !is_playing_custom_game && !recording) { /* 4705 */
                    /* 4706 */ textout_centre_ex(swap_screen, data[52].dat, "Enter your initials",
                                       320, (int)(hy * 2.0 + 80.0), -1, -1);
                }
                falling++;  /* 4709: cmp/sbb idiom on the wait counter, simplified */
                if (falling <= ply[player_id]->level * 5 && falling <= 250) {     /* 4710 */
                    play_sound(sounds[6], 0, 1);                                      /* 4711 */
                    if (custom.falling)                                               /* 4712 */
                        stop_sample(custom.falling);
                    ply[player_id]->shake = 24;                                       /* 4714 */
                }
                if (ply[player_id]->shake) {                                          /* 4716 */
                    /* 4718 */ blit(swap_screen, screen, 0, new_rand() % 8, 0, 0,
                         swap_screen->w, swap_screen->h);
                    ply[player_id]->shake--;                                          /* 4720 */
                }
                blit_to_screen(swap_screen);                                          /* 4722 */
                if (key[KEY_F1]) {                                                    /* 4725 */
                    take_screenshot(swap_screen);                                     /* 4726 */
                }
                if (key[KEY_TAB] && key[KEY_LSHIFT]) {                                /* 4729..4731 */
                    rest(2);                                                          /* 4734 */
                    if (cycle_count == 0)
                        continue;
                }
                if (ply[player_id]->shake == 0 && falling > 0)  /* ? approximated loop-exit predicate */
                    break;
            }
            ply[player_id]->dead = 0;                                                 /* 4737 */
            clear_keybuf();                                                           /* 4738 */

            /* summary scroller message: custom/guest/personal-record tip (4742..4775). */
            if (!recording) {
                summary_scroller_message[0] = 0;                                      /* 4743 */
                if (is_playing_custom_game) {
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
                        tip = hints[new_rand() % 45];                                   /* 4770 */
                    strcpy(summary_scroller_message, tip);                              /* 4775 */
                }
            }

            /* name entry loop: scroller/rank banner setup and per-frame draw + input
             * (4781..4923). */
            /* 4781 */ init_scroller(&summary_scroller, data[54].dat, summary_scroller_message,
                           640, 30, -1);
            scroll_scroller(&summary_scroller, -150);                                  /* 4782 */
            new_rank_id = get_rank_id(profile);                                        /* 4787 */
            pos = 0;
            skip_keys = 0;

            for (;;) {
                if (skip_keys == 20)                    /* 4792: approximated loop-exit predicate */
                    break;
                if (closeButtonClicked)                                                /* 4793 */
                    break;
                cycle_count = 0;                                                       /* 4797 */
                step_count++;                                                          /* 4798 */
                update_frame();                                                        /* 4800 */
                if (key[KEY_F1])                                                       /* 4802 */
                    take_screenshot(swap_screen);                                      /* 4803 */
                if (hurry_y + 99 <= 578)                                               /* 4808 */
                    hurry_y -= 2;
                draw_frame(swap_screen);                                               /* 4809 */
                /* 4810 */ draw_results(swap_screen, data[alpha_pos].dat, 480, qualify,
                             qualifyValue, is_playing_custom_game ? 0 : recording);
                if (isGuest && gotHigh && !is_playing_custom_game && !recording) {  /* 4811 */
                    /* 4812 */ textout_centre_ex(swap_screen, data[52].dat, "Enter your initials",
                                       320, (int)(hy * 2.0 + 80.0), -1, -1);
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
                    /* 4822 */ textout_ex(swap_screen, data[52].dat, "rank up!",
                               20, rank_y + 0x46, -1, -1);
                    /* 4823 */ rank_y = rank_y + (int)((320 - rank_y) * 0.1);
                }
                if (summary_scroller_message[0]) {                                       /* 4827 */
                    scroll_scroller(&summary_scroller, -2);                              /* 4828 */
                    drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);                              /* 4829 */
                    set_trans_blender(0, 0, 0, 110);                                     /* 4830 */
                    rectfill(swap_screen, 0, 0, 639, 20, makecol(0, 0, 0));              /* 4831 */
                    rectfill(swap_screen, 0, 0, 639, 18, makecol(0, 0, 0));              /* 4832 */
                    rectfill(swap_screen, 0, 0, 639, 16, makecol(0, 0, 0));              /* 4833 */
                    solid_mode();                                                         /* 4834 */
                    /* 4835 */ draw_scroller(&summary_scroller, swap_screen, 1, alpha_pos,
                                   makecol(150, 150, 150));
                    /* 4836 */ if (!draw_scroller(&summary_scroller, swap_screen, 0, alpha_pos,
                                        makecol(200, 200, 200)))
                        restart_scroller(&summary_scroller);
                }
                alpha_pos = (int)(alpha_pos - alpha_pos * 0.1);   /* 4838: decay approximation */

                if (falling <= ply[player_id]->level * 5 && falling <= 250) {         /* 4844 */
                    play_sound(sounds[6], 0, 1);                                          /* 4845 */
                    if (custom.falling)                                                   /* 4846 */
                        stop_sample(custom.falling);
                    ply[player_id]->shake = 24;                                           /* 4850 */
                    falling = 0;
                }
                if (ply[player_id]->shake) {                                              /* 4852 */
                    /* 4855 */ blit(swap_screen, screen, 0, new_rand() % 8, 0, 0,
                         swap_screen->w, swap_screen->h);
                    ply[player_id]->shake--;                                              /* 4857 */
                }
                blit_to_screen(swap_screen);                                              /* 4860 */

                if (isGuest && gotHigh && !is_playing_custom_game && !recording) {     /* 4863 */
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
                        if (letters[pos] == (char)0xa4) {                                  /* 4895: blank slot confirmed */
                            buf[pos * 2] = '.';                                             /* 4896 */
                            if (pos > 1)                                                    /* 4899 */
                                pos--;
                            else
                                pos++;
                            if (skip_keys != 20)                                            /* 4900 */
                                skip_keys = 19;                                              /* 4902 */
                        } else if (pos != 0) {               /* ? best-effort for the non-blank confirm case */
                            pos++;
                        } else {
                            pos--;
                        }
                    }
                    if (!is_any(&ctrl) && !key[KEY_DEL] && key[KEY_BACKSPACE]) {            /* 4913 */
                        if (pos <= 2)
                            buf[pos * 2] = letters[pos];                                    /* 4915 */
                    }
                } else {
                    poll_control(&ctrl, 0);                                                 /* 4920 */
                    if (skip_keys != 20)                                                    /* 4923 */
                        skip_keys--;
                    if (isGuest && gotHigh && !is_playing_custom_game) {                /* 4921 */
                        if (keypressed()) {                                                 /* 4922 */
                            if (skip_keys != 20) {
                                int matched = 0;
                                char typed = 0;

                                k = readkey() & 0xff;                                        /* 4866 */
                                k -= 0x20;             /* lowercase ascii -> uppercase letter code */
                                if (k == -24) {                                              /* 4867: BACKSPACE (ascii 8) */
                                    typed = (char)0xa4;
                                    matched = 1;
                                } else if (k == 14) {                                        /* 4868: '.' (ascii 46) */
                                    typed = '.';
                                    matched = 1;
                                } else if (k == 1) {                                         /* 4869: '!' (ascii 33) */
                                    typed = '!';
                                    matched = 1;
                                } else if (k != 0x20) {                                      /* 4870: '@' (ascii 64) is dropped */
                                    for (i = 0; i < len; i++) {                              /* 4871..4872: scan letters[] */
                                        if (letters[i] == (char)k) {
                                            typed = letters[i];
                                            matched = 1;
                                            break;
                                        }
                                    }
                                }
                                if (matched) {                                               /* 4875 */
                                    buf[pos * 2] = typed;
                                    pos++;                                                    /* 4876 */
                                    if (pos == 3)                                            /* 4877 */
                                        skip_keys = 20;
                                }
                            }
                        }
                    }
                }
                if (key[KEY_TAB] && key[KEY_LSHIFT]) {           /* 4929..4931 */
                    rest(2);                                                                 /* 4932 */
                    if (cycle_count == 0)
                        continue;
                }
            }

            /* highscore entry: commit the typed initials into every qualified table
             * (4940..4951). */
            if (!is_playing_custom_game && recording) {                                  /* 4940 */
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
            if (recording && !debug && !is_playing_custom_game) {                        /* 4963 */
                int f = ply[player_id]->level / 100;                                          /* 4964 */
                if (f > oldUnlockedFloors && f <= 9) {                                        /* 4966 */
                    fadeOut(16);                                                              /* 4968 */
                    blit(data[126].dat, swap_screen, 0, 0, 0, 0, 640, 480);                   /* 4971 */
                    set_trans_blender(0, 0, 0, 158);                                          /* 4974 */
                    drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);                                   /* 4975 */
                    if (gfx_driver)                                                            /* 4976 */
                        rectfill(swap_screen, 0, 0, gfx_driver->w, gfx_driver->h,
                                 makecol(0, 0, 0));
                    solid_mode();                                                             /* 4977 */
                    draw_sprite(swap_screen, data[58].dat,
                                320 - ((BITMAP *)data[58].dat)->w / 2, 20);                    /* 4980 (inlined) */
                    /* 4981 */ textout_centre_ex(swap_screen, data[54].dat, "A new start floor",
                                       320, 0x12c, -1, -1);
                    /* 4982 */ textout_centre_ex(swap_screen, data[54].dat, "has been unlocked!",
                                       320, 0x15e, -1, -1);
                    /* 4983 */ textout_centre_ex(swap_screen, data[54].dat,
                                       "(Get it in the options menu)",
                                       320, 0x1b8, -1, -1);
                    play_sound(sounds[2], 0, 0);                                                /* 4984 */
                    fadeIn(swap_screen, 16);                                                   /* 4985 */
                    while (!key[KEY_ESC] && !key[KEY_ENTER] && !key[KEY_SPACE]) {  /* 4986..4987 */
                        /* ? the two-stage key test at these lines (checked twice, once before
                         * and once after the fall-through) may debounce a stale press; no
                         * distinguishing branch structure survives at the C level */
                    }
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
                play_sound(speaker[2], 0, 0);                 /* 5011 */
            } else {
                in_replay_menu = 1;                                                              /* 5003 */
                play_again = do_replay_menu();                                                   /* 5004 */
                in_replay_menu = 0;                                                              /* 5005 */
                if (recording)                                                                   /* 5011 */
                    play_sound(speaker[2], 0, 0);
            }
            stopGameMusic();                                                                     /* 5013 */
            if (gameMusicVoiceID >= 0)                                                            /* 5014 */
                voice_stop(gameMusicVoiceID);                                                     /* 5015 */
            clear_bitmap(screen);                                                                 /* inlined */
        }
    }

    }   /* end of DWARF block 133269, opened in REGION W4 */

    return play_again;
}
