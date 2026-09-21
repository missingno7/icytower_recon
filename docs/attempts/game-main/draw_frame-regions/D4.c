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

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
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
