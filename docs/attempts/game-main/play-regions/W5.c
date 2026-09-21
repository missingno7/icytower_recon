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

    /* REGION W5: lines 4687..5021 (results screens, name entry, highscore entry, epilogue, replay menu) */
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
                             is_playing_custom_game ? 0 : recording);            /* 4704 */
                if (isGuest && gotHigh && !is_playing_custom_game && !recording) { /* 4705 */
                    textout_centre_ex(swap_screen, data[52].dat, "Enter your initials",
                                       320, (int)(hy * 2.0 + 80.0), -1, -1);          /* 4706 */
                }
                scrollerY++;  /* ? cmp/sbb idiom on the wait counter, simplified, 4709 */
                if (scrollerY <= ply[player_id]->level * 5 && scrollerY <= 250) {     /* 4710 */
                    play_sound(sounds[6], 0, 1);                                      /* 4711 */
                    if (custom.falling)                                               /* 4712 */
                        stop_sample(custom.falling);
                    ply[player_id]->shake = 24;                                       /* 4714 */
                }
                if (ply[player_id]->shake) {                                          /* 4716 */
                    blit(swap_screen, screen, 0, new_rand() % 8, 0, 0,
                         swap_screen->w, swap_screen->h);                             /* 4718 */
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
                if (ply[player_id]->shake == 0 && scrollerY > 0)  /* ? approximated loop-exit predicate */
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
                if (key[KEY_F1])                                                       /* 4802 */
                    take_screenshot(swap_screen);                                      /* 4803 */
                if (hurry_y + 99 <= 578)                                               /* 4808 */
                    hurry_y -= 2;
                draw_frame(swap_screen);                                               /* 4809 */
                draw_results(swap_screen, data[alpha_pos].dat, 480, qualify,
                             qualifyValue, is_playing_custom_game ? 0 : recording); /* 4810 */
                if (isGuest && gotHigh && !is_playing_custom_game && !recording) {  /* 4811 */
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
                               20, rank_y + 0x46, -1, -1);                               /* 4822 */
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
                    play_sound(sounds[6], 0, 1);                                          /* 4845 */
                    if (custom.falling)                                                   /* 4846 */
                        stop_sample(custom.falling);
                    ply[player_id]->shake = 24;                                           /* 4850 */
                    scrollerY = 0;
                }
                if (ply[player_id]->shake) {                                              /* 4852 */
                    blit(swap_screen, screen, 0, new_rand() % 8, 0, 0,
                         swap_screen->w, swap_screen->h);                                 /* 4855 */
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
                        if (letters[pos] != (char)0xa4) {                                  /* 4895 */
                            if (pos != 0)
                                pos++;
                            else
                                pos--;                       /* ? mirrors 4899's esi<=1 special case */
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
                    textout_centre_ex(swap_screen, data[54].dat, "A new start floor",
                                       320, 0x12c, -1, -1);                                    /* 4981 */
                    textout_centre_ex(swap_screen, data[54].dat, "has been unlocked!",
                                       320, 0x15e, -1, -1);                                    /* 4982 */
                    textout_centre_ex(swap_screen, data[54].dat,
                                       "(Get it in the options menu)",
                                       320, 0x1b8, -1, -1);                                    /* 4983 */
                    play_sound(sounds[2], 0, 0);                                                /* 4984 */
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

    return play_again;
}
