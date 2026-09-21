/* Recovered from the full 0x40dc9c..0x40e10f control-flow range.  The
 * candidate retains the original state transitions and API boundary; its
 * instruction layout remains under recovery. */
int new_game(void)
{
    int i;
    Tplayer *p;

    log2file(" init new game");
    collision_type = 2;
    new_srand(rand() % 0x18ff8);
    rec_pos = 0;
    cmdline.jumps = 0;
    cmdline.combos = 0;
    cmdline.sd = 0;
    cmdline.keys = 0;
    cmdline.tiny = 0;
    last_stripe_y = 0;

    if (!itrcheck) {
        floors.max = profile->best_floor / 100;
        if (floors.max > 9)
            floors.max = 9;
        floors.value = floors.max;
        if (floors.value > profile->start_floor)
            floors.value = profile->start_floor;
    }

    jumpSequence.start = 0;
    jumpSequence.dist = 0;
    jumpSequence.num = 0;
    gdLastJumpDiff = 0;
    if (gameData)
        destroy_game_data(gameData);
    gameData = create_game_data();
    if (!gameData) {
        log2file("*** failed to allocate memory for gameData, prepare for crash");
        return 0;
    }
    gameData->replay = demo;

    if (demo) {
        log2file(" preparing to show replay");
        recording = 0;
        rejump = demo->rejump;
        rec_seed = demo->random_seed;
        if (is_custom_replay(demo))
            gdLastJumpDiff = 1;
    } else {
        log2file(" setting up for replay recording");
        recording = 1;
        if (demo)
            destroy_replay(demo);
        demo = create_replay(64000);
        if (!demo)
            return 0;
        strcpy(demo->name, profile->handle);
        if (itrcheck) {
            demo->floor_shrink = options.floor_shrink;
            demo->floor_size = options.floor_size;
            demo->start_speed = options.start_speed;
            demo->speed_increase = options.speed_increase;
            demo->gravity = options.gravity;
        } else {
            demo->floor_shrink = 1;
            demo->floor_size = 1;
            demo->start_speed = 5;
            demo->speed_increase = 1;
            demo->gravity = 1;
        }
        rejump = options.jump_hold;
        srand(time(0));
        rec_seed = rand();
        demo->random_seed = rec_seed;
    }

    scroll_count = 0;
    scroll_delay = 100;
    for (i = 0; i < 15; i++)
        new_personal_best[i] = 0;
    srand(rec_seed);
    log2file(" creating map layout");
    reset_map(&map);
    for (i = 0; i < 30; i++)
        add_floor(&map);
    p = ply[player_id];
    reset_player(p);
    p->x = 200.0;
    p->y = 431.0;
    p->status = 0;
    p->sx = 0.001;
    reward_time = 0;
    hurry_y = 480;
    if (itrcheck)
        return 1;

    reset_particles(stars);
    log2file(" loading custom character: %s", characters[curr_char].name);
    init_custom(&custom, characters[curr_char].name,
                characters[curr_char].uses_datafile);
    if (!load_frames(&custom))
        return 1;
    load_sounds(&custom);
    log2file(" cc done");
    if (got_joystick)
        ctrl.use_joy = 1;
    return 1;
}
