/* Partial recovery of main.c, 0x408358..0x4088c8.  Combo mode uses ordinary
 * solid-foot correction first, then a floor-segment landing intersection. */
void handle_player_collision_combo(int lastX, int lastY)
{
    Tplayer *p;
    int floor_y = -12345678;
    int floor_x1 = 0, floor_x2 = 0;
    int left_x, left_y, right_x, right_y;
    int solid1, solid2, left, right;

    p = ply[player_id];
    solid1 = is_solid(&map, (int)p->x - 11, (int)p->y);
    solid2 = is_solid(&map, (int)p->x + 11, (int)p->y);
    any11 = solid1;
    any12 = solid2;
    any23 = 0;
    any22 = 0;
    any21 = 0;
    if (solid1 || solid2) {
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
        p->y -= solid2 - 9999;
        p->rotate = 0;
        p->edge = 2;
        return;
    }

    if (p->status == 2 || p->status == 0)
        p->status = 3;
    getFloorData(&map, (int)p->y, &floor_y, &floor_x1, &floor_x2);
    if (floor_y == -12345678) {
        getFloorData(&map, lastY, &floor_y, &floor_x1, &floor_x2);
        if (floor_y == -12345678) {
            floor_y = 0;
            floor_x1 = 0;
            floor_x2 = 0;
        }
    }
    left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        (int)p->x - 11, (int)p->y + 1, lastX - 11, lastY, &left_x, &left_y);
    right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        (int)p->x + 11, (int)p->y + 1, lastX + 11, lastY, &right_x, &right_y);
    if (!left && !right) {
        p->edge = 0;
        return;
    }
    p->edge = left == right ? 0 : (left ? 1 : 2);
    if (p->status != 2 && p->status != 3)
        return;

    play_sound(combo_sound[0], 1, 1);
    p->status = 0;
    p->sx = 0;
    p->sy = 0;
    p->y = floor_y - 1;
    p->x = left ? left_x + 11 : right_x - 11;
    p->rotate = 0;
}
