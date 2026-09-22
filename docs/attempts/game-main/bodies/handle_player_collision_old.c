/* Oracle: main.c, 0x407fd8..0x408358.  The legacy mode first tests the
 * current feet, then sweeps a midpoint when the player moved downward. */
void handle_player_collision_old(int lastX, int lastY)
{
    int dX, dY, midX, midY;
    int solid1, solid2;

    /* 3246 */
    dX = lastX - (int)ply[player_id]->x;
    if (dX < 0) dX = -dX;
    /* 3247 */
    dY = lastY - (int)ply[player_id]->y;
    if (dY < 0) dY = -dY;
    /* 3248 */
    if ((int)ply[player_id]->x < lastX) midX = lastX - dX / 2;
    /* 3249 */
    else midX = lastX + dX / 2;
    /* 3250 */
    if ((int)ply[player_id]->y < lastY) midY = lastY - dY / 2;
    /* 3251 */
    else midY = lastY + dY / 2;

    /* 3253 */
    solid1 = is_solid(&map, (int)ply[player_id]->x - 11, (int)ply[player_id]->y);
    /* 3254 */
    solid2 = is_solid(&map, (int)ply[player_id]->x + 11, (int)ply[player_id]->y);
    /* 3255 */
    any11 = solid1;
    /* 3256 */
    any12 = solid2;
    /* 3257 */
    any23 = 0;
    any22 = 0;
    any21 = 0;
    /* 3258 */
    if (solid1 + solid2 == 0) {
        /* 3259 */
        if (ply[player_id]->status == 2 || ply[player_id]->status == 0)
            ply[player_id]->status = 3;
        /* 3270 */
        if (midY <= lastY)
            return;
        goto sweep;
    }

resolve:
    /* 3260 */
    if (ply[player_id]->status == 1 || ply[player_id]->status == 2)
        return;
    /* 3261 */
    if (ply[player_id]->status)
        play_sound(combo_sound[0], 1, 1);
    /* 3262 */
    ply[player_id]->status = 0;
    /* 3263 */
    ply[player_id]->sy = 0;
    /* 3264 */
    if (solid1) {
        ply[player_id]->y -= solid1 - 9999;
        /* 3266 */
        ply[player_id]->rotate = 0;
        /* 3267 */
        if (solid1 == solid2)
            ply[player_id]->edge = 0;
        else
            ply[player_id]->edge = 1;
        return;
    }
    goto check2;

sweep:
    /* 3271 */
    solid1 = is_solid(&map, midX - 11, midY);
    /* 3272 */
    solid2 = is_solid(&map, midX + 11, midY);
    /* 3273 */
    any21 = solid1;
    /* 3274 */
    any22 = solid2;
    /* 3275 */
    if (solid1 + solid2 == 0) {
        /* 3276 */
        if (ply[player_id]->status == 2 || ply[player_id]->status == 0)
            ply[player_id]->status = 3;
        return;
    }
    /* 3277 */
    if (ply[player_id]->status == 1 || ply[player_id]->status == 2)
        return;
    /* 3278 */
    any23 = 1;
    /* 3279 */
    if (ply[player_id]->status)
        play_sound(combo_sound[0], 1, 1);
    /* 3280 */
    ply[player_id]->status = 0;
    /* 3281 */
    ply[player_id]->sy = 0;
    /* 3282 */
    if (solid1) {
        ply[player_id]->y -= solid1 - 9999;
        /* 3284 */
        ply[player_id]->rotate = 0;
        /* 3285 */
        if (solid1 == solid2)
            ply[player_id]->edge = 0;
        else
            ply[player_id]->edge = 1;
        return;
    }
check2:
    /* 3283 */
    if (solid2) {
        ply[player_id]->y -= solid2 - 9999;
        ply[player_id]->rotate = 0;
        ply[player_id]->edge = 2;
        return;
    }
    /* 3286 */
    ply[player_id]->rotate = 0;
    ply[player_id]->edge = 0;
    return;
}
