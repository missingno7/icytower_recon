/* Partial historical menu.c recovery.
 * DIFFER: build_menu_string @ 0x004174dc, 415 bytes
 */
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


typedef struct Tmenu_selection_data {
    int value;
    int max;
    char *choices[1];
} Tmenu_selection_data;

extern void key_to_str(int key, char *dest);

void build_menu_string(Tmenu *m, char *dest)
{
    int v;
    int t;
    int i;

    if (m->flags & 2) {
        Tmenu_slider *s;
        s = (Tmenu_slider *)m->data;
        v = (s->value - s->min) / s->step;
        t = (s->max - s->min) / s->step;
        sprintf(dest, "%s: ", m->caption);
        for (i = 0; i < v; i++)
            strcat(dest, "}");
        for (; i < t; i++)
            strcat(dest, "{");
    } else if (m->flags & 8) {
        Tmenu_selection_data *s;
        s = (Tmenu_selection_data *)m->data;
        sprintf(dest, "%s: %s", m->caption, s->choices[s->value]);
    } else if (m->flags & 4) {
        int *v;
        v = (int *)m->data;
        sprintf(dest, "%s: %s", m->caption, *v ? "YES" : "NO");
    } else if (m->flags & 64) {
        char str[50];
        key_to_str(*(int *)m->data, str);
        sprintf(dest, "%s: (%s)", m->caption, str);
    } else if (m->flags & 16 || m->flags & 32) {
        sprintf(dest, "%s:", m->caption);
    } else
        strcpy(dest, m->caption);
}
