/* Partial recovery of main.c, 0x4088c8..0x408d08.  This variant retries the
 * floor segment four pixels lower before transitioning to falling state. */
void handle_player_collision_vector_2(int lastX, int lastY)
{
    Tplayer *p;
    int floor_y, floor_x1, floor_x2;
    int left_x, left_y, right_x, right_y;
    int left, right;
    int current_x, current_y;
    int plx1, plx2, prx1, prx2;
    int col1, col2;

    p = ply[player_id];
    plx1 = (int)p->x - 11;
    current_x = (int)p->x;
    current_y = (int)p->y + 1;
    plx2 = lastX - 11;
    prx1 = (int)p->x + 11;
    prx2 = lastX + 11;
    col1 = makecol(255, 0, 0);
    col2 = makecol(255, 255, 0);
    floor_y = -12345678;
    floor_x1 = 0;
    floor_x2 = 0;
    getFloorData(&map, (int)p->y, &floor_y, &floor_x1, &floor_x2);
    if (floor_y == -12345678) {
        getFloorData(&map, lastY, &floor_y, &floor_x1, &floor_x2);
        if (floor_y == -12345678) {
            floor_y = 0;
            floor_x1 = 0;
            floor_x2 = 0;
        }
    }

    if (debug) {
        if (key[KEY_F2]) {
            line(screen, floor_x1, floor_y, floor_x2, floor_y, col1);
            line(screen, plx1, current_y, plx2, lastY, col2);
            line(screen, prx1, current_y, prx2, lastY, col2);
        }
    }
    left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        plx1, current_y, plx2, lastY, &left_x, &left_y);
    right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        prx1, current_y, prx2, lastY, &right_x, &right_y);
    if (!left && !right) {
        left = line_intersect(floor_x1, floor_y + 4, floor_x2, floor_y + 4,
            plx1, current_y, plx2, lastY, &left_x, &left_y);
        right = line_intersect(floor_x1, floor_y + 4, floor_x2, floor_y + 4,
            prx1, current_y, prx2, lastY, &right_x, &right_y);
    }
    if (!left && !right) {
        if (ply[player_id]->status == 2 || ply[player_id]->status == 0)
            ply[player_id]->status = 3;
        ply[player_id]->edge = 0;
        return;
    }
    ply[player_id]->edge = left == right ? 0 : (left ? 1 : 2);
    if (ply[player_id]->status != 2 && ply[player_id]->status != 3)
        return;

    play_sound(combo_sound[0], 1, 1);
    ply[player_id]->status = 0;
    ply[player_id]->sy = 0;
    ply[player_id]->y = floor_y - 1;
    ply[player_id]->x = left ? left_x + 11 : right_x - 11;
    ply[player_id]->rotate = 0;
}
