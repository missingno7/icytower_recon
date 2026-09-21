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

    /* REGION W4: lines 4374..4683 (post-game accounting, gameData XML, replay files, profile, highscore qualification) */

    /* REGION W5: lines 4687..5021 (results screens, name entry, highscore entry, epilogue, replay menu) */

    return play_again;
}
