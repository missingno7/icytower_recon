/* Partial recovery of main.c, 0x408d08..0x409137.  The normal path is the
 * oracle's floor-segment intersection; its collision-debug line drawing is
 * intentionally left for the presentation recovery pass. */
void handle_player_collision_vector(int lastX, int lastY)
{
    int fy1;
    int fx1 = 0, fx2 = 0;
    int ilx, ily, irx, iry;
    int left, right;
    int plx1, ply1, plx2;
    int prx1, prx2;

    fy1 = -12345678;
    ply1 = (int)ply[player_id]->y;
    getFloorData(&map, ply1, &fy1, &fx1, &fx2);
    if (fy1 == -12345678) {
        getFloorData(&map, lastY, &fy1, &fx1, &fx2);
        if (fy1 == -12345678) {
            if (ply[player_id]->status == 2 || ply[player_id]->status == 0)
                ply[player_id]->status = 3;
            return;
        }
    }

    plx1 = (int)ply[player_id]->x - 11;
    ply1 = ply1 + 1;
    plx2 = lastX - 11;
    prx1 = (int)ply[player_id]->x + 11;
    prx2 = lastX + 11;
    if (debug) {
        if (key[KEY_F2]) {
            int col1 = makecol(255, 0, 0);
            int col2 = makecol(255, 255, 0);
            line(screen, fx1, fy1, fx2, fy1, col1);
            line(screen, plx1, ply1, plx2, lastY, col2);
            line(screen, prx1, ply1, prx2, lastY, col2);
        }
    }
    left = line_intersect(fx1, fy1, fx2, fy1,
        plx1, ply1, plx2, lastY, &ilx, &ily);
    right = line_intersect(fx1, fy1, fx2, fy1,
        prx1, ply1, prx2, lastY, &irx, &iry);
    if (!left && !right) {
        if (ply[player_id]->status == 2 || ply[player_id]->status == 0)
            ply[player_id]->status = 3;
        return;
    }
    ply[player_id]->edge = left == right ? 0 : (left ? 1 : 2);
    if (ply[player_id]->status != 2 && ply[player_id]->status != 3)
        return;
    if (left && right &&
        (ilx < -10000 || irx < -10000 || ilx > 10000 || irx > 10000))
        return;

    play_sound(combo_sound[0], 1, 1);
    ply[player_id]->status = 0;
    ply[player_id]->sy = 0;
    ply[player_id]->y = fy1 - 1;
    ply[player_id]->x = left ? ilx + 11 : irx - 11;
    ply[player_id]->rotate = 0;
}
