/* Partial recovery of main.c, 0x4088c8..0x408d08.  This variant retries the
 * floor segment four pixels lower before transitioning to falling state. */
void handle_player_collision_vector_2(int lastX, int lastY)
{
    Tplayer *p;
    int floor_y = -12345678;
    int floor_x1 = 0, floor_x2 = 0;
    int left_x, left_y, right_x, right_y;
    int left, right;
    int current_x, current_y;

    p = ply[player_id];
    current_x = (int)p->x;
    current_y = (int)p->y + 1;
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
        (int)p->x - 11, current_y, lastX - 11, lastY, &left_x, &left_y);
    right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        (int)p->x + 11, current_y, lastX + 11, lastY, &right_x, &right_y);
    if (!left && !right) {
        floor_y += 4;
        left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
            (int)p->x - 11, current_y, lastX - 11, lastY, &left_x, &left_y);
        right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
            (int)p->x + 11, current_y, lastX + 11, lastY, &right_x, &right_y);
    }
    if (!left && !right) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
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
