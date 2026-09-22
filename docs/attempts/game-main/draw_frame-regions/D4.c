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

        vcr = data[127].dat;                            /* 2773 */
        myPos = rec_pos;                                /* 2774 */
        len = demo->size;                               /* 2774 */
        ox = 0x27b - vcr->w;                             /* 2776 */
        y = 0x1db - vcr->h; /* 2777: DWARF: `y`'s slot (reg edi) is live 4279..4341, exactly this
                              * assignment through the dead-check below; the D1-owned `x`
                              * local is NOT live over the matching esi computation here
                              * (its ranges stop at 2234), so that esi temp stays `ox`. */
        draw_sprite(bmp, vcr, ox, y); /* offsets 4282..4315, draw.inl:238 -- the only main.c:2778
                                        * candidate in this range; args are the ox/y just set. */
        if (!ply[player_id]->dead) {                     /* 2779 */
            /* `y` stays live (edi) through 7594..7837 for these three: is_left/is_fire/is_right
             * each build `y + 5` directly in a register (ecx) while the x-argument is spilled
             * through the `cx` stack slot (-0x178) only as a call-argument temporary. */
            if (is_left(&ctrl))                          /* 2780 */
                draw_sprite(bmp, data[128].dat, ox + 0x61, y + 5);
            if (is_fire(&ctrl))                           /* 2781 */
                draw_sprite(bmp, data[130].dat, ox + 0x6b, y + 5);
            if (is_right(&ctrl))                          /* 2782 */
                draw_sprite(bmp, data[129].dat, ox + 0x75, y + 5);
        }
        /* Stack-slot evidence (DW_OP_breg5): cx = -0x178(ebp), cy = -0x174(ebp).
         * offset 4338 "add $0xa,%edi; mov %edi,-0x178(%ebp)" stores y+0xa into cx (edi holds y).
         * offset 4347 "lea 0xa(%esi),%edi; mov %edi,-0x174(%ebp)" stores ox+0xa into cy (esi holds ox),
         * and that same edi is the set_clip_rect x1 argument, i.e. cy, not cx. */
        cx = y + 0xa;                                     /* 2784 */
        cy = ox + 0xa;                                     /* 2785 */
        set_clip_rect(bmp, cy, 0, 0x26f, 0x1df);            /* 2785 */
        if (!demo->comment[0])                              /* 2787 */
            sprintf(scrollerText, "%s%s%s", "", " - ", demo->name);
        else
            sprintf(scrollerText, "%s%s%s", demo->comment, " - ", demo->name);
        /* offset 4479 "mov -0x178(%ebp),%edi; add $0x4,%edi" reloads cx (not cy) for the
         * y-coordinate of every textout_ex below; the x-coordinate keeps using ox. */
        textout_ex(bmp, data[53].dat, demo->name, ox + 0xc - scroll_count / 2,     /* 2788 */
            cx + 4, makecol(150, 150, 160), -1);
        textout_ex(bmp, data[53].dat, demo->name, ox + 0xd - scroll_count / 2,     /* 2789 */
            cx + 4, makecol(200, 200, 210), -1);
        if (demo->comment[0]) {                                                    /* 2790 */
            textout_ex(bmp, data[53].dat, " - ",                                    /* 2791 */
                ox + 0xc - scroll_count / 2 + text_length(data[53].dat, demo->name),
                cx + 4, makecol(200, 200, 210), -1);
            textout_ex(bmp, data[53].dat, demo->comment,                            /* 2792 */
                ox - scroll_count / 2 + 0x1e + text_length(data[53].dat, demo->name),
                cx + 4, makecol(200, 200, 210), -1);
        }
        set_clip_rect(bmp, 0, 0, 0x27f, 0x1df);              /* 2794 */
        if (demo->comment[0]) {                               /* 2796 */
            if (scroll_delay > 0) {                            /* 2797 */
                scroll_delay--;                                 /* 2798 */
            }
            else {
                scroll_count++;                                 /* 2801 */
                if (scroll_count / 2 > text_length(data[53].dat, scrollerText))  /* 2802 */
                    scroll_count = -250;                          /* 2803 */
            }
        }
        /* rectfill is inlined (draw.inl:112, offsets 4801..4895) with no visible mnemonics
         * through the available tools, so its argument order is inferred, not disassembled:
         * cx is the value carrying the y+0xa quantity throughout this scope (used as the
         * y-coordinate for every textout_ex above) and cy carries the ox+0xa quantity (used
         * as set_clip_rect's x1), so the bar rect keeps that same x=cy / y=cx pairing. (?) */
        rectfill(bmp, cy, cx + 0x1e,                                      /* 2808 */
            cy + (myPos * 117 / len > 0x74 ? 0x74 : myPos * 117 / len),
            cx + 0x1d, makecol(50, 200, 50));
    }

    if (debug && key[KEY_F2]) {                                          /* 2812 */
            textprintf_ex(bmp, font, 0, 0, 15, -1, "FPS:%6d / %d", fps, lps);  /* 2813 */
            textprintf_ex(bmp, font, 0, 0xa, 15, -1, "REC:%6d / %d", rec_pos,   /* 2814 */
                demo->size);
            textprintf_ex(bmp, font, 0, 0x14, 15, -1, "    %6d  (%d) ",          /* 2815 */
                demo->data[rec_pos].key_flags, demo->data[rec_pos].cycle_count);
            textprintf_ex(bmp, font, 0xc8, 0, 15, -1, "POS: %d, %d",              /* 2816 */
                (int)ply[player_id]->x, (int)ply[player_id]->y);
            textprintf_ex(bmp, font, 0xc8, 0xa, 15, -1, " dx: %1.2f",              /* 2817 */
                ply[player_id]->sx);
            textprintf_ex(bmp, font, 0xc8, 0x14, 15, -1, "rjp: %d",                 /* 2818 */
                options.jump_hold);
            textprintf_ex(bmp, font, 0x190, 0, 15, -1, "any: %6d %6d %6d",           /* 2819 */
                any11, any12, any13);
            textprintf_ex(bmp, font, 0x190, 0xa, 15, -1, "any: %6d %6d %6d",          /* 2820 */
                any21, any22, any23);
        }
    /* line 2822 tail: fragments at offsets 2246 ("mov $0x2,%edi") and 2556
     * ("mov $0x6,%esi") are also attributed to this line by the line table,
     * but they sit far outside this region's byte range and duplicate
     * register-constant setup that reads as spillover from an earlier
     * region's block layout; no call is associated with them, so nothing
     * is written here beyond the implicit function epilogue, which the
     * closing brace below inherits this annotation for. */
    /* 2822 */
}
