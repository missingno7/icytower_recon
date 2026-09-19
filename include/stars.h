#ifndef ICYTOWER_STARS_H
#define ICYTOWER_STARS_H
#include <allegro.h>

typedef struct {
    double x;
    double y;
    int z;
} Tstar;

typedef struct {
    int clear_color;
    int stars;
    int width;
    int height;
    int depth;
    int col1;
    int col_step;
    Tstar star[1024];
} Tstar_field;

void init_star_field(Tstar_field *sf, int w, int h, int num, int first_col,
                     int last_col, int dep, int cc);
void draw_star_field(Tstar_field *sf, BITMAP *bmp, int x, int y);
void scroll_star_field(Tstar_field *sf, double xstep, double ystep);
#endif
