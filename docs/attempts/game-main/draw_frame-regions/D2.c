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
                sy = cx + (map.offset & 0xf) + 10;  /* 2565 */
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

    for (fo = 0; fo < 512; fo++) {          /* 2580: loop index reuses fo; not otherwise evidenced as the star-loop counter */
        if (stars[fo].intensity) {           /* 2581 */
            draw_sprite(swap_screen, data[stars[fo].color + 0x75].dat, fixtoi(stars[fo].x), fixtoi(stars[fo].y));  /* 2582 */
        }
    }

    /* 2589: no pre-set default here -- offset 1813's `je` on status==0 lands at offset 2256,
     * a point downstream of the elseif chain that never passes through any of the chain's own
     * `mov $0x6,%esi` instructions (1852 for status==3's false arm, 2556 for status==2's own
     * false arm). Each arm below carries its OWN literal-6 fallback instead of one shared
     * pre-set; on the status==0 edge p_im is left holding whatever it already had, which is
     * exactly the unprovable edge the 2594 range test below needs to survive folding. */
    if (ply[player_id]->status) {                       /* 2589 */
        if (ply[player_id]->status == 3) {                /* 2590 */
            if (ply[player_id]->sy > 3.0)              /* 2590: fucompp/fnstsw compare direction inferred, not asserted */
                p_im = 7;
            else
                p_im = 6;                                   /* offset 1852's own `mov $0x6,%esi` */
        }
        else if (ply[player_id]->status == 2) {           /* 2591 */
            if (ply[player_id]->sy > 3.0)               /* 2591 */
                p_im = 7;
            else
                p_im = 6;                                   /* offset 2556's own `mov $0x6,%esi` */
        }
        else if (ply[player_id]->status == 1) {            /* 2592 */
            if (ply[player_id]->sy < -3.0)               /* 2592 */
                p_im = 5;
            else
                p_im = 6;
        }
    }
    /* 2594: reached even when status==0 skipped the whole chain above, leaving p_im
     * unassigned on that edge -- the compiler cannot fold this test away. */
    if ((unsigned)(p_im - 5) <= 2) {          /* 2594: range test on p_im, not p_im==6 */
        if (ply[player_id]->sx != 0.0) {      /* 2594: fucom vs 0.0 */
            if (ply[player_id]->sx > -0.02 && ply[player_id]->sx < 0.02) {   /* 2594: outer +-0.02 band */
                if (ply[player_id]->sx >= -0.01 && ply[player_id]->sx <= 0.01) {  /* 2595: inner +-0.01 band */
                    p_im = 8;                                                       /* 2595 */
                }
            }
        }
    }

    if (ply[player_id]->sx > 0.2 || ply[player_id]->sx < -0.2)  /* 2597 */
        ply[player_id]->frame = 0;

    if (ply[player_id]->frame > 3)                              /* 2599 */
        ply[player_id]->frame = 0;

    /* 2605: no comparison instructions precede either historical load of custom.frame[0]
     * (offsets 2315 and 2615 are both bare `mov`s) -- the earlier `if (custom.frame[0] == 0)
     * p_im = 1;` guess had no instruction support and is dropped. */
    /* 2606: `oy` seeded unconditionally from custom.frame[0]'s height; the historical 108 bytes
     * here against today's ~13 come from this same `1 - custom.frame[0]->h` load being
     * duplicated by the compiler at each of its several predecessors (offsets 1924, 2321/2621,
     * 3391, 6051), not from extra source logic this region is missing. */
    oy = 1 - custom.frame[0]->h;                                     /* 2606 */

    flip = 0;                                            /* 2609: p_im==0 skips the edge/flip block entirely --
                                                            * offset 2631's `test %esi,%esi; je` jumps straight to
                                                            * offset 2649 (the shared final draw below), so the
                                                            * edge handling AND the `ply->rotate` read only happen
                                                            * when p_im is one of the 5/6/7/8 poses. */
    if (p_im) {                                          /* 2609 */
    if (ply[player_id]->edge) {                          /* 2611: offset 2341..2346, edge==0 skips straight to offset 3115 (the customFrame block below) */
        customFrame = (logic_count & 8) ? custom.frame[13] : custom.frame[14];   /* 2612/2615 */

        if (ply[player_id]->edge == 2) {                  /* 2617: offset 2374..2383 */
            oy = (int)ply[player_id]->y + oy;               /* 2624 */
            ox = (int)ply[player_id]->x - customFrame->w + 0xb;   /* 2624: subtracts the *full* w, not w/2 */
            draw_sprite_h_flip(bmp, customFrame, ox, oy);          /* draw.inl:280, offset 3451..3560; edge==2 jumps past the block below entirely */
        }
        else {
            oy = (int)ply[player_id]->y + oy;               /* 2624 */
            ox = (int)ply[player_id]->x - 0xb;               /* 2624: no customFrame->w term on this side */
            draw_sprite(bmp, customFrame, ox, oy);            /* draw.inl:238 */

            /* 2629..2638: a second, overlay draw -- edge==0 reaches this same block
             * directly (2611's `je` target is offset 3115, this block's own start),
             * so it is duplicated verbatim below for the no-edge case. */
            if (map.offset > 0xc8 && ply[player_id]->y > 400.0) {   /* 2629: offset 3115..3134 (map.offset), 3416..3433 (y vs 400.0) */
                customFrame = custom.frame[11];                      /* 2629 */
            }
            else {
                if (logic_count <= 0xb)                              /* 2630 */
                    customFrame = custom.frame[9];
                else if (logic_count > 0x18 && logic_count <= 0x24)  /* 2631/2632 */
                    customFrame = custom.frame[10];
            }
            ox = -(customFrame->w / 2);                              /* 2636 */
            if (ply[player_id]->sx == 0.0) {                          /* 2638: fldl 0x10(%esi)/fldz/fucompp guards the draw */
                oy = (int)ply[player_id]->y + oy;
                ox = (int)ply[player_id]->x + ox;
                draw_sprite(bmp, customFrame, ox, oy);                /* draw.inl:238, offset 3285..3323 */
            }
        }
    }
    else {
        /* 2629..2638 duplicated for edge==0: 2611's `je` on edge==0 lands directly
         * at offset 3115, the start of this same customFrame/w2/sx-truncate/draw block. */
        if (map.offset > 0xc8 && ply[player_id]->y > 400.0) {   /* 2629 */
            customFrame = custom.frame[11];
        }
        else {
            if (logic_count <= 0xb)                              /* 2630 */
                customFrame = custom.frame[9];
            else if (logic_count > 0x18 && logic_count <= 0x24)  /* 2631/2632 */
                customFrame = custom.frame[10];
        }
        ox = -(customFrame->w / 2);                              /* 2636 */
        if (ply[player_id]->sx == 0.0) {                          /* 2638 */
            oy = (int)ply[player_id]->y + oy;
            ox = (int)ply[player_id]->x + ox;
            draw_sprite(bmp, customFrame, ox, oy);
        }
    }

    flip = ply[player_id]->rotate;                       /* 2643: test of 0x50(%edx), offset 2652..2657 */
    }

    if (flip) {
        customFrame = custom.frame[12];                 /* 2644: bypasses the p_im+frame index entirely */
        rotate_sprite(bmp, customFrame, (int)ply[player_id]->x, (int)ply[player_id]->y,
                       ply[player_id]->angle);            /* draw.inl:345, offset 6639..6852;
                                                             x/y args not fully traced -- the 200-byte
                                                             inline body wasn't walked past its w/h loads */
    }
    else {
        customFrame = custom.frame[p_im + ply[player_id]->frame];   /* 2649/2650: offset 2663 `add 0x3c(%edx),%esi`
                                                            * adds ply->frame onto the still-live p_im (esi,
                                                            * location-list range 2561..2666 covers this add),
                                                            * then offset 2666 indexes custom.frame[] with it --
                                                            * p_im is not dead, it is the pose base index itself,
                                                            * so the 2594 range test that keeps it in [5,8] guards
                                                            * a real array bound, not a provably-redundant compare */
        ox = -(customFrame->w / 2);
        /* 2651: fldl 0x10(%edx)/fldz/fucompp guards the draw, then the fistpl-truncated y and x
         * are added onto the running oy/ox and the draw call issued -- offsets 2686..2786, all one
         * historical source line per function_lines --source-view. */
        if (ply[player_id]->sx == 0) {                  /* 2651 */
            oy = (int)ply[player_id]->y + oy;            /* 2651 */
            ox = (int)ply[player_id]->x + ox;            /* 2651 */
            draw_sprite(bmp, customFrame, ox, oy);       /* 2651, draw.inl:238 */
        }
        /* ? ply[player_id]->sx != 0.0 (jne to offset 7917) leaves this region entirely --
         * not reconstructed here, out of scope for D2 (historical lines end at 2651). */
    }

    /* REGION D3: lines 2652..2768 (scroller, hurry bar, replay overlay, custom mode text) */

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
