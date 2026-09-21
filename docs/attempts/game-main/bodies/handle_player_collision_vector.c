/* Partial recovery of main.c, 0x408d08..0x409137.  The normal path is the
 * oracle's floor-segment intersection; its collision-debug line drawing is
 * intentionally left for the presentation recovery pass. */
void handle_player_collision_vector(int lastX, int lastY)
{
    Tplayer *p;
    int floor_y = -12345678;
    int floor_x1 = 0, floor_x2 = 0;
    int left_x, left_y, right_x, right_y;
    int left, right;
    int current_x, current_y;

    p = ply[player_id];
    current_x = (int)p->x;
    current_y = (int)p->y;
    getFloorData(&map, current_y, &floor_y, &floor_x1, &floor_x2);
    if (floor_y == -12345678) {
        getFloorData(&map, lastY, &floor_y, &floor_x1, &floor_x2);
        if (floor_y == -12345678) {
            if (p->status == 2 || p->status == 0)
                p->status = 3;
            return;
        }
    }

    left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        lastX - 11, lastY, current_x - 11, current_y + 1, &left_x, &left_y);
    right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        lastX + 11, lastY, current_x + 11, current_y + 1, &right_x, &right_y);
    if (!left && !right) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
        return;
    }
    p->edge = left == right ? 0 : (left ? 1 : 2);
    if (p->status != 2 && p->status != 3)
        return;
    if (left && right &&
        (left_x < -10000 || right_x < -10000 || left_x > 10000 || right_x > 10000))
        return;

    play_sound(combo_sound[0], 1, 1);
    p->status = 0;
    p->sx = 0;
    p->sy = 0;
    p->y = floor_y - 1;
    p->x = left ? left_x + 11 : right_x - 11;
    p->rotate = 0;
}
