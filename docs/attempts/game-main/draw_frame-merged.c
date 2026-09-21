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

    for (ls = 31; ls >= 0; ls--) {          /* ? loop bound/index inherited from D1's setup over map.room[32]; not directly evidenced in this range */
        if (map.room[ls].sign) {
            int s;
            int sy;
            int sw;
            int c1;
            int c2;

            s = so + map.room[ls].tiles;
            if (s > 0x6e)
                s = 0x6e;
            if (map.room[ls].level > 0x1387)
                s++;
            sy = cx + (map.offset % 16) + 10;
            sw = ((BITMAP *)data[s].dat)->w;
            cy = map.room[ls].start_tile + (map.room[ls].end_tile - map.room[ls].start_tile) / 2;
            cy *= 16;
            draw_sprite(bmp, data[s].dat, cy, sy);
            c1 = makecol(255, 255, 255);
            c2 = makecol(55, 55, 55);
            cy += sw / 2;
            /* shadowed stripe-number text: four gray offsets then one white on top */
            textprintf_centre_ex(bmp, data[54].dat, cy + 1, sy + 7, c2, -1, "%d", map.room[ls].sign);
            textprintf_centre_ex(bmp, data[54].dat, cy + 2, sy + 6, c2, -1, "%d", map.room[ls].sign);
            textprintf_centre_ex(bmp, data[54].dat, cy,     sy + 6, c2, -1, "%d", map.room[ls].sign);
            textprintf_centre_ex(bmp, data[54].dat, cy + 1, sy + 5, c2, -1, "%d", map.room[ls].sign);
            textprintf_centre_ex(bmp, data[54].dat, cy + 1, sy + 6, c1, -1, "%d", map.room[ls].sign);
        }
        cx += 0x10;
    }

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

        if (p_im == 6) {                                  /* ? refine default frame by horizontal speed thresholds */
            if (ply[player_id]->sx > -0.02 && ply[player_id]->sx < 0.02) {
                if (ply[player_id]->sx > 0.01 || ply[player_id]->sx < -0.01)   /* ? */
                    p_im = 8;
            }
        }

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
