/* Historical CU: F:\projects\icytower\trunk\source\player.c
 * Ownership: GAME. Other entities remain unrecovered.
 * UNKNOWN: jump_player @ 0x00418678, 198 bytes
 * UNKNOWN: update_player @ 0x00418740, 651 bytes
 */

#include "recovered_types.h"

/* DWARF names parameter p at original line 18. This body preserves the
 * original reset set; x, y, and angle deliberately remain untouched. */
void reset_player(Tplayer *p)
{
    int i;

    p->sx = 0.0;
    p->sy = 0.0;
    p->status = 0;
    p->jump_key = 1;
    p->frame = 0;
    p->level = 0;
    p->in_combo = 0;
    p->acc_level = 0;
    p->acc_jumps = 0;
    p->score = 0;
    p->dead = 0;
    p->max_s = 0.0;
    p->rotate = 0;
    p->edge = 0;
    p->edge_drawn = 0;
    p->bounce = 0;
    p->shake = 0;
    p->latest_combo = 0;
    p->show_combo = 0;
    p->best_combo = 0;
    p->no_combo_top_floor = 0;
    p->biggest_lost_combo = 0;
    for (i = 0; i < 5; i++) {
        p->ccc[i] = 0;
        p->jcTop[i] = 0;
        p->jc[i] = 0;
    }
}

/* DWARF names the second parameter cheat.  The normal jump preserves the
 * original two-path x87 expression instead of reducing it to fabs(sx). */
extern int collision_type;
extern double max_speed[];

int jump_player(Tplayer *p, int cheat)
{
    if (cheat) {
        p->status = 1;
        p->sy = (double)(-(cheat * 12));
        return -1;
    }
    if (p->status)
        return 0;

    p->status = 1;
    {
        double sx = p->sx;
        double candidate = (sx + sx >= 0.0) ? sx * -2.0 : sx + sx;
        double floor_speed = -max_speed[collision_type];

        p->sy = (floor_speed > candidate) ? candidate : floor_speed;
        p->max_s = sx;
    }
    if (p->sy < -22.0)
        p->rotate = 1;
    p->angle = 0;
    return -1;
}

/* Partial recovery of player.c, 0x418740..0x4189cb.  The core integration
 * and state transition order are oracle-backed; mode-table tuning is pending. */
void update_player(Tplayer *p)
{
    double max_speed = 12.0;

    if (p->sy < -100.0)
        p->sy = -max_speed;
    else if (p->sy > max_speed)
        p->sy = max_speed;
    if (p->sx < -max_speed)
        p->sx = -max_speed;
    else if (p->sx > max_speed)
        p->sx = max_speed;

    p->x += p->sx;
    p->y += p->sy;
    if (p->y > 1000.0)
        p->y = 1000.0;
    if (p->x < 0.0) {
        p->x = 0.0;
        p->sx *= -0.9;
        if (p->sx == 4.0)
            p->edge_drawn = 20;
    }
    else if (p->x > 555.0) {
        p->x = 555.0;
        p->sx *= -0.9;
        if (p->sx == -4.0)
            p->edge_drawn = -20;
    }
    if (p->status) {
        p->sy += 0.8;
        if (p->status == 1 && p->sy >= 0.0)
            p->status = 2;
    }
}
