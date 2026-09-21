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

    /* REGION D3: lines 2652..2768 (scroller, hurry bar, replay overlay, custom mode text) */

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
