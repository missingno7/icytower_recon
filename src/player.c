/* Historical CU: F:\projects\icytower\trunk\source\player.c
 * Ownership: GAME. Other entities remain unrecovered.
 * UNKNOWN: jump_player @ 0x00418678, 198 bytes
 * UNKNOWN: update_player @ 0x00418740, 651 bytes
 */

typedef struct Tplayer {
    double x, y, sx, sy, max_s;
    int level, score, best_combo, status, jump_key, frame, in_combo;
    int acc_level, acc_jumps, dead, rotate;
    int angle;
    int edge, edge_drawn, bounce, shake, latest_combo, show_combo;
    int no_combo_top_floor, biggest_lost_combo;
    int ccc[5], jcTop[5], jc[5];
} Tplayer;

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
