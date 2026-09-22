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

    /* lines 2652..2697: no main.c line-table rows in this offset range (the
     * instructions here -- draw.inl:238/280 inline draw_sprite/draw_sprite_h_flip
     * calls plus reused fragments of main.c:2560/2590-2606/2629-2638 -- are the
     * last unrolled iteration of the scroller/background-layer loop whose source
     * text belongs to D1/D2's declared ranges, not D3's; nothing to add here. */

    /* lines 2698..2699: the scrolling side strips, reconstructed from offsets 2786..3105.
     * The loop base in %esi runs -124, 0, 124, 248, 372 and exits on `cmp $0x1f0` (496, line
     * 2698's `cmp`/`je` test, offsets 2970..2982) with a step of 0x7c (124); the second half's
     * tail jumps back to the first half's entry, so the two physically duplicated halves are one
     * loop body cross-jumped by -O2. Inside it, the `idiv $0x54` REMAINDER of map.offset is
     * multiplied by the double 1.476 at 0x4d6d18 and truncated, giving the scroll offset added to
     * the base (line 2699's own bytes: the divisor setup at 2824..2836 plus the idiv/float-mult/
     * data[100] lookup at 2982..3063 -- the mirror computation for the other half is credited by
     * the line table to the inlined draw.inl:280 body instead, an artifact of the cross-jump, not
     * a separate main.c statement). The sprite is data[100].dat and the two constant arguments in
     * the third slot (x) are 0x235 (565) and 0xffffffc7 (-57), so the strips are vertical, at the
     * right and left screen edges, sharing one y per iteration. Resolved by side-by-side reading
     * of offsets 2786..3110 (aligned_view sbs) against the ORIGINAL's own GFX_VTABLE layout, read
     * from its DWARF rather than guessed: 0x44 draw_sprite, 0x48 draw_256_sprite, 0x4c
     * draw_sprite_v_flip, 0x50 draw_sprite_h_flip, 0x54 draw_sprite_vh_flip. So the call reached
     * with x=0x235 uses 0x44 and 0x48, which is the depth check inside the plain draw_sprite
     * inline (draw.inl:238), and the call reached with x=0xffffffc7 uses 0x50, which is
     * draw_sprite_h_flip: the left strip is the right strip mirrored horizontally. An earlier
     * reading of this block was one vtable slot out and used the vertical flips. */
    for (cy = -124; cy != 496; cy += 124) {                                    /* 2698 */
        cx = cy + (int)((map.offset % 84) * 1.476);                             /* 2699 */
        draw_sprite(bmp, data[100].dat, 565, cx);                                /* 2699 */
        draw_sprite_h_flip(bmp, data[100].dat, -57, cx);                        /* 2699 */
    }

    draw_sprite(bmp, data[16].dat, 22, 100);          /* 2705 */
    /* Machine evidence (offsets 3640..3806 vs 5823..5968, --report comparison.json):
     * the in_combo branch's own tail (after its own blit+draw_sprite) jumps directly
     * into offset 3744, which is INSIDE the reward_time branch's argument setup for
     * textprintf_centre_ex, skipping reward_time's own test (3663) and its own
     * draw_sprite (3677) entirely. A live combo can therefore never also run the
     * reward_time body in the same frame, which is only reachable if the two `if`s
     * are one if/else-if chain, not two independent statements. */
    if (ply[player_id]->in_combo) {                    /* 2706 */
        blit(data[15].dat, bmp, 0, 100 - ply[player_id]->in_combo, 33,   /* 2707 */
             219 - ply[player_id]->in_combo, 16, ply[player_id]->in_combo);
        draw_sprite(bmp, data[14].dat, -8, 210);         /* 2708 */
        textprintf_centre_ex(bmp, data[50].dat, 42, 210, -1, -1, "%d",   /* 2709 */
                              ply[player_id]->acc_level);
    } else if (reward_time) {                            /* 2711 */
        draw_sprite(bmp, data[14].dat, -8, 210);           /* 2712 */
        textprintf_centre_ex(bmp, data[50].dat, 42, 210, -1, -1, "%d",     /* 2713 */
                              ply[player_id]->latest_combo);
    }

    if (hurry_y < 251 || hurry_y > 479) {                 /* 2717 */
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
    draw_sprite(bmp, data[12].dat, x, y);                  /* 2718 */

    if (hurry_y >= 201 && hurry_y <= 479) {                /* 2719 */
        cx = (logic_count + 2) % 3 - 1;
        cy = (logic_count + 3) % 3 - 1;
    }
    rotate_sprite(bmp, data[13].dat, cx + 34, cy + 28,      /* 2720 */
                  clock_angle ? ftofix((clock_angle % 1500) * 0.1706666) : 0);

    if (reward_time) {                                      /* 2721 */
        draw_reward(swap_screen);                            /* 2722 */
    }

    textprintf_ex(bmp, data[52].dat, 8, 440, -1, -1, "score: %d",   /* 2739 */
                  ply[player_id]->level * 10 + ply[player_id]->score);

    if (!recording) {                                        /* 2742 */
        char myBuf[256];

        if (frame_count & 8) {                                /* 2746 */
            strcpy(myBuf, "REPLAY");                            /* 2747 */
            ls = 630 - text_length(data[53].dat, myBuf);         /* 2748 */
            textprintf_ex(bmp, data[53].dat, ls + 1, 5, makecol(0, 0, 0), -1, "REPLAY");        /* 2749 */
            textprintf_ex(bmp, data[53].dat, ls, 4, makecol(255, 255, 255), -1, "REPLAY");       /* 2750 */
        }

        if (is_playing_custom_game) {                          /* 2754 */
            sprintf(myBuf, "%s Floors", floor_size_selection.caption[demo->floor_size]);  /* 2755 */
            cx = 630 - text_length(data[53].dat, myBuf);          /* 2756 */
            textout_ex(bmp, data[53].dat, myBuf, cx + 1, 16, makecol(0, 0, 0), -1);          /* 2757 */
            textout_ex(bmp, data[53].dat, myBuf, cx, 15, makecol(255, 255, 255), -1);         /* 2758 */

            sprintf(myBuf, "%s Speed", scroll_speed_selection.caption[demo->start_speed]);  /* 2760 */
            cx = 630 - text_length(data[53].dat, myBuf);           /* 2761 */
            textout_ex(bmp, data[53].dat, myBuf, cx + 1, 26, makecol(0, 0, 0), -1);           /* 2762 */
            textout_ex(bmp, data[53].dat, myBuf, cx, 25, makecol(255, 255, 255), -1);          /* 2763 */

            strcpy(myBuf, gravity_selection.caption[demo->gravity]);   /* 2765 */
            cx = 630 - text_length(data[53].dat, myBuf);              /* 2766 */
            textout_ex(bmp, data[53].dat, myBuf, cx + 1, 36, makecol(0, 0, 0), -1);            /* 2767 */
            textout_ex(bmp, data[53].dat, myBuf, cx, 35, makecol(255, 255, 255), -1);           /* 2768 */
        }
        /* DWARF lexical block 124048 (myBuf/myPos/vcr/len/scrollerText) has PC ranges
         * covering both this REPLAY/custom-game text (main.c:2742..2768) and D4's
         * scroller/controller-icon code (main.c up to ~2803, ending right before the
         * unconditional debug F2 overlay): they are one shared `if (!recording) { }`
         * block, not two separate blocks. This region intentionally leaves that
         * block open; D4 declares myPos/len/vcr/scrollerText as siblings of myBuf
         * and closes the brace itself. */

    /* REGION D4: lines 2773..2822 (clip rects, debug overlay, FPS/REC/POS readouts) */
}
