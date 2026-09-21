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
    } else {
        max_bg_id = (ply[player_id]->level >= 0x259) + 4; /* 2507: branchless in the
                                                             * historical binary (cmp/setge/
                                                             * movzbl/add $0x4), not a
                                                             * separate else-if/else pair */
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
        /* 2547: real loop, evidenced by the back-edge test `cmpl $0x1e0,-0x178(%ebp)` (cx)
         * at offset 1580 sitting AFTER the sign-text block (main.c:2562..2575) but tagged
         * to line 2547 -- a rotated for-loop whose test/increment sit at the bottom. `esi`
         * (the per-row Tfloor pointer) is decremented by sizeof(Tfloor)==0x18 each pass
         * (offset 1570 `sub $0x18,%esi`) in lockstep with cx += 0x10 (offset 1573), for
         * 0x1e0/0x10 == 30 rows. Field offsets (empty=0, start_tile=4, end_tile=8, level=12,
         * sign=16, tiles=20) match Tfloor exactly for BOTH the floor body below (2548..2560)
         * and the sign body carried into D2 (2562..2575): they are the SAME loop over the
         * SAME `room` pointer, so this loop opens here and its closing brace is in D2.c. */
        Tfloor *room = &map.room[31]; /* ? starting row; map.room[32], matches the historical sign scan bound */

        for (cx = 0; cx != 0x1e0; cx += 0x10) {      /* 2547 */
            if (!room->empty) {                       /* 2548 */
                int tile;
                int rowy = cx + (map.offset & 0xf) - 6; /* ? sign-preserving mod-16 term, 2552 */

                ls = fo + room->tiles * 3;   /* 2549 */
                if (ls > 0x2c) {
                    ls = 0x2c;
                }
                if (room->level > 0x1387) {  /* 2550 */
                    ls += 3;
                }

                tile = room->start_tile;     /* 2551 */

                /* left edge tile */
                cy = tile * 16 - 5;          /* 2552, stored at -0x174(%ebp) */
                x = cy;                      /* ? DWARF tracks a separate `x` over this same span; mirrored here */
                draw_sprite(bmp, data[ls].dat, x, rowy);

                /* middle tiles: 2553..2556 */
                for (tile++; tile < room->end_tile; tile++) {
                    cy = tile * 16;
                    x = cy;                  /* ? */
                    draw_sprite(bmp, data[ls + 1].dat, x, rowy);
                }

                /* right edge tile, 2558 */
                cy = tile * 16;
                x = cy;                      /* ? */
                draw_sprite(bmp, data[ls + 2].dat, x, rowy);

                if (debug && !key[KEY_F2]) {  /* 2560 */
                    textprintf_ex(bmp, font, 0x208, cx + (map.offset & 0xf), 15, -1, "%d",
                                  (room->level - 1) / 10);
                }
            }

            /* lines 2562..2575 continue this same per-row loop (sign text) in D2.c;
             * loop closes and `room` is decremented at the end of D2.c's chunk. */
    /* REGION D2: lines 2562..2651 (player sprite, combo text, rewards) */

    /* REGION D3: lines 2652..2768 (scroller, hurry bar, replay overlay, custom mode text) */

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
