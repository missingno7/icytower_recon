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

        if ((unsigned)(p_im - 5) <= 2) {          /* 2594/2595: range test on p_im, not p_im==6 -- p_im is
                                                    * only ever 5/6/7 here so the compiler couldn't fold it away */
            if (ply[player_id]->sx != 0.0) {      /* 2594: fucom vs 0.0 */
                if (ply[player_id]->sx > -0.02 && ply[player_id]->sx < 0.02) {   /* 2594: outer +-0.02 band */
                    if (ply[player_id]->sx >= -0.01 && ply[player_id]->sx <= 0.01) {  /* 2595/2597: inner +-0.01 band */
                        p_im = 8;
                    }
                }
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

        /* 2606: `oy` seeded from custom.frame[0]'s height ahead of the edge branch --
         * every draw below (edge h-flip, edge plain, final pose) accumulates onto this
         * same `oy`, never a fresh -(h/2) of the frame actually drawn. */
        oy = 1 - custom.frame[0]->h;

        if (ply[player_id]->edge) {
            customFrame = (logic_count & 8) ? custom.frame[13] : custom.frame[14];

            oy = (int)ply[player_id]->y + oy;               /* 2624/2629 truncation pair, shared by both edge sub-cases */

            if (ply[player_id]->edge == 2) {
                ox = (int)ply[player_id]->x - customFrame->w + 0xb;   /* 3536/3538: subtracts the *full* w, not w/2 */
                draw_sprite_h_flip(bmp, customFrame, ox, oy);          /* draw.inl:280, offset 3451..3581 */
            }
            else {
                ox = (int)ply[player_id]->x - 0xb;          /* 2461: no customFrame->w term on this side */
                draw_sprite(bmp, customFrame, ox, oy);       /* draw.inl:238, offset 2383..2497 */

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

        flip = ply[player_id]->rotate;

        if (flip) {
            customFrame = custom.frame[12];                 /* 2644: bypasses the fo+frame index entirely */
            rotate_sprite(bmp, customFrame, (int)ply[player_id]->x, (int)ply[player_id]->y,
                           ply[player_id]->angle);            /* draw.inl:345, offset 6639..6852;
                                                                 x/y args not fully traced -- the 200-byte
                                                                 inline body wasn't walked past its w/h loads */
        }
        else {
            customFrame = custom.frame[fo + ply[player_id]->frame];
            ox = -(customFrame->w / 2);
            if (ply[player_id]->sx == 0) {                  /* 2686: fldl 0x10(%edx)/fldz/fucompp guards the draw */
                oy = (int)ply[player_id]->y + oy;            /* 2706..2755: fistpl-truncated y added onto the running oy */
                ox = (int)ply[player_id]->x + ox;            /* 2757..2783: fistpl-truncated x added onto ox */
                draw_sprite(bmp, customFrame, ox, oy);       /* draw.inl:238, offset 2786..2824 */
            }
            /* ? ply[player_id]->sx != 0.0 (jne to offset 7917) leaves this region entirely --
             * not reconstructed here, out of scope for D2 (historical lines end at 2651). */
        }
    }

    /* REGION D3: lines 2652..2768 (scroller, hurry bar, replay overlay, custom mode text) */

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
