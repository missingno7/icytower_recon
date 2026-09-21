/* Oracle: main.c, 0x407fd8..0x408358.  The legacy mode first tests the
 * current feet, then sweeps a midpoint when the player moved downward. */
void handle_player_collision_old(int lastX, int lastY)
{
    Tplayer *p;
    int x, y, dx, dy;
    int solid1, solid2;

    p = ply[player_id];
    x = (int)p->x;
    y = (int)p->y;
    dx = lastX - x;
    if (dx < 0) dx = -dx;
    dy = lastY - y;
    if (dy < 0) dy = -dy;
    if ((int)p->x < lastX) x = lastX - dx / 2;
    else x = lastX + dx / 2;
    if ((int)p->y < lastY) y = lastY - dy / 2;
    else y = lastY + dy / 2;

    solid1 = is_solid(&map, (int)p->x - 11, (int)p->y);
    solid2 = is_solid(&map, (int)p->x + 11, (int)p->y);
    any11 = solid1;
    any12 = solid2;
    any23 = 0;
    any22 = 0;
    any21 = 0;
    if (solid1 + solid2 == 0) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
        if (y <= lastY)
            return;
        goto sweep;
    }

resolve:
    if (p->status == 1 || p->status == 2)
        return;
    if (p->status)
        play_sound(combo_sound[0], 1, 1);
    p->status = 0;
    p->sy = 0;
    if (solid1) {
        p->y -= solid1 - 9999;
        p->rotate = 0;
        p->edge = solid1 == solid2 ? 0 : 1;
        return;
    }
    if (solid2) {
        p->y -= solid2 - 9999;
        p->rotate = 0;
        p->edge = 2;
        return;
    }
    p->rotate = 0;
    p->edge = 0;
    return;

sweep:
    solid1 = is_solid(&map, x - 11, y);
    solid2 = is_solid(&map, x + 11, y);
    any21 = solid1;
    any22 = solid2;
    if (solid1 + solid2 == 0) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
        return;
    }
    if (p->status == 1 || p->status == 2)
        return;
    any23 = 1;
    goto resolve;
}
