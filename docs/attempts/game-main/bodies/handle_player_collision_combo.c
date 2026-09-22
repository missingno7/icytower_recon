/* Partial recovery of main.c, 0x408358..0x4088c8.  Combo mode uses ordinary
 * solid-foot correction first, then a floor-segment landing intersection. */
/* Geometry recovered and evidenced: plx1=-0x60(ebp), plx2=-0x58(ebp),
 * prx1=-0x50(ebp), prx2=-0x44(ebp) are real slots, computed once right after
 * the floor-data retry (before the `debug` check) by converting DOUBLES for
 * (double)ply[player_id]->x/->y that were cached at function entry (lines
 * 3160/3161, offsets 12-32) -- a deferred 387 float-to-int conversion.
 * fy2/ply2/pry1/pry2 carry NO DW_AT_location at all (trivial copies of
 * fy1/lastY/ply1/lastY the optimizer fully removed), same pattern as
 * handle_player_collision_old's dX. ply[player_id] itself has no DWARF
 * location either -- there is no cached player pointer historically; every
 * ->x/->y/->status/etc access is a fresh ply[player_id]-> dereference.
 * TRIED AND FAILED to close the size gap this way: rewrote the leading
 * `if (solid1 || solid2) {...; return;}` as `if (...) goto solid_return;`
 * with the body moved to a label at the end, matching the shape that fixed
 * handle_player_collision_old (one physical block reached by a forward
 * jump). Measured byte-identical in total (1345, still 45 under 1390) to
 * the inline-if version, and NOT byte-identical instruction-for-instruction
 * (364 vs 365 instructions) -- so the goto is not a no-op, but it does not
 * reproduce the original's out-of-line placement of this block (original
 * jumps away at offset 287 to offset 738; our candidate still emits the
 * block's full body, including its own epilogue, immediately after the
 * branch in every variant measured). The `if`-vs-`goto` surface form does
 * not control block placement the way it did for _old's duplicated-tail
 * case; whatever drives the original's placement here is still unidentified.
 * Prologue callback-saved set (edi,esi,ebx) and frame size (0x9c) are
 * unchanged from the original across all measured variants -- ruled out as
 * the cause. Regression from the pre-geometry baseline (1381, 9 under) to
 * this state (1345, 45 under) is confirmed but not resolved this pass. */
void handle_player_collision_combo(int lastX, int lastY)
{
    Tplayer *p;
    int fy1 = -12345678;
    int fx1 = 0, fx2 = 0;
    int ilx, ily, irx, iry;
    int solid1, solid2, left, right;
    int col1, col2;
    int plx1, ply1, plx2;
    int prx1, prx2;

    p = ply[player_id];
    col1 = makecol(255, 0, 0);
    col2 = makecol(255, 255, 0);
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
    getFloorData(&map, (int)p->y, &fy1, &fx1, &fx2);
    if (fy1 == -12345678) {
        getFloorData(&map, lastY, &fy1, &fx1, &fx2);
        if (fy1 == -12345678) {
            fy1 = 0;
            fx1 = 0;
            fx2 = 0;
        }
    }
    plx1 = (int)p->x - 11;
    ply1 = (int)p->y + 1;
    plx2 = lastX - 11;
    prx1 = (int)p->x + 11;
    prx2 = lastX + 11;
    if (debug) {
        if (key[KEY_F2]) {
            line(screen, fx1, fy1, fx2, fy1, col1);
            line(screen, (int)p->x - 11, (int)p->y + 1, lastX - 11, lastY, col2);
            line(screen, (int)p->x + 11, (int)p->y + 1, lastX + 11, lastY, col2);
        }
    }
    left = line_intersect(fx1, fy1, fx2, fy1,
        plx1, ply1, plx2, lastY, &ilx, &ily);
    right = line_intersect(fx1, fy1, fx2, fy1,
        prx1, ply1, prx2, lastY, &irx, &iry);
    if (!left && !right) {
        p->edge = 0;
        return;
    }
    p->edge = left == right ? 0 : (left ? 1 : 2);
    if (p->status != 2 && p->status != 3)
        return;

    play_sound(combo_sound[0], 1, 1);
    p->status = 0;
    p->sy = 0;
    p->y = fy1 - 1;
    p->x = left ? ilx + 11 : irx - 11;
    p->rotate = 0;
}
