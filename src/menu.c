/* Partial historical menu.c recovery.
 * DIFFER: build_menu_string @ 0x004174dc, 415 bytes
 * DIFFER: update_game_menu @ 0x00417adc, 583 bytes
 */
#include <allegro.h>
#include <string.h>
#include "control.h"
#include "timer.h"
typedef struct Tmenu_slider {
    int value;
    int min;
    int max;
    int step;
} Tmenu_slider;

typedef struct Tmenu_selection {
    int value;
    int size;
    char caption[128];
} Tmenu_selection;

typedef struct Tmenu_floor_selection {
    int value;
    int max;
} Tmenu_floor_selection;

typedef struct Tmenu_char_selection {
    int value;
    int max;
    BITMAP *bmp;
    PALETTE pal;
} Tmenu_char_selection;

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

int stepIn;

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
    if (v < 0 || v >= s->size) return 0;
    s->value = v;
    return -1;
}

void key_to_str(int k, char *dest)
{
    switch (k) {
    case 1: strcpy(dest, "A"); break;
    case 2: strcpy(dest, "B"); break;
    case 3: strcpy(dest, "C"); break;
    case 4: strcpy(dest, "D"); break;
    case 5: strcpy(dest, "E"); break;
    case 6: strcpy(dest, "F"); break;
    case 7: strcpy(dest, "G"); break;
    case 8: strcpy(dest, "H"); break;
    case 9: strcpy(dest, "I"); break;
    case 10: strcpy(dest, "J"); break;
    case 11: strcpy(dest, "K"); break;
    case 12: strcpy(dest, "L"); break;
    case 13: strcpy(dest, "M"); break;
    case 14: strcpy(dest, "N"); break;
    case 15: strcpy(dest, "O"); break;
    case 16: strcpy(dest, "P"); break;
    case 17: strcpy(dest, "Q"); break;
    case 18: strcpy(dest, "r"); break;
    case 19: strcpy(dest, "S"); break;
    case 20: strcpy(dest, "T"); break;
    case 21: strcpy(dest, "U"); break;
    case 22: strcpy(dest, "V"); break;
    case 23: strcpy(dest, "W"); break;
    case 24: strcpy(dest, "X"); break;
    case 25: strcpy(dest, "Y"); break;
    case 26: strcpy(dest, "Z"); break;
    case 27: strcpy(dest, "0"); break;
    case 28: strcpy(dest, "1"); break;
    case 29: strcpy(dest, "2"); break;
    case 30: strcpy(dest, "3"); break;
    case 31: strcpy(dest, "4"); break;
    case 32: strcpy(dest, "5"); break;
    case 33: strcpy(dest, "6"); break;
    case 34: strcpy(dest, "7"); break;
    case 35: strcpy(dest, "8"); break;
    case 36: strcpy(dest, "9"); break;
    case 37: strcpy(dest, "0 (Pad)"); break;
    case 38: strcpy(dest, "1 (Pad)"); break;
    case 39: strcpy(dest, "2 (Pad)"); break;
    case 40: strcpy(dest, "3 (Pad)"); break;
    case 41: strcpy(dest, "4 (Pad)"); break;
    case 42: strcpy(dest, "5 (Pad)"); break;
    case 43: strcpy(dest, "6 (Pad)"); break;
    case 44: strcpy(dest, "7 (Pad)"); break;
    case 45: strcpy(dest, "8 (Pad)"); break;
    case 46: strcpy(dest, "9 (Pad)"); break;
    case 47: strcpy(dest, "F1"); break;
    case 48: strcpy(dest, "F2"); break;
    case 49: strcpy(dest, "F3"); break;
    case 50: strcpy(dest, "F4"); break;
    case 51: strcpy(dest, "F5"); break;
    case 52: strcpy(dest, "F6"); break;
    case 53: strcpy(dest, "F7"); break;
    case 54: strcpy(dest, "F8"); break;
    case 55: strcpy(dest, "F9"); break;
    case 56: strcpy(dest, "F10"); break;
    case 57: strcpy(dest, "F11"); break;
    case 58: strcpy(dest, "F12"); break;
    case 59: strcpy(dest, "ESC"); break;
    case 60: strcpy(dest, "TILDE"); break;
    case 61: strcpy(dest, "-"); break;
    case 62: strcpy(dest, "="); break;
    case 63: strcpy(dest, "Backspace"); break;
    case 64: strcpy(dest, "Tab"); break;
    case 65: strcpy(dest, "{"); break;
    case 66: strcpy(dest, "}"); break;
    case 67: strcpy(dest, "Enter"); break;
    case 68: strcpy(dest, ":"); break;
    case 105: strcpy(dest, ";"); break;
    case 69: strcpy(dest, "'"); break;
    case 70: strcpy(dest, "\\"); break;
    case 71: strcpy(dest, "\\"); break;
    case 72: strcpy(dest, ","); break;
    case 73: strcpy(dest, "."); break;
    case 74: strcpy(dest, "/"); break;
    case 75: strcpy(dest, "Space"); break;
    case 76: strcpy(dest, "Insert"); break;
    case 77: strcpy(dest, "Delete"); break;
    case 78: strcpy(dest, "Home"); break;
    case 79: strcpy(dest, "End"); break;
    case 80: strcpy(dest, "Pg Up"); break;
    case 81: strcpy(dest, "Pg Down"); break;
    case 82: strcpy(dest, "Left"); break;
    case 83: strcpy(dest, "Right"); break;
    case 84: strcpy(dest, "Up"); break;
    case 85: strcpy(dest, "Down"); break;
    case 86: strcpy(dest, "/ (Pad)"); break;
    case 87: strcpy(dest, "*"); break;
    case 88: strcpy(dest, "- (Pad)"); break;
    case 89: strcpy(dest, "+ (Pad)"); break;
    case 90: strcpy(dest, "Del (Pad)"); break;
    case 91: strcpy(dest, "Enter (Pad)"); break;
    case 92: strcpy(dest, "Print Screen"); break;
    case 93: strcpy(dest, "Pause"); break;
    case 95: strcpy(dest, "Yen"); break;
    case 96: strcpy(dest, "Kana"); break;
    case 115: strcpy(dest, "L Shift"); break;
    case 116: strcpy(dest, "R Shift"); break;
    case 117: strcpy(dest, "L Ctrl"); break;
    case 118: strcpy(dest, "R Ctrl"); break;
    case 119: strcpy(dest, "Alt"); break;
    case 120: strcpy(dest, "Alt Gr"); break;
    case 121: strcpy(dest, "Left Win"); break;
    case 122: strcpy(dest, "Right Win"); break;
    case 123: strcpy(dest, "Menu"); break;
    case 124: strcpy(dest, "Scroll Lock"); break;
    case 125: strcpy(dest, "Num Lock"); break;
    case 126: strcpy(dest, "Caps Lock"); break;
    default: strcpy(dest, "undefined"); break;
    }
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
extern void draw_menu(BITMAP *bmp, Tmenu *m, Tmenu_params *mp, int x, int y,
                      int step_in);
extern void play_menu_move(void);
extern void play_menu_select(void);
extern void checkMenuFocus(void);
extern void blit_to_screen(BITMAP *bmp);
extern void line_alert(char *text);
extern void view_profile(void *p);
extern void change_profile(void);
extern void *profile;
extern int closeButtonClicked;
extern int stepIn;
extern volatile char key[];
/* Icy Tower was built against an older Allegro scancode layout. */
#ifdef KEY_F1
#undef KEY_F1
#endif
#define KEY_F1 59

void build_menu_string(Tmenu *m, char *dest);

/* The original keeps the second slider bitmap in a small menu-specific
 * pointer table; it is not a Tmenu_slider despite sharing the menu data
 * field. */
void draw_menu(BITMAP *bmp, Tmenu *m, Tmenu_params *mp, int cx, int y, int dx)
{
    int pos;
    int h;
    char str[256];

    stepIn = dx;
    h = mp->font_height - 12;
    pos = -1;
    do {
        int x;

        pos++;
        x = cx + dx * pos;
        build_menu_string(m, str);
        if (m->flags & 64) {
            char key_str[50];

            key_to_str(*(int *)m->data, key_str);
            textprintf_ex(bmp, (FONT *)mp->font, x, y, -1, -1, "%s:", m->caption);
            textprintf_ex(bmp, (FONT *)mp->font, x + 101, y, -1, -1, "%s", key_str);
        }
        if (m->flags & 1)
            draw_sprite(bmp, (BITMAP *)mp->bullet,
                        x - 3 - ((BITMAP *)mp->bullet)->w, y - 3);
        textout_ex(bmp, (FONT *)mp->font, str, x, y, -1, -1);
        if (m->flags & 16) {
            DATAFILE *assets;

            assets = (DATAFILE *)mp->data + mp->fo;
            draw_sprite(bmp, (BITMAP *)assets[0].dat, x + 215, y + 10);
            draw_sprite(bmp, (BITMAP *)assets[1].dat, x + 236, y + 10);
            draw_sprite(bmp, (BITMAP *)assets[2].dat, x + 252, y + 10);
        }
        if (m->flags & 32) {
            BITMAP *b;

            b = ((BITMAP **)m->data)[2];
            draw_sprite(bmp, b, x + 244 - b->w / 2, y + y - b->h + 10);
        }
        m++;
        y += h;
    } while (!(m[-1].flags & 0x80000000));
}

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

int update_game_menu(void *bmp, Tmenu *m, Tmenu_params *mp, Tcontrol *ctrl,
                     int x, int y, int *data)
{
    int num_posts;
    int old_pos;
    int pos;
    int return_value;

    pos = 0;
    num_posts = -1;
    do {
        num_posts++;
        if (m[num_posts].flags & 1)
            pos = num_posts;
    } while (!(m[num_posts].flags & 0x80000000));
    old_pos = pos;
    draw_menu(bmp, m, mp, x, y, stepIn);
    if (ctrl) {
        if (is_up(ctrl) || is_up((Tcontrol *)&mp->ctrl[0])) {
            pos--;
            if (pos < 0)
                pos = num_posts;
        } else if (is_down(ctrl) || is_down((Tcontrol *)&mp->ctrl[0])) {
            pos++;
            if (pos > num_posts)
                pos = 0;
        }
    }
    if (key[KEY_F1] && pos != num_posts)
        pos = num_posts;
    return_value = 0;
    if (old_pos != pos) {
        m[old_pos].flags &= ~1;
        m[pos].flags |= 1;
        play_menu_move();
    }
    if (ctrl) {
        if (is_fire(ctrl) || is_enter((Tcontrol *)&mp->ctrl[0]) ||
            is_fire((Tcontrol *)&mp->ctrl[0]))
            return_value = m[pos].return_select;
        else if (is_left(ctrl) || is_left((Tcontrol *)&mp->ctrl[0]))
            return_value = m[pos].return_left;
        else if (is_right(ctrl) || is_right((Tcontrol *)&mp->ctrl[0]))
            return_value = m[pos].return_right;
    }
    *data = (int)m[pos].data;
    mp->pos = pos;
    return return_value;
}

int handle_menu(Tmenu *menu, Tmenu_params *mp, Tcontrol *ctrl, BITMAP *bmp,
                void (*callback)(void), int x, int y, int dx)
{
    int menu_return;
    int handle_keys;
    int data;
    int key_counter;

    stepIn = dx;
    data = 0;
    reset_menu(menu, mp, mp->pos);
    handle_keys = 0;
    key_counter = 0;
    menu_return = 0;
    while (!closeButtonClicked) {
        cycle_count = 0;
        checkMenuFocus();
        if (callback)
            callback();
        else
            clear(bmp);
        if (handle_keys)
            menu_return = update_game_menu(bmp, menu, mp, ctrl, x, y, &data);
        else
            menu_return = 0;
        blit_to_screen(bmp);

        if (is_any(ctrl) || is_any((Tcontrol *)&mp->ctrl[0]) || key[KEY_F1]) {
            if (key_counter)
                key_counter--;
            else
                key_counter = 39;
            handle_keys = key_counter ? 0 : -1;
        } else {
            key_counter = 0;
            handle_keys = -1;
        }
        poll_control(ctrl, 1);
        poll_control((Tcontrol *)&mp->ctrl[0], 0);

        if (menu_return) {
            play_menu_select();
            switch (menu_return) {
            case 101:
            case 104:
            case 105:
            case 107:
            case 108:
            case 122:
            case 123:
            case 124:
            case 133:
                return menu_return;
            case 103: {
                int sub_ret;

                mp->pos = 0;
                sub_ret = handle_menu((Tmenu *)data, mp, ctrl, bmp, callback,
                                      x, y, dx);
                if (sub_ret && sub_ret != 108)
                    return sub_ret;
                break;
            }
            case 109: {
                Tmenu_slider *sld = (Tmenu_slider *)data;

                sld->value += sld->step;
                if (sld->value > sld->max)
                    sld->value = sld->max;
                break;
            }
            case 110: {
                Tmenu_slider *sld = (Tmenu_slider *)data;

                sld->value -= sld->step;
                if (sld->value < sld->min)
                    sld->value = sld->min;
                break;
            }
            case 111:
            case 118:
            case 120:
                if (--*(int *)data < 0)
                    *(int *)data = 0;
                break;
            case 112: {
                Tmenu_selection *sel = (Tmenu_selection *)data;

                if (++sel->value > sel->size - 1)
                    sel->value = sel->size - 1;
                break;
            }
            case 113:
                *(int *)data = *(int *)data < 1 ? -1 : 0;
                break;
            case 114: {
                int k;
                int kp;
                char txt[256];

                sprintf(txt, "press key for %s", menu[mp->pos].caption);
                line_alert(txt);
                for (k = 0; k < 128; k++)
                    key[k] = 0;
                for (;;) {
                    k = 0;
                    for (kp = 0; kp < 128; kp++)
                        if (key[kp])
                            k = kp;
                    if (k == KEY_F1)
                        k = *(int *)data;
                    rest(2);
                    if (k)
                        break;
                }
                for (kp = 0; kp < 128; kp++)
                    key[kp] = 0;
                *(int *)data = k;
                play_menu_select();
                break;
            }
            case 119:
            case 121: {
                Tmenu_floor_selection *sel = (Tmenu_floor_selection *)data;

                if (++sel->value > sel->max)
                    sel->value = sel->max;
                break;
            }
            case 131:
                view_profile(profile);
                break;
            case 132:
                change_profile();
                break;
            default: {
                char buf[256];

                sprintf(buf, "unknown return value: %d", menu_return);
                my_alert("handle_menu", buf, NULL, "OK", NULL, 0, 0);
                break;
            }
            }
        }
        while (!cycle_count)
            rest(2);
    }
    return menu_return;
}
