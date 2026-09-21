/* Reconstruction of draw_frame() (historical main.c lines 2490..2822, 8518 bytes at 0x40929c).
 * Function-level locals from DWARF (13); regions are filled from the historical line table,
 * one coherent source region at a time. Retained evidence body for the TU_CONTEXT overlay;
 * production only through the strict gate. */
void draw_frame(BITMAP *bmp)
{
    int x;
    int y;
    int p_im;
    int flip;
    int cx;
    int cy;
    int ls;
    int fo;
    int so;
    int max_bg_id;
    BITMAP *customFrame;
    int oy;
    int ox;

    /* REGION D1: lines 2490..2560 (background layers, scrolling parallax, floor tiles) */

    /* REGION D2: lines 2562..2651 (player sprite, combo text, rewards) */

    /* REGION D3: lines 2652..2768 (scroller, hurry bar, replay overlay, custom mode text) */

    /* lines 2652..2697: no main.c line-table rows in this offset range (the
     * instructions here -- draw.inl:238/280 inline draw_sprite/draw_sprite_h_flip
     * calls plus reused fragments of main.c:2560/2590-2606/2629-2638 -- are the
     * last unrolled iteration of the scroller/background-layer loop whose source
     * text belongs to D1/D2's declared ranges, not D3's; nothing to add here. */

    /* lines 2698..2699: cmp/idiv fragments (offset 2970..3063) that sit between
     * the D1/D2 loop tail above and line 2705's code below; they could not be
     * isolated as standalone D3 statements from this evidence alone. (?) */

    draw_sprite(bmp, data[16].dat, 22, 100);
    if (ply[player_id]->in_combo) {
        blit(data[15].dat, bmp, 0, 100 - ply[player_id]->in_combo, 33,
             219 - ply[player_id]->in_combo, 16, ply[player_id]->in_combo);
        draw_sprite(bmp, data[14].dat, -8, 210);
        textprintf_centre_ex(bmp, data[50].dat, 42, 210, -1, -1, "%d",
                              ply[player_id]->acc_level);
    }

    if (reward_time) {
        draw_sprite(bmp, data[14].dat, -8, 210);
        textprintf_centre_ex(bmp, data[50].dat, 42, 210, -1, -1, "%d",
                              ply[player_id]->latest_combo);
    }

    if (hurry_y < 251 || hurry_y > 479) {
        x = 6;
        y = 10;
        cx = 0;
        cy = 0;
    } else {
        x = logic_count % 3 + 5;
        y = (logic_count + 1) % 3 + 8;
        cx = logic_count % 3 - 1;
        cy = (logic_count + 1) % 3 - 1;
    }
    draw_sprite(bmp, data[12].dat, x, y);

    if (hurry_y >= 201 && hurry_y <= 479) {
        cx = (logic_count + 2) % 3 - 1;
        cy = (logic_count + 3) % 3 - 1;
    }
    rotate_sprite(bmp, data[13].dat, cx + 34, cy + 28,
                  clock_angle ? ftofix((clock_angle % 1500) * 0.1706666) : 0);

    if (reward_time) {
        draw_reward(swap_screen);
    }

    textprintf_ex(bmp, data[52].dat, 8, 440, -1, -1, "score: %d",
                  ply[player_id]->level * 10 + ply[player_id]->score);

    if (!recording) {
        char myBuf[256];

        if (frame_count & 8) {
            strcpy(myBuf, "REPLAY");
            ls = 630 - text_length(data[53].dat, myBuf);
            textprintf_ex(bmp, data[53].dat, ls + 1, 5, makecol(0, 0, 0), -1, "REPLAY");
            textprintf_ex(bmp, data[53].dat, ls, 4, makecol(255, 255, 255), -1, "REPLAY");
        }

        if (is_playing_custom_game) {
            sprintf(myBuf, "%s Floors", floor_size_selection.caption[demo->floor_size]);
            cx = 630 - text_length(data[53].dat, myBuf);
            textout_ex(bmp, data[53].dat, myBuf, cx + 1, 16, makecol(0, 0, 0), -1);
            textout_ex(bmp, data[53].dat, myBuf, cx, 15, makecol(255, 255, 255), -1);

            sprintf(myBuf, "%s Speed", scroll_speed_selection.caption[demo->start_speed]);
            cx = 630 - text_length(data[53].dat, myBuf);
            textout_ex(bmp, data[53].dat, myBuf, cx + 1, 26, makecol(0, 0, 0), -1);
            textout_ex(bmp, data[53].dat, myBuf, cx, 25, makecol(255, 255, 255), -1);

            strcpy(myBuf, gravity_selection.caption[demo->gravity]);
            cx = 630 - text_length(data[53].dat, myBuf);
            textout_ex(bmp, data[53].dat, myBuf, cx + 1, 36, makecol(0, 0, 0), -1);
            textout_ex(bmp, data[53].dat, myBuf, cx, 35, makecol(255, 255, 255), -1);
        }
    }

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
