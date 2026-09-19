#include "map.h"

void reset_map(Tmap *m)
{
    int i;
    for (i = 0; i < 32; i++) {
        m->room[i].empty = -1;
        m->room[i].level = 0;
        m->room[i].sign = 0;
    }
    m->offset = 0;
}

int is_solid(Tmap *m, int cx, int cy)
{
    int x, y;
    y = (cy + 1) >> 4;
    if (29 - y < 0 || 29 - y > 31) return 0;
    if (m->room[29 - y].empty != 0) return 0;
    x = cx >> 4;
    if (x < m->room[29 - y].start_tile) return 0;
    if (x > m->room[29 - y].end_tile) return 0;
    return cy - (m->offset % 16) + 10000 - (y << 4);
}

int get_level(Tmap *m, int cy)
{
    int y = 29 - ((cy + 1) >> 4);
    if (y < 0 || y > 31) return 0;
    return m->room[y].level;
}

void getFloorData(Tmap *m, int cy, int *fy, int *fx1, int *fx2)
{
    int y = (cy + 1) >> 4;
    if (29 - y < 0 || 29 - y > 31) return;
    if (m->room[29 - y].empty != 0) return;
    *fx1 = (m->room[29 - y].start_tile << 4) - 2;
    *fx2 = (m->room[29 - y].end_tile << 4) + 17;
    *fy = (y << 4) + (m->offset % 16);
}

/* add_floor @ 0x004167dc, 608 bytes: recovery pending. */
