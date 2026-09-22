Treplay *replay_selector(Tcontrol *ctrl, char *path)
{
    FONT *old_font = font;
    BITMAP *bg = create_bitmap(SCREEN_W, SCREEN_H);
    Treplay *rep = NULL;
    int curr_file_id = 0;
    int done = 0;
    int ctrl_wait = 1000;
    int page_size;
    int offset = 0;
    int need_to_update = 1;
    int ok_to_rename = 0;
    int pageY = 500;
    int targetY = 0;
    char fname[512];

    if (!bg)
        return NULL;
    blit(screen, bg, 0, 0, 0, 0, SCREEN_W, SCREEN_H);
    if (data)
        font = data[54].dat;
    page_size = 270 / text_height(font);
    clear_keybuf();

    while (!done) {
        int kp = 0;

        if (need_to_update) {
            if (rep) {
                destroy_replay(rep);
                rep = NULL;
            }
            if (num_itr_files > 0 && curr_file_id >= 0 &&
                curr_file_id < num_itr_files && !itr_file_list[curr_file_id].directory)
                rep = load_replay(itr_file_list[curr_file_id].full_path);
            need_to_update = 0;
        }

        poll_control(ctrl, 1);
        if (is_any(ctrl) && ctrl_wait == 0) {
            if (is_down(ctrl))
                simulate_keypress(KEY_DOWN << 8);
            else if (is_up(ctrl))
                simulate_keypress(KEY_UP << 8);
            else if (is_fire(ctrl))
                simulate_keypress(KEY_ENTER << 8);
        }
        if (ctrl_wait > 0)
            ctrl_wait--;

        if (keypressed())
            kp = readkey() >> 8;
        if (kp) {
            ctrl_wait = 20;
            switch (kp) {
            case KEY_UP:
                if (curr_file_id > 0) {
                    curr_file_id--;
                    if (curr_file_id < offset)
                        offset--;
                    play_menu_move();
                    need_to_update = 1;
                }
                break;
            case KEY_DOWN:
                if (curr_file_id + 1 < num_itr_files) {
                    curr_file_id++;
                    if (curr_file_id >= offset + page_size)
                        offset++;
                    play_menu_move();
                    need_to_update = 1;
                }
                break;
            case KEY_ENTER:
                if (curr_file_id >= 0 && curr_file_id < num_itr_files) {
                    Treplay_post *post = &itr_file_list[curr_file_id];
                    if (post->directory) {
                        strcpy(path, post->full_path);
                        canonicalize_filename(fname, path, sizeof(fname));
                        strcpy(path, fname);
                        update_file_list(path);
                        curr_file_id = offset = 0;
                        need_to_update = 1;
                    } else if (rep) {
                        play_menu_select();
                        done = 1;
                    }
                }
                break;
            case KEY_DEL:
                if (curr_file_id >= 0 && curr_file_id < num_itr_files &&
                    !itr_file_list[curr_file_id].directory && rep &&
                    my_alert("Really delete replay?", "WARNING: It will be gone forever.",
                             1, 0)) {
                    delete_file(itr_file_list[curr_file_id].full_path);
                    need_to_update = 1;
                }
                break;
            case KEY_ESC:
                play_menu_select();
                destroy_replay(rep);
                rep = NULL;
                done = -1;
                break;
            case KEY_F1:
                set_sort_method(1);
                need_to_update = 1;
                break;
            case KEY_F2:
                set_sort_method(2);
                need_to_update = 1;
                break;
            case KEY_F3:
                set_sort_method(3);
                need_to_update = 1;
                break;
            case KEY_F4:
                set_sort_method(4);
                need_to_update = 1;
                break;
            case KEY_F5:
                install_mouse();
                file_select_ex("Select a new folder and press OK", path, "itr",
                               sizeof(fname), 400, 400);
                remove_mouse();
                replace_filename(fname, path, "", sizeof(fname));
                strcpy(path, fname);
                update_file_list(path);
                curr_file_id = offset = 0;
                need_to_update = 1;
                ok_to_rename = 1;
                break;
            default:
                break;
            }
        }

        if (need_to_update) {
            update_file_list(path);
            if (curr_file_id >= num_itr_files)
                curr_file_id = num_itr_files - 1;
            if (curr_file_id < 0)
                curr_file_id = 0;
            if (offset > curr_file_id)
                offset = curr_file_id;
        }

        if (pageY > targetY)
            pageY -= (pageY - targetY) / 3 + 1;
        blit(bg, screen, 0, 0, 0, 0, SCREEN_W, SCREEN_H);
        set_trans_blender(0, 0, 0, (500 - pageY) / 3);
        drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);
        rectfill(screen, 0, 0, SCREEN_W, SCREEN_H, makecol(0, 0, 0));
        solid_mode();
        draw_replay_selector(screen, rep, itr_file_list, curr_file_id, offset,
                             page_size, 120, pageY + 120);
        blit_to_screen(screen);
        checkMenuFocus();
        rest(2);
        (void)ok_to_rename;
    }

    destroy_bitmap(bg);
    font = old_font;
    for (curr_file_id = 0; curr_file_id < num_itr_files; curr_file_id++) {
        free(itr_file_list[curr_file_id].full_path);
        itr_file_list[curr_file_id].parent = 0;
        itr_file_list[curr_file_id].directory = 0;
    }
    num_itr_files = 0;
    return rep;
}
