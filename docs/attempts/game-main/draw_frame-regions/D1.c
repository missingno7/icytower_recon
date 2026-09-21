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

    fo = profile->start_floor * 3 + 0x11;              /* 2498 */
    so = profile->start_floor + 0x65;                  /* 2499 */

    frame_count++;                                     /* 2501 */

    if (ply[player_id]->level <= 0xc8) {                /* 2505 */
        max_bg_id = 2;
    } else if (ply[player_id]->level <= 0x15e) {        /* 2506 */
        max_bg_id = 3;
    } else if (ply[player_id]->level >= 0x259) {        /* 2507 */
        max_bg_id = 5;
    } else {
        max_bg_id = 4;
    }

    {
        /* 2510: row = floor(map.offset / 256), rounding toward -inf for negative offsets
         * (the js/lea 0xff/sar sequence is the historical bias-then-shift idiom). */
        int row = (map.offset < 0) ? ((map.offset + 0xff) >> 8) : (map.offset >> 8);
        int i;

        if (row > last_stripe_y) {                      /* 2510 */
            last_stripe_y++;                             /* 2511 */

            bg_stripe_ids[4] = bg_stripe_ids[3];         /* 2514 */
            bg_stripe_ids[3] = bg_stripe_ids[2];
            bg_stripe_ids[2] = bg_stripe_ids[1];
            bg_stripe_ids[1] = bg_stripe_ids[0];

            if (new_rand() % 100 > 0x28) {               /* 2517 */
                bg_stripe_ids[0] = 0;                     /* 2523 */
            } else {
                bg_stripe_ids[0] = new_rand() % max_bg_id; /* 2521 */
                if (bg_stripe_ids[0] == bg_stripe_ids[1] || /* 2522 */
                    bg_stripe_ids[0] == bg_stripe_ids[2])
                    bg_stripe_ids[0] = 0;                  /* 2523 */
            }
        }

        for (i = 0; i != 4; i++) {                        /* 2529 */
            BITMAP *stripe = data[bg_stripe_ids[i + 1] + 1].dat; /* 2530 */
            blit(stripe, bmp, 0, 0, 0x25,
                 i * 0x80 + (map.offset % 0x100) / 2,
                 stripe->w, stripe->h);
        }
    }

    if (hurry_y + 0x63 <= 0x242 && options.flash != 2) {  /* 2541 */
        BITMAP *hspr = data[67].dat;   /* ? historical index 67 (0x4dd23c + 0x430) not named by
                                         * function_data_refs beyond the generic "data" table */
        draw_sprite(bmp, hspr, 320 - hspr->w / 2, hurry_y); /* 2542 */
    }

    {
        Tfloor *fl = &map.room[31];    /* 0x4f8e00: function_data_refs names this map.room[31] */

        if (!fl->empty) {              /* 2548 */
            int f = 0xffffffe0;        /* y-cursor base for the floor row; DWARF block-local `f` */
            int tile;
            int rowy;

            ls = fo + fl->tiles * 3;   /* 2549 */
            if (ls > 0x2c) {
                ls = 0x2c;
            }
            if (fl->level > 0x1387) {  /* 2550 */
                ls += 3;
            }

            tile = fl->start_tile;     /* 2551 */
            rowy = f + (map.offset & 0xf) - 6; /* ? sign-preserving mod-16 term, 2552 */

            /* left edge tile */
            draw_sprite(bmp, data[ls].dat, tile * 16 - 5, rowy); /* 2552 */

            /* middle tiles: 2553..2556 */
            for (tile++; tile < fl->end_tile; tile++) {
                draw_sprite(bmp, data[ls + 1].dat, tile * 16, rowy);
            }

            /* right edge tile, 2558 */
            draw_sprite(bmp, data[ls + 2].dat, tile * 16, rowy);

            if (debug && !key[KEY_F2]) {   /* 2560 */
                textprintf_ex(bmp, font, 0x208, f + (map.offset & 0xf), 15, -1, "%d",
                              (fl->level - 1) / 10);
            }
        }
    }

    /* REGION D2: lines 2562..2651 (player sprite, combo text, rewards) */

    /* REGION D3: lines 2652..2768 (scroller, hurry bar, replay overlay, custom mode text) */

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
