#ifndef ICYTOWER_SCROLLER_H
#define ICYTOWER_SCROLLER_H

#include <allegro.h>

typedef struct {
    int horizontal;
    char *text;
    FONT *fnt;
    int font_height;
    int width;
    int height;
    int offset;
    int rows;
    int length;
    char *lines[512];
} Tscroller;

void init_scroller(Tscroller *sc, FONT *f, char *t, int w, int h, int horiz);
int draw_scroller(Tscroller *sc, BITMAP *bmp, int x, int y, int color);
void scroll_scroller(Tscroller *sc, int step);
void restart_scroller(Tscroller *sc);
#endif
