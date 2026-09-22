void blit_to_screen(BITMAP *bmp)
{
    if (debug) {
        if (key[56]) blit_mode = 0;                      /* 2271 */
        if (key[57]) blit_mode = 1;                       /* 2272 */
        if (key[58]) blit_mode = 2;                       /* 2273 */
        if (key[59]) blit_mode = 3;                       /* 2274 */
        if (key[60]) blit_mode = 4;                       /* 2275 */
        if (key[61]) blit_mode = 5;                       /* 2276 */
        if (key[62]) blit_mode = 6;                       /* 2277 */
    }
    acquire_screen();
    if (!blit_mode) {                                          /* 2282 */
        blit(bmp, screen, 0, 0, 0, 0, bmp->w, bmp->h);
    }
    else if (blit_mode == 1) {                                 /* 2285 */
        draw_sprite_h_flip(screen, bmp, 0, 0);                 /* 2286 */
    }
    else if (blit_mode == 2) {                                 /* 2288 */
        draw_sprite_v_flip(screen, bmp, 0, 0);                 /* 2289 */
    }
    else if (blit_mode == 3) {                                 /* 2291 */
        int y;
        for (y = 0; y < 480; y++) {                            /* 2293 */
            int x = fixtoi(fixsin(itofix(y + logic_count * 5)) *
                            ply[player_id]->level);              /* 2294 */
            blit(bmp, screen, 0, y, x, y, 640, 1);
        }
    }
    else if (blit_mode == 4) {                                 /* 2297 */
        int y = ply[player_id]->level % 480;                    /* 2298 */
        blit(bmp, screen, 0, 0, 0, y, bmp->w, bmp->h);           /* 2301 */
        blit(bmp, screen, 0, 0, 0, y - 480, bmp->w, bmp->h);     /* 2302 */
    }
    else if (blit_mode == 5) {                                 /* 2304 */
        int x = (int)(ply[player_id]->x - 160.0);                /* 2305 */
        int y = (int)(ply[player_id]->y - 160.0);                /* 2306 */
        if (x < 0) x = 0;
        else if (x > 320) x = 320;
        if (y < 0) y = 0;
        else if (y > 240) y = 240;
        stretch_blit(bmp, screen, x, y, 320, 240, 0, 0, 640, 480); /* 2307 */
    }
    else if (blit_mode == 6) {                                 /* 2309 */
        int x = (int)(ply[player_id]->x - 80.0);                 /* 2310 */
        int y = (int)(ply[player_id]->y - 80.0);                  /* 2311 */
        if (x < 0) x = 0;
        else if (x > 520) x = 520;
        if (y < 0) y = 0;
        else if (y > 360) y = 360;
        stretch_blit(bmp, screen, x, y, 160, 120, 0, 0, 640, 480); /* 2312 */
    }
    else {
        blit(bmp, screen, 0, 0, 0, 0, bmp->w, bmp->h);
    }
    release_screen();
}
