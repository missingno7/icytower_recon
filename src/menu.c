/* Partial historical menu.c recovery. */
typedef struct Tmenu_slider {
    int value;
    int min;
    int max;
    int step;
} Tmenu_slider;

typedef struct Tmenu_selection {
    int value;
    int max;
} Tmenu_selection;

typedef struct Tmenu {
    char caption[128];
    int return_select;
    int return_left;
    int return_right;
    int flags;
    void *data;
} Tmenu;

typedef struct Tmenu_params {
    void *font;
    int font_height;
    int ctrl[9];
    void *bullet;
    int pos;
    void *data;
    int fo;
} Tmenu_params;

extern int text_height(void *font);

int get_slider_value(Tmenu_slider *s) { return s->value; }

int set_slider_value(Tmenu_slider *s, int v)
{
    if (v < s->min || v > s->max) return 0;
    s->value = v;
    return -1;
}

int get_selection_value(Tmenu_selection *s) { return s->value; }

int set_selection_value(Tmenu_selection *s, int v)
{
    if (v < 0 || v >= s->max) return 0;
    s->value = v;
    return -1;
}

void reset_menu(Tmenu *m, Tmenu_params *mp, int sel_pos)
{
    int i;
    int flags;

    i = 0;
    do {
        flags = m[i].flags;
        flags &= ~1;
        m[i].flags = flags;
        i++;
    } while ((signed char)flags >= 0);
    m[sel_pos].flags |= 1;
    mp->font_height = text_height(mp->font);
}
