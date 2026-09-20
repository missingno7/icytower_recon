/* Generated from locked DWARF; do not hand-edit. */
#ifndef RECOVERED_TPARTICLE_H
#define RECOVERED_TPARTICLE_H
#include <stddef.h>
#include <allegro.h>
#ifndef RECOVERED_STATIC_ASSERT
#define RECOVERED_STATIC_ASSERT(expr, name) typedef char recovered_static_assert_##name[(expr) ? 1 : -1]
#endif
typedef struct {
    int intensity;
    fixed x;
    fixed y;
    fixed sx;
    fixed sy;
    int color;
} Tparticle;
RECOVERED_STATIC_ASSERT(sizeof(Tparticle) == 24, Tparticle_size);
RECOVERED_STATIC_ASSERT(offsetof(Tparticle, intensity) == 0, Tparticle_offset_intensity);
RECOVERED_STATIC_ASSERT(offsetof(Tparticle, x) == 4, Tparticle_offset_x);
RECOVERED_STATIC_ASSERT(offsetof(Tparticle, y) == 8, Tparticle_offset_y);
RECOVERED_STATIC_ASSERT(offsetof(Tparticle, sx) == 12, Tparticle_offset_sx);
RECOVERED_STATIC_ASSERT(offsetof(Tparticle, sy) == 16, Tparticle_offset_sy);
RECOVERED_STATIC_ASSERT(offsetof(Tparticle, color) == 20, Tparticle_offset_color);
#endif
