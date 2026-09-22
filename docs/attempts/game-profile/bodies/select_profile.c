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
    page_size = 16;
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
                char *name = profiles + profileIndex * 32;    /* 777 */
                /* 777 */
                if (stricmp(name, "guest") &&
                    stricmp(name, (char *)current_profile + 6)) {
                    sprintf(input, "Really delete '%s'?", name); /* 779 */
                    /* 780 */
                    if (my_alert(input, "WARNING: It will be gone forever.",
                                 1, 0)) {
                        delete_profile(name);                    /* 782 */
                        numProfiles = rebuild_profile_list(&profiles); /* 783 */
                        if (profileIndex >= numProfiles)
                            profileIndex = numProfiles - 1;
                        /* 766 */
                        offset = numProfiles - page_size;
                        if (offset < 0)
                            offset = 0;
                    }
                }
                break;
            }
            case 67: {
                char *name = profiles + profileIndex * 32;
                play_menu_select();                             /* 791 */
                if (!stricmp(name, "CREATE NEW PROFILE")) {      /* 792 */
                    set_trans_blender(0, 0, 0, 158);              /* 794 */
                    drawing_mode(5, 0, 0, 0);                      /* 795 */
                    /* 796 */
                    rectfill(swap_screen, 0, 0,
                             SCREEN_W,
                             SCREEN_H,
                             makecol(0, 0, 0));
                    solid_mode();                                  /* 797 */
                    input[0] = 0;                                  /* 800 */
                    draw_sprite(swap_screen, data[88].dat, 100, 140); /* 801 */
                    /* 802 */
                    textprintf_ex(swap_screen, data[51].dat, 140, 140,
                                  -1, -1, "Enter profile name:");
                    /* 803 */
                    textout_right_ex(swap_screen, data[54].dat,
                                      "...and press enter.", 480, 210, 0, -1);
                    /* 804 */
                    rect(swap_screen, 139, 191, 480, 210,
                         makecol(255, 255, 255));
                    /* 805 */
                    rectfill(swap_screen, 139, 191, 480, 210,
                             makecol(80, 80, 80));
                    /* 807 */
                    if (get_string(swap_screen, input, 340, 32, data[54].dat,
                                   140, 191, makecol(0, 0, 0), -1) >= 0 &&
                        input[0]) {
                        replaceBadCharacters(input, '_');               /* 809 */
                        selectedProfile = create_profile(input, 0);     /* 810 */
                        if (selectedProfile) {                          /* 811 */
                            my_alert("CREATE PROFILE", "Profile created!", 0, 1); /* 812 */
                            done = -1;
                        } else {
                            my_alert("CREATE PROFILE", "Failed to create profile.", 0, 1); /* 816 */
                        }
                    }
                } else {
                    selectedProfile = load_profile(name);              /* 823 */
                    if (selectedProfile)                                /* 824 */
                        done = -1;
                    else
                        /* 825 */
                        my_alert("SELECT PROFILE",
                                 "The profile you selected is broken.", 0, 1);
                }
                break;
            }
            case 59:
                play_menu_select();                             /* 772 */
                clear_keybuf();                                  /* 773 */
                done = -1;                                       /* 773 */
                break;
            }
        }

        blit(bgbmp, swap_screen, 0, 0, 0, 0, 640, 480);           /* 838 */
        set_trans_blender(0, 0, 0, (500 - pageY) / 3);              /* 840 */
        drawing_mode(5, 0, 0, 0);                                    /* 841 */
        /* 842 */
        rectfill(swap_screen, 0, 0, SCREEN_W,
                 SCREEN_H, makecol(0, 0, 0));
        solid_mode();                                                 /* 843 */
        /* 844 */
        draw_profile_selector(swap_screen, (char *)current_profile + 6,
                              profiles, numProfiles, profileIndex, offset,
                              page_size, 140, pageY);
        blit_to_screen(swap_screen);                                  /* 845 */
        while (!cycle_count)                                          /* 847 */
            rest(2);
        pageY += (int)((targetY - pageY) * 0.2f);                     /* 836 */
    }

    if (selectedProfile) {                                            /* 850 */
        sprintf(buf, "Now using profile '%s'", (char *)selectedProfile + 6); /* 852 */
        my_alert("Profile Changed!", buf, 0, 1);                       /* 853 */
    }

    targetY = 510;
    while (pageY <= 499) {                                             /* 858 */
        cycle_count = 0;                                                /* 859 */
        pageY += (int)((targetY - pageY) * 0.2f);                       /* 860 */
        blit(bgbmp, swap_screen, 0, 0, 0, 0, 640, 480);                 /* 863 */
        set_trans_blender(0, 0, 0, (500 - pageY) / 3);                  /* 865 */
        drawing_mode(5, 0, 0, 0);                                        /* 866 */
        /* 867 */
        rectfill(swap_screen, 0, 0, SCREEN_W,
                 SCREEN_H, makecol(0, 0, 0));
        solid_mode();                                                     /* 868 */
        /* 870 */
        draw_profile_selector(swap_screen, (char *)current_profile + 6,
                              profiles, numProfiles, profileIndex, offset,
                              page_size, 140, pageY);
        blit_to_screen(swap_screen);                                      /* 872 */
        while (!cycle_count)                                              /* 874 */
            rest(2);
    }
    destroy_bitmap(bgbmp);                                                 /* 878 */
    font = old_font;                                                       /* 880 */
    return selectedProfile;                                                /* 884 */
}
