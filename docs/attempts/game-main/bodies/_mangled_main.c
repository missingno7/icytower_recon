/* Source recovery of main.c:5761, 0x415f10..0x4166a2.  This retains the
 * startup, main-menu action dispatch, game/replay transitions, and orderly
 * shutdown recovered from the original control-flow branches. */
int _mangled_main(int argc, char **argv)
{
    char executable_name[1024];
    char logfile_path[256];
    FILE *fp;
    int i;
    int ret;
    int must_fade;
    int play_result;
    int redraw_menu;

    if (!LoadLibraryA("exchndl.dll"))
        printf("No exception handler present, RPTs will not be generated");
    allegro_init();
    register_png_file_type();
    get_executable_name(executable_name, sizeof(executable_name));
    replace_filename(working_directory, executable_name, "data",
                     sizeof(working_directory));
    chdir(working_directory);
    memset(logfile_path, 0, sizeof(logfile_path));
    get_logfile_path(logfile_path, sizeof(logfile_path));
    fp = fopen(logfile_path, "wt");
    if (fp) {
        fprintf(fp, "Icy Tower v%s - log file\n----------------------------\n",
                "1.5.1");
        fclose(fp);
    }
    for (i = 0; i < argc; i++)
        if (!stricmp(argv[i], "-check"))
            itrcheck = 1;
    log2file("Game started with the following commands:");
    for (i = 0; i < argc; i++)
        log2file("    %s", argv[i]);
    log2file("Working directory is:\n    %s", working_directory);
    if (!init_game(argc,argv)) {
        if (!dropped_file_is_not_a_replay) {
            log2file("* Failed to initialize the game *");
            allegro_message("Failed to initialize the game.");
        }
        log2file("Cleaning up Allegro");
        uninit_game();
        log2file("Done...");
        return 1;
    }

    if (itrcheck && demo) {
        log2file("Running replay.");
        run_demo(NULL);
        if (itrcheck) {
            log2file("Exiting Allegro");
            allegro_exit();
            log2file("\nDone...");
            exit(0);
        }
    }
    if (itrcheck)
        load_new_ad_image();
    init_scroller(&greeting_scroller, data[54].dat, scroller_greetings,
                  640, 30, -1);
    menu_params.font=data[51].dat;
    menu_params.bullet=data[72].dat;
    menu_params.pos=0;
    menu_params.data=data;
    init_control(&menu_params.ctrl);
    reset_menu(main_menu,&menu_params,0);
    startMenuMusic();
    clear_keybuf();

    must_fade=1;
    if (options.timesStarted==1 && !stricmp("guest",options.lastProfile)) {
        main_menu_callback();
        draw_menu(swap_screen,main_menu,&menu_params,355,285,0);
        fadeIn(swap_screen,16);
        force_create_profile();
        syncOptionsFromProfile();
        must_fade=0;
    }
    redraw_menu=1;
    while (!closeButtonClicked) {
        if (redraw_menu) {
            main_menu_callback();
            draw_menu(swap_screen,main_menu,&menu_params,355,285,0);
            if (must_fade)
                fadeIn(swap_screen,16);
            else
                blit_to_screen(swap_screen);
            redraw_menu=0;
        }
        ret=handle_menu(main_menu,&menu_params,&ctrl,swap_screen,
                        main_menu_callback,355,285,0);

        if (ret=='e' || ret==0x85) {
            in_replay_menu=(ret!='e');
            fadeOut(16);
            stopMenuMusic();
            if (demo) {
                destroy_replay(demo);
                demo=NULL;
            }
            do {
                play_result=0;
                if (new_game()) {
                    play_result=play();
                    end_game();
                    fadeOut(16);
                } else
                    fadeOut(16);
            } while (play_result && !closeButtonClicked);
            if (bg_menu)
                play_sample(bg_menu, options.msc_volume, 128, 1000, 1);
            must_fade=1;
        }
        else if (ret=='i') {
            view_scores(hisc_tables,hisc_names);
            must_fade=0;
        }
        else if (ret=='h') {
            fadeOut(16);
            show_instructions();
            must_fade=1;
        }
        else if (ret=='z') {
            if (demo) {
                destroy_replay(demo);
                demo=NULL;
            }
            for (;;) {
                demo=replay_selector(&ctrl,replay_directory);
                if (!demo) {
                    must_fade=0;
                    break;
                }
                fadeOut(16);
                stopMenuMusic();
                run_demo(NULL);
                fadeOut(16);
                main_menu_callback();
                draw_menu(swap_screen,main_menu,&menu_params,355,285,0);
                fadeIn(swap_screen,32);
                if (closeButtonClicked)
                    break;
                if (bg_menu)
                    if (options.msc_volume)
                        play_sample(bg_menu, options.msc_volume, 128, 1000, 1);
            }
        }
        else if (ret=='k')
            break;
        rest(2);
        if (closeButtonClicked || ret=='k')
            break;
        redraw_menu=1;
    }
    fadeOut(16);
    show_credits();
    stopMenuMusic();
    uninit_game();
    return 0;
}
