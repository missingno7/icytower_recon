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
    char buf[128];

    old_font = font;                                   /* 710 */
    font = data[54].dat;                                /* 711 */
    bgbmp = create_bitmap(640, 480);                    /* 720 */
    blit(screen, bgbmp, 0, 0, 0, 0, 640, 480);           /* 721 */
    clear_keybuf();                                     /* 723 */
    selectedProfile = 0;
    profileIndex = 0;
    offset = 0;
    page_size = 17;
    ctrl_wait = 1000;
    pageY = 500;
    targetY = 50;
    done = 0;

    while (!closeButtonClicked && !done) {              /* 724 */
        cycle_count = 0;                                 /* 725 */
        checkMenuFocus();                                /* 727 */
        poll_control(ctrl, 1);                            /* 730 */
        if (is_any(ctrl) && !ctrl_wait) {                /* 731 */
            if (is_down(ctrl))                            /* 732 */
                simulate_keypress(0x5500);
            else if (is_up(ctrl))                         /* 733 */
                simulate_keypress(0x5400);
            else if (is_fire(ctrl))                       /* 734 */
                simulate_keypress(0x4300);
            ctrl_wait = 20;
        }
        if (ctrl_wait > 0)                                /* 737 */
            ctrl_wait--;                                  /* 738 */

        if (keypressed()) {                              /* 742 */
            kp = readkey() >> 8;                          /* 743 */
            /* switch, not if/else-if: the original dispatches with
             * `sub $0x3b,%eax; cmp $0x1a,%eax; ja default; jmp *table(,%eax,4)`,
             * a jump table over kp-59..kp-85. Byte-neutral in this build, but
             * this is the better-evidenced form -- keep it. */
            switch (kp) {                                 /* 744 */
            case 85:
                if (profileIndex < numProfiles - 1) {    /* 747 */
                    profileIndex++;                        /* 748 */
                    if (profileIndex >= offset + page_size) /* 749 */
                        offset++;
                    play_menu_move();                      /* 762 */
                } else {                                   /* 759 */
                    profileIndex = numProfiles - 1;        /* 760 */
                    offset = numProfiles - page_size;
                    if (offset < 0)                        /* 761 */
                        offset = 0;                        /* 762 */
                }
                break;
            case 84:
                if (profileIndex > 0) {
                    profileIndex--;
                    if (offset > profileIndex)
                        offset--;
                    play_menu_move();
                } else {
                    profileIndex = 0;
                    offset = 0;
                }
                break;
            case 83: {
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
                break;
            }
            case 67: {
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
                    textout_right_ex(swap_screen, data[54].dat,
                                      "...and press enter.", 480, 210, 0, -1);
                    rect(swap_screen, 139, 191, 480, 210,
                         makecol(255, 255, 255));
                    rectfill(swap_screen, 139, 191, 480, 210,
                             makecol(80, 80, 80));
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
                break;
            }
            case 59:
                play_menu_select();
                clear_keybuf();
                done = -1;
                break;
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

    if (selectedProfile) {
        sprintf(buf, "Now using profile '%s'", (char *)selectedProfile + 6);
        my_alert("Profile Changed!", buf, 0, 1);
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
