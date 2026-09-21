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
    /* still inside the D1 per-row loop for 2562..2575, then combo text / rewards for 2589..2651 */
            if (room->sign) {                  /* 2562, same `room` row as the floor draw above */
                int s;
                int sy;
                int sw;
                int c1;
                int c2;

                s = so + room->tiles;          /* 2563 */
                if (s > 0x6e) {
                    s = 0x6e;
                }
                if (room->level > 0x1387) {    /* 2564 */
                    s++;
                }
                sy = cx + (map.offset & 0xf) + 10;  /* ? sign-preserving mod-16 term like 2552's, 2565 */
                sw = ((BITMAP *)data[s].dat)->w;     /* 2566 */
                cy = room->start_tile + (room->end_tile - room->start_tile) / 2; /* 2567 */
                cy *= 16;
                draw_sprite(bmp, data[s].dat, cy, sy);
                c1 = makecol(255, 255, 255);   /* 2569 */
                c2 = makecol(55, 55, 55);      /* 2570 */
                cy += sw / 2;                  /* 2571 */
                /* shadowed stripe-number text: four gray offsets then one white on top */
                textprintf_centre_ex(bmp, data[54].dat, cy + 1, sy + 7, c2, -1, "%d", room->sign); /* 2571 */
                textprintf_centre_ex(bmp, data[54].dat, cy + 2, sy + 6, c2, -1, "%d", room->sign); /* 2572 */
                textprintf_centre_ex(bmp, data[54].dat, cy,     sy + 6, c2, -1, "%d", room->sign); /* 2573 */
                textprintf_centre_ex(bmp, data[54].dat, cy + 1, sy + 5, c2, -1, "%d", room->sign); /* 2574 */
                textprintf_centre_ex(bmp, data[54].dat, cy + 1, sy + 6, c1, -1, "%d", room->sign); /* 2575 */
            }

            room--;                            /* offset 1570 `sub $0x18,%esi`, sizeof(Tfloor) */
        }   /* closes the for (cx = 0; ...) loop opened in D1.c (2547) */
    }       /* closes the `{ Tfloor *room = ...; ... }` scope opened in D1.c */

    for (fo = 0; fo < 512; fo++) {          /* ? loop index reuses fo; not otherwise evidenced as the star-loop counter */
        if (stars[fo].intensity) {
            draw_sprite(swap_screen, data[stars[fo].color + 0x75].dat, fixtoi(stars[fo].x), fixtoi(stars[fo].y));
        }
    }

    if (ply[player_id]->status) {
        if (ply[player_id]->status == 3) {
            if (ply[player_id]->sy > 3.0)              /* ? fucompp/fnstsw compare direction inferred, not asserted */
                p_im = 7;
            else
                p_im = 6;
        }
        else if (ply[player_id]->status == 2) {
            if (ply[player_id]->sy > 3.0)               /* ? */
                p_im = 7;
            else
                p_im = 6;
        }
        else if (ply[player_id]->status == 1) {
            if (ply[player_id]->sy < -3.0)               /* ? */
                p_im = 5;
            else
                p_im = 6;
        }
        else {
            p_im = 6;
        }

        if (p_im == 6 && ply[player_id]->sx != 0.0) {     /* 2594: fucom vs 0.0 guards the narrow-band check */
            if (ply[player_id]->sx > -0.02 && ply[player_id]->sx < 0.02) {
                p_im = 8;
            }
        }
        /* 2595/2597: a further +-0.01 fucompp pair (separate literals from 2594's +-0.02)
         * follows in the historical code and can still change p_im here; not reconstructed --
         * this region's `esi` bookkeeping across 2589..2606 was not fully traced. */

        if (ply[player_id]->sx > 0.2 || ply[player_id]->sx < -0.2)
            ply[player_id]->frame = 0;

        if (ply[player_id]->frame > 3)
            ply[player_id]->frame = 0;

        fo = 0;                                             /* reuse fo as the custom.frame[] base index for this player's pose */
        if (custom.frame[0] == 0) {
            p_im = 1;                                       /* ? base-index selection below is only approximately reconstructed */
        }

        if (ply[player_id]->edge) {
            customFrame = (logic_count & 8) ? custom.frame[13] : custom.frame[14];
            if (ply[player_id]->edge == 2) {
                ply[player_id]->frame = 0;
            }
            else {
                ply[player_id]->frame = 0;
                if (customFrame) {                            /* 2624: was entirely missing; fldl+fistpl truncation
                                                                 * pair on ply->y (offset 8) and ply->x (offset 0),
                                                                 * folded into the screen-position accumulators ahead
                                                                 * of the fo selection below -- register flow into
                                                                 * and out of this block (ecx/edx) not fully traced */
                    ox = customFrame->w / 2 + (int)ply[player_id]->y;  /* ? */
                    oy = (int)ply[player_id]->x - 0xb;               /* ? */
                }
                if (map.offset > 0xc8) {                     /* ? */
                    if (logic_count <= 11)
                        fo = 9;
                    else if (logic_count <= 36)
                        fo = 10;
                }
                else {
                    fo = (ply[player_id]->y > 400.0) ? 11 : 9;   /* ? */
                }
            }
        }

        customFrame = custom.frame[fo + ply[player_id]->frame];

        flip = ply[player_id]->rotate;

        if (customFrame) {
            ox = -(customFrame->w / 2);
            oy = -(customFrame->h / 2);
            if (ply[player_id]->sx == 0) {                  /* ? fldl 0x10(%esi)/fldz/fucompp guards this whole adjustment */
                oy = (int)ply[player_id]->y + oy;            /* ? fistpl-truncated y folded into the centering offset */
                ox = (int)ply[player_id]->x + ox;            /* ? fistpl-truncated x folded into the centering offset */
            }
        }
    }


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
        /* DWARF lexical block 124048 (myBuf/myPos/vcr/len/scrollerText) has PC ranges
         * covering both this REPLAY/custom-game text (main.c:2742..2768) and D4's
         * scroller/controller-icon code (main.c up to ~2803, ending right before the
         * unconditional debug F2 overlay): they are one shared `if (!recording) { }`
         * block, not two separate blocks. This region intentionally leaves that
         * block open; D4 declares myPos/len/vcr/scrollerText as siblings of myBuf
         * and closes the brace itself. */

    /* Continues D3's `if (!recording) { ... }` block (DWARF lexical block 124048
     * covers myBuf through here, up to and including the rectfill() below, as one
     * shared block, not a nested one); the brace is closed just before the
     * unconditional debug F2 overlay. */
        int myPos;
        int len;
        BITMAP *vcr;
        char scrollerText[70];

        vcr = data[127].dat;
        myPos = rec_pos;
        len = demo->size;
        ox = 0x27b - vcr->w;
        oy = 0x1db - vcr->h;
        draw_sprite(bmp, vcr, ox, oy); /* ? line 2778: no main.c row in the line table for this call; it is fully absorbed by draw.inl:238 between the 2777 and 2779 rows */
        if (!ply[player_id]->dead) {
            if (is_left(&ctrl))
                draw_sprite(bmp, data[128].dat, ox + 0x61, oy + 5);
            if (is_fire(&ctrl))
                draw_sprite(bmp, data[130].dat, ox + 0x6b, oy + 5);
            if (is_right(&ctrl))
                draw_sprite(bmp, data[129].dat, ox + 0x75, oy + 5);
        }
        cy = oy + 0xa;
        cx = ox + 0xa;
        set_clip_rect(bmp, cx, 0, 0x26f, 0x1df);
        if (!demo->comment[0])
            sprintf(scrollerText, "%s%s%s", "", " - ", demo->name);
        else
            sprintf(scrollerText, "%s%s%s", demo->comment, " - ", demo->name);
        textout_ex(bmp, data[53].dat, demo->name, ox + 0xc - scroll_count / 2,
            cy + 4, makecol(150, 150, 160), -1);
        textout_ex(bmp, data[53].dat, demo->name, ox + 0xd - scroll_count / 2,
            cy + 4, makecol(200, 200, 210), -1);
        if (demo->comment[0]) {
            textout_ex(bmp, data[53].dat, " - ",
                ox + 0xc - scroll_count / 2 + text_length(data[53].dat, demo->name),
                cy + 4, makecol(200, 200, 210), -1);
            textout_ex(bmp, data[53].dat, demo->comment,
                ox - scroll_count / 2 + 0x1e + text_length(data[53].dat, demo->name),
                cy + 4, makecol(200, 200, 210), -1);
        }
        set_clip_rect(bmp, 0, 0, 0x27f, 0x1df);
        if (demo->comment[0]) {
            if (scroll_delay > 0) {
                scroll_delay--;
            }
            else {
                scroll_count++;
                if (scroll_count / 2 > text_length(data[53].dat, scrollerText))
                    scroll_count = -250;
            }
        }
        rectfill(bmp, cx, cy + 0x1e,
            cx + (myPos * 117 / len > 0x74 ? 0x74 : myPos * 117 / len),
            cy + 0x1d, makecol(50, 200, 50));
    }

    if (debug && key[KEY_F2]) {
            textprintf_ex(bmp, font, 0, 0, 15, -1, "FPS:%6d / %d", fps, lps);
            textprintf_ex(bmp, font, 0, 0xa, 15, -1, "REC:%6d / %d", rec_pos,
                demo->size);
            textprintf_ex(bmp, font, 0, 0x14, 15, -1, "    %6d  (%d) ",
                demo->data[rec_pos].key_flags, demo->data[rec_pos].cycle_count);
            textprintf_ex(bmp, font, 0xc8, 0, 15, -1, "POS: %d, %d",
                (int)ply[player_id]->x, (int)ply[player_id]->y);
            textprintf_ex(bmp, font, 0xc8, 0xa, 15, -1, " dx: %1.2f",
                ply[player_id]->sx);
            textprintf_ex(bmp, font, 0xc8, 0x14, 15, -1, "rjp: %d",
                options.jump_hold);
            textprintf_ex(bmp, font, 0x190, 0, 15, -1, "any: %6d %6d %6d",
                any11, any12, any13);
            textprintf_ex(bmp, font, 0x190, 0xa, 15, -1, "any: %6d %6d %6d",
                any21, any22, any23);
        }
    /* ? line 2822 tail: fragments at offsets 2246 ("mov $0x2,%edi") and 2556
     * ("mov $0x6,%esi") are also attributed to this line by the line table,
     * but they sit far outside this region's byte range and duplicate
     * register-constant setup that reads as spillover from an earlier
     * region's block layout; no call is associated with them, so nothing
     * is written here beyond the implicit function epilogue. */
}
