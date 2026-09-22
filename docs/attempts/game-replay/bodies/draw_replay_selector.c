void draw_replay_selector(BITMAP *bmp, Treplay *rep, Treplay_post *file_list,
                          int selection, int offset, int max_posts, int x, int y)
{
    int w = 310;
    int h = 305;
    int fh = text_height(font);
    int i;
    int fg = makecol(25, 25, 25);
    int mg = makecol(85, 85, 85);
    float view_percentage = max_posts ? (float)num_itr_files / max_posts : 1.0f;
    float view_offset = max_posts ? (float)offset / max_posts : 0.0f;
    char curr_filename[1024];
    char rbuf[129];
    int is_dir;
    int show_directory = 0;
    int selected_version = 0;
    int isCustom = 0;

    if (view_percentage > 1.0f)
        view_percentage = 1.0f;
    if (data && data[86].dat)
        stretch_sprite(bmp, data[86].dat, x - 15, y - 15, w + 30, h + 30);
    else
        rectfill(bmp, x - 15, y - 15, x + w + 15, y + h + 15, mg);

    set_trans_blender(0, 0, 0, 150);
    drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);
    rect(bmp, x + 5, y + 30, x + w - 5, y + 305, fg);
    rect(bmp, x + 7, y + 32, x + w - 7, y + 303, fg);
    solid_mode();

    textout_ex(bmp, data[51].dat, "SELECT REPLAY", x + 10, y - 12, -1, -1);  /* 490 */

    set_clip_rect(bmp, x + 6, 0, x + 290, bmp->h - 1);        /* 509 */
    for (i = offset; i < num_itr_files && i < offset + max_posts; i++) {  /* 510/514 */
        Treplay_post *post = &file_list[i];                    /* 516 */
        int row = y + 40 + (i - offset) * fh;

        if (post->parent)                                        /* 516 */
            strcpy(rbuf, ".. (parent directory)");                  /* 517 */
        else
            strcpy(rbuf, get_filename(post->full_path));             /* 519 */
        is_dir = post->directory;                                  /* 521 */
        if (i == selection)                                           /* 523 */
            textprintf_ex(bmp, font, x + 8, row, mg, -1, "> %c %s",      /* 534 */
                          is_dir ? '}' : '{', rbuf);
        else
            textprintf_ex(bmp, font, x + 8, row, is_dir ? mg : fg, -1,    /* 525 */
                          "  %c %s", is_dir ? '}' : '{', rbuf);
    }
    set_clip_rect(bmp, 0, 0, bmp->w - 1, bmp->h - 1);

    if (selection >= 0 && selection < num_itr_files)
        strcpy(curr_filename, get_filename(file_list[selection].full_path));
    else
        curr_filename[0] = 0;
    textprintf_ex(bmp, font, x + 12, y + 14, fg, -1, "REPLAY SELECTOR: %s",
                  curr_filename);

    if (num_itr_files > max_posts && max_posts > 0) {
        int bar_top = y + 40 + (int)(view_offset * 260.0f);
        int bar_height = (int)(view_percentage * 260.0f);
        rectfill(bmp, x + 190, bar_top, x + 196, bar_top + bar_height, fg);
    }

    if (rep) {
        isCustom = is_custom_replay(rep);
        if (selection >= 0 && selection < num_itr_files)
            selected_version = file_list[selection].version;
        set_clip_rect(bmp, x + 205, y + 35, x + w, y + 300);
        textout_ex(bmp, font, rep->name, x + 210, y + 44, fg, -1);
        textout_right_ex(bmp, font, rep->date, x + w - 8, y + 44, fg, -1);
        textprintf_ex(bmp, font, x + 210, y + 68, fg, -1, "Score: %d", rep->score);
        textprintf_right_ex(bmp, font, x + w - 8, y + 68, fg, -1,
                            "Floor: %d", rep->floor);
        textprintf_right_ex(bmp, font, x + w - 8, y + 68 + fh, fg, -1,
                            "Combo: %d", rep->combo);
        textprintf_ex(bmp, font, x + 210, y + 68 + fh * 2, fg, -1,
                      "Version: %d%s", selected_version, isCustom ? " custom" : "");
        textprintf_ex(bmp, font, x + 210, y + 68 + fh * 3, fg, -1,
                      "%s", rep->comment);
        set_clip_rect(bmp, 0, 0, bmp->w - 1, bmp->h - 1);
    } else if (show_directory) {
        textout_ex(bmp, font, "Select a folder or replay", x + 210, y + 50,
                   fg, -1);
    }

    textout_ex(bmp, font, "Enter: select   Del: delete   Esc: back",
               x + 12, y + h - fh, fg, -1);
}
