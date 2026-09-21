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

    /* REGION D3: lines 2652..2768 (scroller, hurry bar, replay overlay, custom mode text) */

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
