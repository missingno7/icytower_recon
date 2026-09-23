Tprofile_create *select_profile(Tprofile_create *current_profile, char *profiles,
                                int numProfiles, Tprofile_control *ctrl)
{
    Tprofile_create *selectedProfile;
    int kp;
    int done;
    void *old_font;
    int profileIndex;
    int offset;
    int page_size;
    int ctrl_wait;
    int pageY;
    int targetY;
    void *bgbmp;
    char input[256];

    old_font = font;
    font = data[54].dat;
    bgbmp = create_bitmap(640, 480);
    blit(screen, bgbmp, 0, 0, 0, 0, 640, 480);
    clear_keybuf();
    selectedProfile = 0;
    profileIndex = 0;
    offset = 0;
    page_size = 17;
    ctrl_wait = 1000;
    pageY = 500;
    targetY = 50;
    done = 0;

    while (!closeButtonClicked && !done) {
        cycle_count = 0;
        checkMenuFocus();
        poll_control(ctrl, 1);
        if (is_any(ctrl) && !ctrl_wait) {
            if (is_down(ctrl))
                simulate_keypress(0x5500);
            else if (is_up(ctrl))
                simulate_keypress(0x5400);
            else if (is_fire(ctrl))
                simulate_keypress(0x4300);
            ctrl_wait = 20;
        }
        if (ctrl_wait > 0)
            ctrl_wait--;

        if (keypressed()) {
            kp = readkey() >> 8;
            if (kp == 85) {
                if (profileIndex < numProfiles - 1) {
                    profileIndex++;
                    if (profileIndex >= offset + page_size)
                        offset++;
                    play_menu_move();
                } else {
                    profileIndex = numProfiles - 1;
                    offset = numProfiles - page_size;
                    if (offset < 0)
                        offset = 0;
                }
            } else if (kp == 84) {
                if (profileIndex > 0) {
                    profileIndex--;
                    if (offset > profileIndex)
                        offset--;
                    play_menu_move();
                } else {
                    profileIndex = 0;
                    offset = 0;
                }
            } else if (kp == 83) {
                char *name = profiles + profileIndex * 32;
                if (stricmp(name, "guest") &&
                    stricmp(name, (char *)current_profile + 6)) {
                    sprintf(input, "Really delete '%s'?", name);
                    if (my_alert(input, "WARNING: It will be gone forever.",
                                 1, 0)) {
                        delete_profile(name);
                        numProfiles = rebuild_profile_list(&profiles);
                        if (profileIndex >= numProfiles)
                            profileIndex = numProfiles - 1;
                    }
                }
            } else if (kp == 67) {
                char *name = profiles + profileIndex * 32;
                play_menu_select();
                if (!stricmp(name, "CREATE NEW PROFILE")) {
                    set_trans_blender(0, 0, 0, 158);
                    drawing_mode(5, 0, 0, 0);
                    rectfill(swap_screen, 0, 0,
                             SCREEN_W,
                             SCREEN_H,
                             makecol(0, 0, 0));
                    solid_mode();
                    input[0] = 0;
                    draw_sprite(swap_screen, data[88].dat, 100, 140);
                    textprintf_ex(swap_screen, data[51].dat, 140, 140,
                                  -1, -1, "Enter profile name:");
                    if (get_string(swap_screen, input, 340, 32, data[54].dat,
                                   140, 191, makecol(0, 0, 0), -1) >= 0 &&
                        input[0]) {
                        replaceBadCharacters(input, '_');
                        selectedProfile = create_profile(input, 0);
                        if (selectedProfile) {
                            my_alert("CREATE PROFILE", "Profile created!", 0, 1);
                            done = -1;
                        } else {
                            my_alert("CREATE PROFILE", "Failed to create profile.", 0, 1);
                        }
                    }
                } else {
                    selectedProfile = load_profile(name);
                    if (selectedProfile)
                        done = -1;
                    else
                        my_alert("SELECT PROFILE",
                                 "The profile you selected is broken.", 0, 1);
                }
            } else if (kp == 59) {
                play_menu_select();
                clear_keybuf();
                done = -1;
            }
        }

        blit(bgbmp, swap_screen, 0, 0, 0, 0, 640, 480);
        set_trans_blender(0, 0, 0, (500 - pageY) / 3);
        drawing_mode(5, 0, 0, 0);
        rectfill(swap_screen, 0, 0, SCREEN_W,
                 SCREEN_H, makecol(0, 0, 0));
        solid_mode();
        draw_profile_selector(swap_screen, (char *)current_profile + 6,
                              profiles, numProfiles, profileIndex, offset,
                              page_size, 16, pageY);
        blit_to_screen(swap_screen);
        while (!cycle_count)
            rest(2);
        pageY += (int)((targetY - pageY) * 0.2f);
    }

    targetY = 510;
    while (pageY <= 499) {
        cycle_count = 0;
        pageY += (int)((targetY - pageY) * 0.2f);
        blit(bgbmp, swap_screen, 0, 0, 0, 0, 640, 480);
        set_trans_blender(0, 0, 0, (500 - pageY) / 3);
        drawing_mode(5, 0, 0, 0);
        rectfill(swap_screen, 0, 0, SCREEN_W,
                 SCREEN_H, makecol(0, 0, 0));
        solid_mode();
        draw_profile_selector(swap_screen, (char *)current_profile + 6,
                              profiles, numProfiles, profileIndex, offset,
                              page_size, 16, pageY);
        blit_to_screen(swap_screen);
        while (!cycle_count)
            rest(2);
    }
    destroy_bitmap(bgbmp);
    font = old_font;
    return selectedProfile;
}