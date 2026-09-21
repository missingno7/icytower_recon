/* Partial recovery of main.c:1375, 0x40e7dc..0x40fe78.  The oracle starts
 * with packfile/network state, command-line processing, and the platform
 * subsystems before it exposes the datafile-backed game globals. */
int init_game(int argc, char **argv)
{
    char title[64];
    WSADATA wsaData;
    unsigned short wVersionRequested;
    char cfgfilename[256];
    char profiles_dir[1024];
    char tmpHandle[32];
    char *replay_path;
    PACKFILE *cfg;
    DATAFILE *loader;
    DATAFILE *sfx;
    BITMAP *fldLogo;
    Tgamepad *pad;
    int whiteColor;
    int check;
    int i;

    tmpHandle[0]=0;
    init_ok=0;
    log2file("INIT GAME");
    packfile_password(NULL);
    sprintf(title,"Icy Tower v%s","1.5.1");
    set_window_title(title);
    wVersionRequested=MAKEWORD(2,2);
    if (WSAStartup(wVersionRequested,&wsaData)!=0)
        log2file(" !!! Failed to setup Winsock");
    if (LOBYTE(wsaData.wVersion)<2 || HIBYTE(wsaData.wVersion)<2)
        log2file(" !!! Failed to get proper Winsock version (wanted 2.2, got %d.%d)",
                 LOBYTE(wsaData.wVersion),HIBYTE(wsaData.wVersion));
    curr_char=0;
    play_char.value=0;
    characters=NULL;
    replay_path=NULL;
    check=0;
    eyecandy_selection.value=0;
    eyecandy_selection.size=3;
    eyecandy_selection.caption[0]=strdup("Lots");
    eyecandy_selection.caption[1]=strdup("Some");
    eyecandy_selection.caption[2]=strdup("None");
    scroll_speed_selection.value=0;
    scroll_speed_selection.size=6;
    scroll_speed_selection.caption[5]=strdup("Normal");
    scroll_speed_selection.caption[4]=strdup("Hasty");
    scroll_speed_selection.caption[3]=strdup("Fast");
    scroll_speed_selection.caption[2]=strdup("Faster");
    scroll_speed_selection.caption[1]=strdup("Fastest");
    scroll_speed_selection.caption[0]=strdup("Insane");
    floor_size_selection.value=0;
    floor_size_selection.size=5;
    floor_size_selection.caption[0]=strdup("Wide");
    floor_size_selection.caption[1]=strdup("Normal");
    floor_size_selection.caption[2]=strdup("Shorter");
    floor_size_selection.caption[3]=strdup("Shortest");
    floor_size_selection.caption[4]=strdup("Tiny");
    floor_size_selection.value=2;
    gravity_selection.value=0;
    gravity_selection.size=3;
    gravity_selection.caption[0]=strdup("Helium");
    gravity_selection.caption[1]=strdup("Normal");
    gravity_selection.caption[2]=strdup("Heavy");
    fldads_start();
    if (argc>2) {
        for (i=1;i<argc;i++) {
            if (argv[i][0]!='-')
                replay_path=argv[i];
            if (!stricmp(argv[i],"-check")) check=1;
            else if (!stricmp(argv[i],"-jumps")) cmdline.jumps=1;
            else if (!stricmp(argv[i],"-combos")) cmdline.combos=1;
            else if (!stricmp(argv[i],"-sd")) cmdline.sd=1;
            else if (!stricmp(argv[i],"-keys")) cmdline.keys=1;
            else if (!stricmp(argv[i],"-all")) {
                cmdline.jumps=1;
                cmdline.combos=1;
                cmdline.sd=1;
                cmdline.keys=1;
            }
            else if (!stricmp(argv[i],"-tiny")) cmdline.tiny=1;
        }
        if (!check) {
            set_gfx_mode(GFX_TEXT,0,0,0,0);
            allegro_message("<%s>\nis not a vaild option.",argv[1]);
            log2file("*** Erroneous option (%s)",argv[1]);
            dropped_file_is_not_a_replay=1;
            return 0;
        }
        log2file("Loading %s",replay_path);
        demo=load_replay(replay_path);
        if (!demo) {
            set_gfx_mode(GFX_TEXT,0,0,0,0);
            printf("<itrcheck_results status=\"error\">%s</itrcheck_results>\n",
                   get_filename(replay_path));
            log2file("*** Failed!");
            dropped_file_is_not_a_replay=1;
            return 0;
        }
        itrcheck=1;
        log2file("ITRCHECK activated, checking <%s>",replay_path);
    } else if (argc==2) {
        log2file("Loading %s",argv[1]);
        demo=load_replay(argv[1]);
        if (!demo) {
            strcpy(tmpHandle,get_filename(argv[1]));
            get_extension(tmpHandle)[-1]=0;
            profile=load_profile(tmpHandle);
            if (!profile) {
                tmpHandle[0]=0;
                set_gfx_mode(GFX_TEXT,0,0,0,0);
                allegro_message("The file\n<%s>\nis not a vaild Icy Tower profile.",
                               get_filename(argv[1]));
                log2file("*** Failed!");
                dropped_file_is_not_a_replay=1;
                return 0;
            }
            free(profile);
            profile=NULL;
        }
    }
    get_configfile_path(cfgfilename,sizeof(cfgfilename));
    log2file("Creating hiscore tables.");
    for (i=0;i<15;i++) {
        hisc_tables[i]=make_hisc_table(hisc_names[i]);
        if (!hisc_tables[i]) {
            log2file("*** failed.");
            set_gfx_mode(GFX_TEXT,0,0,0,0);
            allegro_message("Failed reserve memory for highscore table.");
            return 0;
        }
        reset_hisc_table(hisc_tables[i],"Harold",1000,0);
    }
    log2file("Initiating controls");
    init_control(&ctrl);
    log2file("Loading config file");
    cfg=pack_fopen(cfgfilename,"rp");
    if (cfg) {
        load_options(&options,cfg);
        for (i=0;i<15;i++)
            if (!load_hisc_table(hisc_tables[i],cfg))
                reset_hisc_table(hisc_tables[i],"Harold",1000,0);
        pack_fclose(cfg);
    } else
    {
        log2file("*** failed.");
        log2file("Resetting to default config");
        reset_options(&options);
    }
    if (tmpHandle[0]) {
        log2file("Setting last profile");
        strcpy(options.lastProfile,tmpHandle);
    }
    if (!itrcheck) {
        options.timesStarted++;
        log2file("Game started %d times",options.timesStarted);
    }

    allegro_init();
    set_color_depth(32);
    if (options.full_screen) {
        log2file("Setting fullscreen mode 640x480");
        if (set_gfx_mode(GFX_AUTODETECT_FULLSCREEN,640,480,0,0)!=0) {
            log2file("*** failed.");
            set_gfx_mode(GFX_TEXT,0,0,0,0);
            allegro_message("Failed to set graphics mode.");
            return 0;
        }
        window=0;
    } else {
        log2file("Setting windowed mode 640x480");
        if (set_gfx_mode(GFX_AUTODETECT_WINDOWED,640,480,0,0)!=0) {
            log2file("*** failed.");
            options.full_screen=-1;
            if (set_gfx_mode(GFX_AUTODETECT_FULLSCREEN,640,480,0,0)!=0) {
                log2file("*** failed.");
                set_gfx_mode(GFX_TEXT,0,0,0,0);
                allegro_message("Failed to set graphics mode.");
                return 0;
            }
        } else
            window=1;
    }
    if (!screen) {
        log2file("ERROR: screen was not set");
        set_gfx_mode(GFX_TEXT,0,0,0,0);
        allegro_message("For some reason, the game failed to go into\ngraphics mode. Try starting the game again.\n\nIf this problem persists,\nplease visit www.freelunchdesign.com.");
        return 0;
    }
    log2file("Graphics mode set. (screen = %d)",screen);
    install_mouse();
    enable_hardware_cursor();
    select_mouse_cursor(2);
    if (!options.full_screen)
        show_mouse(screen);

    textprintf_centre_ex(screen,font,320,220,makecol(180,180,180),-1,
                         "please wait");
    set_color_conversion(COLORCONV_NONE);
    packfile_password("(c) Free Lunch Design");
    loader=load_datafile("data/loading.dat");
    log2file("Loading loader.");
    if (!loader) {
        set_gfx_mode(GFX_TEXT,0,0,0,0);
        allegro_message("Failed to load loader datafile.");
        return 0;
    }
    packfile_password(NULL);
    log2file("Putting FLD Logo on screen");
    fldLogo=loader[1].dat;
    select_palette(loader[0].dat);
    whiteColor=makecol(255,255,255);
    clear_to_color(screen,whiteColor);
    draw_sprite(screen,fldLogo,320-fldLogo->w/2,200-fldLogo->h/2);
    unload_datafile(loader);

    log2file("Setting focus modes");
    set_display_switch_mode(options.full_screen ? SWITCH_BACKAMNESIA :
                            SWITCH_BACKGROUND);
    log2file("Setting focus callbacks");
    set_display_switch_callback(SWITCH_IN,switchedToProgram);
    set_display_switch_callback(SWITCH_OUT,switchedFromProgram);
    set_close_button_callback(clickedCloseButton);
    srand((unsigned int)time(NULL));
    log2file("Installing timers");
    draw_progress_bar();
    install_timers();
    cycle_count=0;
    log2file("Installing keyboard");
    draw_progress_bar();
    install_keyboard();
    log2file("Installing sound");
    draw_progress_bar();
    install_sound(DIGI_AUTODETECT,MIDI_AUTODETECT,NULL);
    log2file("Installing joystick/gamepad");
    draw_progress_bar();
    got_joystick=(install_joystick(JOY_TYPE_AUTODETECT)==0);
    if (got_joystick) {
        ctrl.use_joy=1;
        log2file(" gamepad has %d buttons",joy[0].num_buttons);
        if (exists("gamepad.txt")) {
            log2file(" getting values from gamepad.txt");
            set_config_file("gamepad.txt");
            pad=get_gamepad();
            pad->up=get_gamepad_value("up");
            pad->left=get_gamepad_value("left");
            pad->right=get_gamepad_value("right");
            pad->down=get_gamepad_value("down");
            for (i=1;i<=32;i++) {
                sprintf(cfgfilename,"b%d",i);
                pad->b[i-1]=get_gamepad_value(cfgfilename);
            }
        } else {
            log2file(" gamepad.txt is missing, setting defaults");
            pad=get_gamepad();
            pad->up=4;
            pad->left=1;
            pad->right=2;
            pad->down=8;
            for (i=0;i<32;i++)
                pad->b[i]=16;
        }
    } else
        log2file(" no gamepad or joystick found, play with keyboard only");

    log2file("Reserving memory");
    draw_progress_bar();
    swap_screen=create_bitmap(SCREEN_W,SCREEN_H);
    if (!swap_screen) {
        log2file("*** failed.");
        set_gfx_mode(GFX_TEXT,0,0,0,0);
        allegro_message("Failed reserve memory screen buffers.");
        return 0;
    }

    set_color_conversion(0x00ffffff);
    draw_progress_bar();
    pwd_garble_string(init_string,50);
    log2file("Loading data");
    packfile_password(init_string);
    data=load_datafile_callback("data/data.dat",datafile_callback_slow);
    if (!data) {
        log2file("*** failed.");
        set_gfx_mode(GFX_TEXT,0,0,0,0);
        allegro_message("Failed to load datafile.");
        return 0;
    }
    packfile_password(NULL);
    draw_progress_bar();
    log2file("Initiating player");
    player_id=rand()%1000;
    ply[player_id]=malloc(sizeof(*ply[player_id]));
    if (!ply[player_id]) {
        log2file("*** failed.");
        set_gfx_mode(GFX_TEXT,0,0,0,0);
        allegro_message("Failed to allocate memory for player.");
        return 0;
    }
    if (!itrcheck) {
        ((RGB *)data[0].dat)[0].r=0;
        ((RGB *)data[0].dat)[0].g=0;
        ((RGB *)data[0].dat)[0].b=0;
        gameover_bmp=data[55].dat;
        log2file("Checking profile directory");
        get_profiles_dir(profiles_dir,sizeof(profiles_dir));
        if (!file_exists(profiles_dir,FA_DIREC,0)) {
            log2file("  does not exist, trying to create");
            mkdir(profiles_dir);
        }
        if (!file_exists(profiles_dir,FA_DIREC,0)) {
            log2file("  *** failed!");
            set_gfx_mode(GFX_TEXT,0,0,0,0);
            allegro_message("Failed to create profile directory %s",profiles_dir);
            return 0;
        }
        log2file("Checking available profiles");
        draw_progress_bar();
        rebuild_profile_list(0);
        log2file("Loading profile");
        draw_progress_bar();
        log2file(" loading '%s'",options.lastProfile);
        profile=load_profile(options.lastProfile);
        if (!profile) {
            log2file(" profile not found '%s'",options.lastProfile);
            log2file(" trying to load default profile '%s'","guest");
            profile=load_profile("guest");
            if (!profile) {
                profile=create_profile("guest",1);
                log2file(" created profile '%s'",profile->handle);
            }
        }
        if (!profile) {
            log2file("  *** failed!");
            set_gfx_mode(GFX_TEXT,0,0,0,0);
            allegro_message("Failed create profile.");
            return 0;
        }
        strcpy(options.lastProfile,profile->handle);
        syncOptionsFromProfile();
        log2file("Checking available characters");
        draw_progress_bar();
        if (!check_characters()) {
            log2file(" *** no characters available");
            set_gfx_mode(GFX_TEXT,0,0,0,0);
            allegro_message("No characters available.\nPlease reinstall game or add custom characters.\nRefer to readme.txt.");
            return 0;
        }
        select_palette(data[0].dat);
        log2file("Loading SFX");
        draw_progress_bar();
        packfile_password(init_string);
        log2file(" loading sounds");
        sfx=load_datafile_callback("data/sfx15.dat",datafile_callback);
        strcpy(sfx_file,"sfx15.dat");
        if (sfx)
            log2file(" sfx15.dat loaded");
        else {
            log2file(" could not load data/sfx15.dat");
            log2file("no sound");
        }
        packfile_password(NULL);
        if (sfx) {
            log2file("Getting sounds from data file");
            draw_progress_bar();
            combo_sound[0]=getSampleFromOggDatafile(sfx,8);
            combo_sound[1]=getSampleFromOggDatafile(sfx,18);
            combo_sound[2]=getSampleFromOggDatafile(sfx,9);
            combo_sound[3]=getSampleFromOggDatafile(sfx,17);
            combo_sound[4]=getSampleFromOggDatafile(sfx,21);
            combo_sound[5]=getSampleFromOggDatafile(sfx,1);
            combo_sound[6]=getSampleFromOggDatafile(sfx,5);
            combo_sound[7]=getSampleFromOggDatafile(sfx,6);
            combo_sound[8]=getSampleFromOggDatafile(sfx,15);
            combo_sound[9]=getSampleFromOggDatafile(sfx,20);
            bg_beat=getSampleFromOggDatafile(sfx,2);
            bg_menu=getSampleFromOggDatafile(sfx,3);
            speaker[0]=getSampleFromOggDatafile(sfx,10);
            speaker[1]=getSampleFromOggDatafile(sfx,7);
            speaker[2]=getSampleFromOggDatafile(sfx,19);
            menu_sounds[0]=getSampleFromOggDatafile(sfx,0);
            menu_sounds[1]=getSampleFromOggDatafile(sfx,13);
            sounds[2]=getSampleFromOggDatafile(sfx,0);
            sounds[4]=getSampleFromOggDatafile(sfx,13);
            sounds[6]=getSampleFromOggDatafile(sfx,14);
            sounds[7]=getSampleFromOggDatafile(sfx,4);
            sounds[8]=getSampleFromOggDatafile(sfx,16);
            log2file("Releasing ogg datafile.");
            unload_datafile(sfx);
        } else
            log2file(" no sounds loaded");
        log2file("Setting menu values");
        snd_volume_slider.value=options.snd_volume;
        msc_volume_slider.value=options.msc_volume;
        eyecandy_selection.value=options.flash;
        gravity_selection.value=options.gravity;
        floor_size_selection.value=options.floor_size;
        scroll_speed_selection.value=options.start_speed;
        floors.max=profile->best_floor>999 ? 9 : profile->best_floor/100;
        floors.value=profile->start_floor;
        if (floors.value>floors.max)
            floors.value=floors.max;
    }
    log2file("Cleaning up");
    draw_progress_bar();
    log2file("Welcome to Icy Tower");
    draw_progress_bar();
    i=0;
    while (!keypressed() && cycle_count<=149) {
        if (!(cycle_count%10) && i!=cycle_count) {
            draw_progress_bar();
            i=cycle_count;
        }
        rest(2);
    }
    seed=rand()%2367;
    fadeOut(16);
    clear_bitmap(screen);
    vsync();
    clear_keybuf();
    init_ok=1;
    return -1;
}
