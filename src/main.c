/* Partial historical main.c recovery. Other original entities remain absent. */
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <allegro.h>
#include "loadpng.h"
#include "beta.h"
#include "control.h"
#include "custom.h"
#include "directories.h"
#include "game_services.h"
#include "timer.h"
#include "particle.h"
#include "map.h"
#include "scroller.h"

/* This exported extension belongs to the separately reconstructed logg CU. */
SAMPLE *logg_load_memory(void *pData, size_t iSize);
extern void *__attribute__((stdcall)) ShellExecuteA(void *hwnd,
    const char *operation, const char *file, const char *parameters,
    const char *directory, int show);

/* Declared at original line 92; log2file suppresses output while it is set. */
int itrcheck;
int init_ok;
char last_log[1024];
typedef struct {
    int jumps;
    int combos;
    int sd;
    int keys;
    int tiny;
} Tcmdline;
Tcmdline cmdline;
double seed;
int hasFocus;
int closeButtonClicked;
int window;
int lastFocus;
int in_replay_menu;
int collision_type;
int got_joystick;
int scroll_count;
int scroll_delay;
int gdLastJumpDiff;
int last_stripe_y;
int new_personal_best[15];
Tbeta *testers;
Tbeta *the_tester;

typedef struct Treplay {
    char header[6];
    int size;
    char name[32];
    char date[32];
    int checksum;
    int score;
    int floor;
    int combo;
    int no_combo_top_floor;
    int biggest_lost_combo;
    int ccc[5];
    int jc[5];
    int floor_shrink;
    int floor_size;
    int start_speed;
    int speed_increase;
    int gravity;
    int rejump;
    int random_seed;
} Treplay;
Treplay *demo;
Tcontrol ctrl;
extern DATAFILE *data;

void line_alert(char *text)
{
    int color;
    int width;
    int height;

    set_trans_blender(0,0,0,158);
    drawing_mode(DRAW_MODE_TRANS,0,0,0);
    color=makecol(0,0,0);
    width=0;
    height=0;
    if (gfx_driver) {
        width=gfx_driver->w;
        height=gfx_driver->h;
    }
    rectfill(screen,0,0,width,height,color);
    solid_mode();
    draw_sprite(screen,data[88].dat,103,200);
    textprintf_centre_ex(screen,data[51].dat,320,220,-1,-1,"%s",text);
}

void blit_to_screen(BITMAP *bmp);
void checkMenuFocus(void);

BITMAP *swap_screen;

void fadeIn(BITMAP *bmp, int speed)
{
    int a;
    BITMAP *mybmp;

    mybmp=create_bitmap(SCREEN_W,SCREEN_H);
    for (a=255;a>0;a-=speed) {
        cycle_count=0;
        draw_sprite(mybmp,bmp,0,0);
        set_trans_blender(0,0,0,a);
        drawing_mode(DRAW_MODE_TRANS,0,0,0);
        rectfill(mybmp,0,0,SCREEN_W,SCREEN_H,makecol(0,0,0));
        solid_mode();
        blit_to_screen(mybmp);
        while (!cycle_count) rest(2);
    }
    destroy_bitmap(mybmp);
}

void fadeOut(int speed)
{
    int a;
    BITMAP *bmp;

    bmp=create_bitmap(SCREEN_W,SCREEN_H);
    blit(screen,bmp,0,0,0,0,SCREEN_W,SCREEN_H);
    for (a=0;a<256;a+=speed) {
        cycle_count=0;
        draw_sprite(swap_screen,bmp,0,0);
        set_trans_blender(0,0,0,a);
        drawing_mode(DRAW_MODE_TRANS,0,0,0);
        rectfill(swap_screen,0,0,SCREEN_W,SCREEN_H,makecol(0,0,0));
        solid_mode();
        blit_to_screen(swap_screen);
        while (!cycle_count) rest(2);
    }
    destroy_bitmap(bmp);
    rectfill(screen,0,0,SCREEN_W,SCREEN_H,makecol(0,0,0));
}

void show_instructions(void)
{
    int done;

    blit(data[126].dat,screen,0,0,0,0,640,480);
    masked_blit(data[70].dat,screen,0,0,0,0,640,480);
    while (is_any(&ctrl))
        poll_control(&ctrl,0);
    fadeIn(screen,16);
    done=0;
    while (!closeButtonClicked && !done) {
        cycle_count=0;
        checkMenuFocus();
        poll_control(&ctrl,0);
        done=is_fire(&ctrl);
        if (key[KEY_ESC])
            done=1;
        if (!cycle_count)
            rest(2);
    }
    fadeOut(16);
}

typedef struct Toptions {
    int flash;
    int checksum;
    int jump_hold;
    int full_screen;
    int floor_shrink;
    int floor_size;
    int start_speed;
    int speed_increase;
    int gravity;
    int msc_volume;
    int snd_volume;
    int sort_method;
    char updateDate[16];
    char posterDate[16];
    char posterUrl[256];
    char posterSrc[256];
    int posterSize;
    char lastProfile[32];
    int timesStarted;
} Toptions;

typedef struct Tprofile {
    unsigned char header[6];
    char handle[32];
    int checksum;
    int games_played;
    int custom_games_played;
    int games_quit;
    int seconds_spent_playing;
    int total_floors;
    int total_score;
    int total_combos;
    int total_combo_floors;
    int best_floor;
    int best_combo;
    int best_score;
    int no_combo_top_floor;
    int biggest_lost_combo;
    int cccNum[5];
    int cccTotal[5];
    int ccc[5];
    int jc[5];
    unsigned char reserved1[0x4dc-176];
    int flash;
    int jump_hold;
    unsigned char reserved2[64];
    int start_floor;
    int msc_volume;
    int snd_volume;
} Tprofile;

typedef struct Tavailable_profile {
    char handle[32];
} Tavailable_profile;

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

/* menu.h layout recovered from the main-CU DWARF inventory. */
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

typedef struct FLDAdSpot {
    const char *pRemoteImageURL;
    const char *pLocalImagePath;
    const char *pVisitURL;
    float fFrequency;
} FLDAdSpot;
extern const FLDAdSpot *fldads_get_random_ad(void);

typedef struct Tavatar_profile {
    unsigned char reserved[0x4e4];
    char avatar[1];
} Tavatar_profile;

typedef struct Tcharacter {
    char filename[1024];
    BITMAP *bmp;
    int ok;
    char name[128];
    int uses_datafile;
    PALETTE pal;
} Tcharacter;

typedef struct Tplayer {
    double x;
    double y;
    double sx;
    double sy;
    double max_s;
    int level;
    int score;
    int best_combo;
    int status;
    int jump_key;
    int frame;
    int in_combo;
    int acc_level;
    int acc_jumps;
    int dead;
    int rotate;
    float angle;
    int edge;
    int edge_drawn;
    int bounce;
    int shake;
    int latest_combo;
    int show_combo;
    int no_combo_top_floor;
    int biggest_lost_combo;
    int ccc[5];
    int jcTop[5];
    int jc[5];
} Tplayer;

typedef struct Tgame_data {
    Treplay *replay;
} Tgame_data;

typedef struct Tjump_sequence {
    int start;
    int dist;
    int num;
} Tjump_sequence;

Toptions options;
int start_speeds[6] = { 5, 4, 3, 2, 1, 0 };
char *version_str = "1.5.1";
Tprofile *profile;
Tavailable_profile *profiles;
int numProfiles;
SAMPLE *bg_menu;
SAMPLE *menu_sounds[2];
SAMPLE *jump_sound[3];
SAMPLE *speaker[3];
SAMPLE *sounds[9];
Tcustom custom;
int reward_time;
fixed reward_scale;
BITMAP *reward_bmp;
Tparticle stars[512];
SAMPLE *combo_sound[10];
int num_chars;
Tcharacter *characters;
int curr_char;
int play_char;
Tplayer *ply[1000];
int player_id;
int any11;
int any12;
int any13;
int any21;
int any22;
int any23;
Tmap map;
Tgame_data *gameData;
int rejump;
Tjump_sequence jumpSequence;
int fast_forward;
int fast_fast_forward;
int gameMusicVoiceID = -1;
SAMPLE *bg_beat;
Tmenu_slider snd_volume_slider = { 0, 0, 250, 25 };
Tmenu_slider msc_volume_slider = { 0, 0, 250, 25 };
Tmenu_selection eyecandy_selection;
Tmenu_floor_selection floors;
Tmenu_selection scroll_speed_selection;
Tmenu_selection floor_size_selection;
Tmenu_selection gravity_selection;
Tmenu_params menu_params;
char replay_directory[1024];
BITMAP *pFLDAdBitmap;
const FLDAdSpot *pFLDAd;
DATAFILE *data;
int rec_pos;
int recording;
int rec_seed;
int hurry_y;
void *hisc_tables[15];
static int count;
char summary_scroller_message[5120];
Tscroller summary_scroller;
static char *result_categories[5] = {
    "Score", "Best Combo", "Floor", "Lost Combo", "Top Floor, No Combos"
};

/* Initialized menu data recovered from main.c's DWARF declarations and the
 * original .data bytes.  Links stay symbolic so the ordinary linker owns the
 * final relocations. */
Tmenu ctrl_menu[6] = {
    { "LEFT",   'r', 0,   0,   0x40, &ctrl.key_left },
    { "RIGHT",  'r', 0,   0,   0x40, &ctrl.key_right },
    { "JUMP",   'r', 0,   0,   0x40, &ctrl.key_fire },
    { "PAUSE",  'r', 0,   0,   0x40, &ctrl.key_pause },
    { "ReJump", 'q', 'q', 'q', 0x04, &rejump },
    { "Back",   'l', 0,   0,   0x80, NULL }
};

Tmenu snd_menu[3] = {
    { "Sound",   0, 'n', 'm', 0x02, &snd_volume_slider },
    { "Music\\\\", 0, 'n', 'm', 0x02, &msc_volume_slider },
    { "Back",   'l', 0,   0,   0x80, NULL }
};

Tmenu gfx_menu[5] = {
    { "Character",   0,   'x', 'y', 0x20, &play_char },
    { "Start floor", 0,   'v', 'w', 0x10, &floors },
    { "Eye Candy",   0,   'p', 'o', 0x08, &eyecandy_selection },
    { "Fullscreen",  'q', 'q', 'q', 0x04, &options.full_screen },
    { "Back",        'l', 0,   0,   0x80, NULL }
};

Tmenu game_menu[1] = {
    { "Back", 'l', 0, 0, 0x80, NULL }
};

Tmenu profile_menu[3] = {
    { "View Profile",   0x83, 0, 0, 0, NULL },
    { "Change Profile", 0x84, 0, 0, 0, NULL },
    { "Back",           'l',  0, 0, 0x80, NULL }
};

Tmenu opt_menu[4] = {
    { "GFX Options",   'g', 0, 0, 0, gfx_menu },
    { "Sound Options", 'g', 0, 0, 0, snd_menu },
    { "Controls",      'g', 0, 0, 0, ctrl_menu },
    { "Back",          'l', 0, 0, 0x80, NULL }
};

Tmenu custom_menu[5] = {
    { "Start Game", 0x85, 0,   0,   0,    NULL },
    { "Speed",      0,    'p', 'o', 0x08, &scroll_speed_selection },
    { "Floors",     0,    'p', 'o', 0x08, &floor_size_selection },
    { "Gravity",    0,    'p', 'o', 0x08, &gravity_selection },
    { "Back",       'l',  0,   0,   0x80, NULL }
};

Tmenu play_menu[3] = {
    { "Classic Game", 'e', 0, 0, 0,    NULL },
    { "Custom Game",  'g', 0, 0, 0,    custom_menu },
    { "Back",         'l', 0, 0, 0x80, NULL }
};

Tmenu main_menu[7] = {
    { "Play Game",   'g', 0, 0, 0,    play_menu },
    { "Instructions", 'h', 0, 0, 0,    NULL },
    { "Profile",     'g', 0, 0, 0,    profile_menu },
    { "High Scores", 'i', 0, 0, 0,    NULL },
    { "Load Replay", 'z', 0, 0, 0,    NULL },
    { "Options",     'g', 0, 0, 0,    opt_menu },
    { "Exit",        'k', 0, 0, 0x80, NULL }
};

Tmenu replay_menu[5] = {
    { "Play Again",    'e', 0, 0, 0,    NULL },
    { "Watch Replay",  '|', 0, 0, 0,    NULL },
    { "Save Replay",   '{', 0, 0, 0,    NULL },
    { "View Profile",  0x83, 0, 0, 0,  NULL },
    { "Main Menu",     'l', 0, 0, 0x80, NULL }
};

/* Candidate recovered from the complete 0x40cd68..0x40d452 modal path. */
int my_alert(char *func, char *txt, int choice, int enter_hint)
{
    Tcontrol *menu_ctrl = (Tcontrol *)menu_params.ctrl;
    int status = 0;
    int done = 0;

    set_trans_blender(0, 0, 0, 158);
    drawing_mode(DRAW_MODE_TRANS, 0, 0, 0);
    rectfill(screen, 0, 0, SCREEN_W - 1, SCREEN_H - 1, makecol(0, 0, 0));
    solid_mode();
    blit(screen, swap_screen, 0, 0, 0, 0, SCREEN_W, SCREEN_H);
    textprintf_centre_ex(screen, data[204].dat, 320, 135, -1, -1, "%s", func ? func : "");
    if (txt)
        textout_centre_ex(screen, data[216].dat, txt, 320, 180, makecol(0, 0, 0), -1);
    while (is_any(&ctrl) || is_any(menu_ctrl) || key[KEY_ESC]) {
        poll_control(&ctrl, 0); poll_control(menu_ctrl, 0); rest(2);
    }
    clear_keybuf();
    while (!done && !closeButtonClicked) {
        poll_control(&ctrl, 0); poll_control(menu_ctrl, 0);
        if (is_left(&ctrl) || is_left(menu_ctrl)) status = -1;
        if (is_right(&ctrl) || is_right(menu_ctrl)) status = 0;
        if (is_fire(&ctrl) || is_fire(menu_ctrl) || is_enter(menu_ctrl)) done = -1;
        if (choice) {
            draw_sprite(screen, data[status == -1 ? 11 : 10].dat, 240, 220);
            draw_sprite(screen, data[status == -1 ? 8 : 7].dat, 365, 220);
        }
        if (enter_hint)
            textout_right_ex(screen, data[216].dat, "Enter", 520, 200,
                             makecol(80, 80, 80), -1);
        if (!done) rest(2);
    }
    blit(swap_screen, screen, 0, 0, 0, 0, SCREEN_W, SCREEN_H);
    return status;
}

void show_credits(void)
{
    double vol;
    double vol_step;
    int gc;
    BITMAP *logoBMP;

    vol=options.msc_volume;
    vol_step=vol/150.0f;
    clear_bitmap(screen);
    logoBMP=data[125].dat;
    blit(data[126].dat,screen,0,0,0,0,640,480);
    draw_sprite(screen,logoBMP,320-logoBMP->w/2,10);
    textout_centre_ex(screen,data[50].dat,"Thanks for playing!",320,280,-1,-1);
    textout_centre_ex(screen,data[52].dat,"DESIGN & CODING: Johan Peitz",320,360,-1,-1);
    textout_centre_ex(screen,data[52].dat,"GRAPHICS: Emanuel Garnheim",320,390,-1,-1);
    fadeIn(screen,16);
    closeButtonClicked=0;
    cycle_count=0;
    while (!key[KEY_ESC] && cycle_count<=149) {
        gc=cycle_count;
        checkMenuFocus();
        if (bg_menu)
            adjust_sample(bg_menu,(int)vol,128,1000,1);
        while (gc==cycle_count)
            rest(2);
        if (closeButtonClicked)
            break;
        vol-=vol_step;
    }
    fadeOut(16);
}


extern void save_options(Toptions *o, PACKFILE *fp);
extern void save_hisc_table(void *table, PACKFILE *fp);
extern void save_profile(Tprofile *profile);
extern Tprofile *select_profile(Tprofile *current_profile, Tavailable_profile *profiles,
                                int numProfiles, Tcontrol *ctrl);
extern int rebuild_profile_list(Tavailable_profile **profs);
extern Tprofile *load_profile(char *handle);
extern Tprofile *create_profile(char *handle, int overwrite);
extern int handle_menu(Tmenu *menu, Tmenu_params *mp, Tcontrol *ctrl,
                       BITMAP *bmp, void (*callback)(void), int x, int y, int dx);
extern void destroy_replay(Treplay *r);
extern Treplay *load_replay(char *filename);
extern void run_demo(char *file_name);
extern int new_game(void);
extern int play(void);
extern int load_character(const char *filename, int attrib, void *param);

char *get_version_str(void)
{
    return "1.5.1";
}

Treplay *get_demo(void)
{
    return demo;
}

Tcontrol *get_controls(void)
{
    return &ctrl;
}

int new_rand(void)
{
    int x;
    seed = seed * 1.4294484665;
    while (seed > 65535.0f) seed -= 65535.0f;
    x = (int)seed;
    return (int)((seed-x) * 65535.0f);
}

inline void new_srand(int s)
{
    seed=s;
}

void set_current_avatar(void);

inline void syncProfileFromOptions(void)
{
    profile->msc_volume = options.msc_volume;
    profile->snd_volume = options.snd_volume;
    profile->jump_hold = options.jump_hold;
    profile->flash = options.flash;
}

void syncOptionsFromProfile(void)
{
    options.msc_volume = profile->msc_volume;
    options.snd_volume = profile->snd_volume;
    options.jump_hold = profile->jump_hold;
    options.flash = profile->flash;
    snd_volume_slider.value = options.snd_volume;
    msc_volume_slider.value = options.msc_volume;
    eyecandy_selection.value = options.flash;
    set_current_avatar();
    get_profile_dir_for_profile(replay_directory, sizeof(replay_directory),
                                profile->handle);
    strcat(replay_directory, "replays/");
}

int get_gamepad_value(char *dir)
{
    char *action = get_config_string(NULL, dir, "nothing");
    if (!stricmp(action, "up"))
        return 4;
    if (!stricmp(action, "down"))
        return 8;
    if (!stricmp(action, "left"))
        return 1;
    if (!stricmp(action, "right"))
        return 2;
    if (!stricmp(action, "jump"))
        return 16;
    return 0;
}

void load_sound(SAMPLE **dest, char *fname, BITMAP *bmp, int y)
{
    if (bmp)
        textprintf_ex(bmp, font, 0, y, 15, -1, "loading: %s", fname);
    *dest = load_wav(fname);
    if (*dest)
        return;
    alert("load_sound(): file not found", fname, NULL, "OK", NULL, 0, 0);
}

void take_screenshot(BITMAP *bmp)
{
    static int number;
    PALETTE p;
    BITMAP *b;
    char buf[256];
    int found;

    for (;;) {
        sprintf(buf, "screenshots/icytower_%04d.png", number++);
        found = exists(buf);
        if (number > 9999) {
            log2file("*** Too many screenshots in the screenshot folder! Delete some and try again.");
            return;
        }
        if (!found)
            break;
    }
    get_palette(p);
    b = create_sub_bitmap(bmp, 0, 0, bmp->w, bmp->h);
    save_bitmap(buf, b, p);
    destroy_bitmap(b);
    while (key[KEY_F12])
        ;
}

#ifndef ICYTOWER_SYNTHETIC_LINK
void open_web_browser(char *pURL)
{
    char cmd[256];
    sprintf(cmd, "url.dll, FileProtocolHandler %s", pURL);
    log2file(" calling '%s'", cmd);
    ShellExecuteA(NULL, "open", "rundll32", cmd, "", 4);
}
#endif

#ifndef ICYTOWER_SYNTHETIC_LINK
void load_new_ad_image(void)
{
    const FLDAdSpot *pAd = fldads_get_random_ad();
    if (pAd) {
        log2file("Got ad: %s", pAd->pLocalImagePath);
        if (pFLDAdBitmap) {
            destroy_bitmap(pFLDAdBitmap);
            pFLDAdBitmap = NULL;
        }
        pFLDAdBitmap = load_bitmap(pAd->pLocalImagePath, NULL);
        pFLDAd = pAd;
    }
}
#endif

int ok_to_play(void)
{
    return 1;
}

void switchedFromProgram(void)
{
    hasFocus = 0;
}

void switchedToProgram(void)
{
    hasFocus = 1;
}

void clickedCloseButton(void)
{
    closeButtonClicked = 1;
}

void testWindowResolution(void)
{
    if (window) {
        if (!options.full_screen)
            return;
        {
            PALETTE pal;
            log2file("Switching to fullscreen (640x480)");
            get_palette(pal);
            show_mouse(NULL);
            set_gfx_mode(GFX_AUTODETECT_FULLSCREEN,640,480,0,0);
            set_palette(pal);
            window=0;
            set_display_switch_mode(SWITCH_BACKAMNESIA);
            set_display_switch_callback(SWITCH_IN,switchedToProgram);
            set_display_switch_callback(SWITCH_OUT,switchedFromProgram);
            if (window)
                return;
        }
    }
    if (options.full_screen)
        return;
    {
        PALETTE pal;
        log2file("Switching to window (640x480)");
        get_palette(pal);
        set_gfx_mode(GFX_AUTODETECT_WINDOWED,640,480,0,0);
        set_palette(pal);
        window=1;
        set_display_switch_mode(SWITCH_BACKGROUND);
        set_display_switch_callback(SWITCH_IN,switchedToProgram);
        set_display_switch_callback(SWITCH_OUT,switchedFromProgram);
        show_mouse(screen);
    }
}

inline int is_custom_replay(Treplay *r)
{
    return r->floor_shrink != 1 || r->floor_size != 1 ||
           r->start_speed != 5 || r->speed_increase != 1 || r->gravity != 1;
}

extern void destroy_game_data(Tgame_data *gd);
extern Tgame_data *create_game_data(void);
extern void reset_player(Tplayer *p);
extern Treplay *create_replay(int size);

/* Recovered from the full 0x40dc9c..0x40e10f control-flow range.  The
 * candidate retains the original state transitions and API boundary; its
 * instruction layout remains under recovery. */
int new_game(void)
{
    int i;
    Tplayer *p;

    log2file(" init new game");
    collision_type = 2;
    new_srand(rand() % 0x18ff8);
    rec_pos = 0;
    cmdline.jumps = 0;
    cmdline.combos = 0;
    cmdline.sd = 0;
    cmdline.keys = 0;
    cmdline.tiny = 0;
    last_stripe_y = 0;

    if (!itrcheck) {
        floors.max = profile->best_floor / 100;
        if (floors.max > 9)
            floors.max = 9;
        floors.value = floors.max;
        if (floors.value > profile->start_floor)
            floors.value = profile->start_floor;
    }

    jumpSequence.start = 0;
    jumpSequence.dist = 0;
    jumpSequence.num = 0;
    gdLastJumpDiff = 0;
    if (gameData)
        destroy_game_data(gameData);
    gameData = create_game_data();
    if (!gameData) {
        log2file("*** failed to allocate memory for gameData, prepare for crash");
        return 0;
    }
    gameData->replay = demo;

    if (demo) {
        log2file(" preparing to show replay");
        recording = 0;
        rejump = demo->rejump;
        rec_seed = demo->random_seed;
        if (is_custom_replay(demo))
            gdLastJumpDiff = 1;
    } else {
        log2file(" setting up for replay recording");
        recording = 1;
        demo = create_replay(64000);
        if (!demo)
            return 0;
        strcpy(demo->name, profile->handle);
        if (itrcheck) {
            demo->floor_shrink = options.floor_shrink;
            demo->floor_size = options.floor_size;
            demo->start_speed = options.start_speed;
            demo->speed_increase = options.speed_increase;
            demo->gravity = options.gravity;
        } else {
            demo->floor_shrink = 1;
            demo->floor_size = 1;
            demo->start_speed = 5;
            demo->speed_increase = 1;
            demo->gravity = 1;
        }
        rejump = options.jump_hold;
        srand(time(0));
        rec_seed = rand();
        demo->random_seed = rec_seed;
    }

    scroll_count = 0;
    scroll_delay = 100;
    for (i = 0; i < 15; i++)
        new_personal_best[i] = 0;
    srand(rec_seed);
    log2file(" creating map layout");
    reset_map(&map);
    for (i = 0; i < 30; i++)
        add_floor(&map);
    p = ply[player_id];
    reset_player(p);
    p->x = 200.0;
    p->y = 431.0;
    p->status = 0;
    p->sx = 0.001;
    reward_time = 0;
    hurry_y = 480;
    if (itrcheck)
        return 1;

    reset_particles(stars);
    log2file(" loading custom character: %s", characters[curr_char].name);
    init_custom(&custom, characters[curr_char].name,
                characters[curr_char].uses_datafile);
    if (!load_frames(&custom))
        return 1;
    load_sounds(&custom);
    log2file(" cc done");
    if (got_joystick)
        ctrl.use_joy = 1;
    return 1;
}

int show_name(char *name, int attribs)
{
    allegro_message("Caught `%s', attribs %d\n", name, attribs);
    return 0;
}

void startMenuMusic(void)
{
    if (bg_menu)
        play_sample(bg_menu, options.msc_volume, 128, 1000, 1);
}

#ifndef ICYTOWER_SYNTHETIC_LINK
void play_sound(SAMPLE *s, int pitch, int please_pan)
{
    int pan;
    int pit;
    if (itrcheck) return;
    if (pitch) pit=new_rand()%300+925;
    else pit=1000;
    if (!s || !options.snd_volume) return;
    if (please_pan) {
        pan=(int)((float)(ply[player_id]->x/640.0f)*192.0f+32.0f);
        any11=pan;
    }
    else pan=128;
    if (fast_forward) pit<<=1;
    if (fast_fast_forward) pit<<=1;
    play_sample(s,options.snd_volume,pan,pit,0);
}
#else
void play_sound(SAMPLE *s, int pitch, int please_pan);
#endif

void play_menu_select(void)
{
    play_sound(menu_sounds[0], 0, 0);
}

void play_menu_move(void)
{
    play_sound(menu_sounds[1], 0, 0);
}

void stopMenuMusic(void)
{
    if (bg_menu)
        stop_sample(bg_menu);
}

void stopGameMusic(void)
{
    if (gameMusicVoiceID >= 0)
        voice_stop(gameMusicVoiceID);
    if (custom.bg_music)
        stop_sample(custom.bg_music);
    if (custom.bg_midi)
        stop_midi();
}

void startGameMusic(void)
{
    gameMusicVoiceID = -1;
    if (!options.msc_volume)
        return;
    if (custom.bg_music) {
        gameMusicVoiceID = play_sample(custom.bg_music, options.msc_volume,
                                       128, 1000, 1);
        return;
    }
    if (custom.bg_midi) {
        set_volume(-1, options.msc_volume);
        play_midi(custom.bg_midi, 1);
        return;
    }
    if (bg_beat)
        gameMusicVoiceID = play_sample(bg_beat, options.msc_volume,
                                       128, 1000, 1);
}

void replaceBadCharacters(char *string, char newChar)
{
    int i;
    char letters[63] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

    for (i = 0; i < (int)strlen(string); i++)
        if (!strchr(letters, string[i]))
            string[i] = newChar;
}

/* Oracle: main.c:2267, 0x40b6bc..0x40bc43.  Debug keys select the historical
 * presentation experiments; ordinary play always takes the direct path. */
int debug;
int blit_mode;

void blit_to_screen(BITMAP *bmp)
{
    if (debug) {
        if (key[56]) blit_mode = 0;
        if (key[57]) blit_mode = 1;
        if (key[58]) blit_mode = 2;
        if (key[59]) blit_mode = 3;
        if (key[60]) blit_mode = 4;
        if (key[61]) blit_mode = 5;
        if (key[62]) blit_mode = 6;
    }
    acquire_screen();
    switch (blit_mode) {
    case 1:
        draw_sprite_h_flip(screen, bmp, 0, 0);
        break;
    case 2:
        draw_sprite_v_flip(screen, bmp, 0, 0);
        break;
    case 5:
        stretch_blit(bmp, screen, 0, 0, bmp->w, bmp->h,
                     160, 120, 320, 240);
        break;
    default:
        blit(bmp, screen, 0, 0, 0, 0, bmp->w, bmp->h);
        break;
    }
    release_screen();
}

/* Partial source recovery of main.c:3405, 0x411a00..0x415e0c.  This retains
 * the oracle's real game-state ownership and phase order while the remaining
 * results/replay branches are being recovered instruction by instruction. */
extern void handle_player_input(void *control);
extern void update_player(Tplayer *p);
extern int jump_player(Tplayer *p, int force);
extern void play_jump_sound(Tplayer *p);

/* Partial recovery of main.c:2320, 0x4070fc..0x407341.  The two paths are
 * distinguished by the original eye-candy option: rectangular scaling for
 * flash mode 1 and fixed-point rotation/scaling for mode 0. */
void draw_reward(BITMAP *bmp)
{
    int w;
    int h;

    if (options.flash) {
        if (options.flash!=1)
            return;
        w=fixtoi(fixmul(itofix(reward_bmp->w),reward_scale));
        h=fixtoi(fixmul(itofix(reward_bmp->h),reward_scale));
        stretch_sprite(bmp,reward_bmp,360-w/2,320-h/2,w,h);
    }
    else {
        rotate_scaled_sprite(bmp,reward_bmp,
                             itofix(360)-fixmul(itofix(reward_bmp->w),reward_scale)/2,
                             itofix(320)-fixmul(itofix(reward_bmp->h),reward_scale)/2,
                             itofix(0),reward_scale);
    }
}

/* Partial recovery of main.c:5337, 0x4073f8..0x4076c0.  The replay menu
 * uses a striped datafile backdrop and overlays the optional summary scroll. */
void replay_menu_callback(void)
{
    int i;

    for (i=0; i<640; i+=2) {
        vline(swap_screen,i,0,480,0);
        hline(swap_screen,0,i,640,0);
    }
    draw_sprite(swap_screen,data[87].dat,120,140);
    if (!summary_scroller_message[0])
        return;
    scroll_scroller(&summary_scroller,-2);
    drawing_mode(DRAW_MODE_TRANS,0,0,0);
    set_trans_blender(0,0,0,110);
    rectfill(swap_screen,0,0,639,20,makecol(0,0,0));
    rectfill(swap_screen,0,0,639,18,makecol(0,0,0));
    rectfill(swap_screen,0,0,639,16,makecol(0,0,0));
    solid_mode();
    draw_scroller(&summary_scroller,swap_screen,1,0,makecol(150,150,150));
    if (!draw_scroller(&summary_scroller,swap_screen,0,0,makecol(200,200,200)))
        restart_scroller(&summary_scroller);
}

/* Initial source recovery of main.c:5474, 0x410f98..0x4119fd. */
int do_replay_menu(void)
{
    int ret = -1;
    int play_again = 0;
    int isGuest = !stricmp("guest",profile->handle);
    char filename[1024];

    log2file(" replay_menu launched");
    while (!closeButtonClicked && ret!='l') {
        ret=handle_menu(replay_menu,&menu_params,&ctrl,swap_screen,
                        replay_menu_callback,180,160,0);
        if (ret=='e') {
            log2file("  play again selected");
            play_again=1;
        }
        else if (ret=='|') {
            log2file("  view replay selected");
            fadeOut(16);
            sprintf(filename,"%slast_game.itr",replay_directory);
            run_demo(filename);
        }
        else if (ret=='{' && !isGuest)
            log2file("  save replay selected");
    }
    return play_again;
}

/* Partial recovery of main.c:3359, 0x4076c0..0x407a07.  This result panel
 * presents the score, floor, and best-combo categories and their markers. */
void draw_results(BITMAP *bmp, BITMAP *logo, int y, int *qualified,
                  int *qValues, int showQ)
{
    int categories[5] = { 0, 2, 1 };
    int numCats = 3;
    int padding = 30;
    int dist;
    int pos = 0;
    int i;

    draw_sprite(bmp,logo,320-logo->w/2,y);
    for (i=0; i<numCats; i++) {
        textprintf_ex(bmp,data[52].dat,200,y+logo->h+3+pos,-1,-1,"%s:",
                      result_categories[categories[i]]);
        textprintf_right_ex(bmp,data[52].dat,440,y+logo->h+3+pos,-1,-1,"%d",
                            qValues[categories[i]]);
        if (showQ) {
            if (new_personal_best[categories[i]]>0 &&
                stricmp(profile->handle,"guest")) {
                draw_sprite(bmp,data[69].dat,476,y+logo->h+13+pos);
                dist = 18;
            }
            else
                dist = -4;
            if (qualified[categories[i]]>0) {
                draw_sprite(bmp,data[68].dat,480+dist,y+logo->h+13+pos);
                textprintf_ex(bmp,data[53].dat,480+dist+7,y+logo->h+18+pos,
                              makecol(0,0,0),-1,"%d",qualified[categories[i]]);
            }
        }
        pos += padding;
    }
}

/* Partial recovery of main.c:5650, 0x40d454..0x40da56.  This mandatory
 * first-run flow captures the display, creates or loads a profile, and
 * returns with the profile list and remembered handle synchronized. */
void force_create_profile(void)
{
    BITMAP *bg;
    int ok;
    char y[128];
    char new_name[32];

    bg=create_bitmap(gfx_driver->w,gfx_driver->h);
    blit(screen,bg,0,0,0,0,gfx_driver->w,gfx_driver->h);
    memset(new_name,0,sizeof(new_name));
    for (;;) {
        checkMenuFocus();
        blit(bg,screen,0,0,0,0,gfx_driver->w,gfx_driver->h);
        set_trans_blender(0,0,0,158);
        drawing_mode(DRAW_MODE_TRANS,0,0,0);
        rectfill(screen,0,0,gfx_driver->w,gfx_driver->h,makecol(0,0,0));
        solid_mode();
        draw_sprite(screen,data[87].dat,100,120);
        textout_ex(screen,data[51].dat,"Welcome to Icy Tower",130,127,-1,-1);
        textout_ex(screen,data[54].dat,"Yo, wazup? In Icy Tower, all your highscores",130,160,0,-1);
        textout_ex(screen,data[54].dat,"and progress will be stored in a personal profile.",130,175,0,-1);
        textout_ex(screen,data[54].dat,"AWESOME!",130,190,0,-1);
        textout_ex(screen,data[54].dat,"Please enter a name for your profile:",130,220,0,-1);
        textout_right_ex(screen,data[54].dat,"...and press enter.",430,260,0,-1);
        rect(screen,129,240,430,258,makecol(255,255,255));
        rectfill(screen,129,240,430,258,makecol(80,80,80));
        blit_to_screen(screen);
        ok=get_string(screen,new_name,300,32,data[54].dat,130,240,makecol(0,0,0),-1);
        if (ok<0 || (ok>0 && !new_name[0]))
            continue;
        if (ok==0) {
            my_alert("You can create a profile later in the OPTIONS menu.","Oh Well...",0,1);
            profile=load_profile("guest");
            if (!profile)
                profile=create_profile("guest",1);
            syncOptionsFromProfile();
            break;
        }
        replaceBadCharacters(new_name,'_');
        profile=create_profile(new_name,0);
        if (!profile) {
            my_alert("That profile name is taken.","Ooops!",0,1);
            continue;
        }
        sprintf(y,"Welcome %s!",profile->handle);
        my_alert(y,"Your profile has been created!",0,1);
        break;
    }
    destroy_bitmap(bg);
    strcpy(options.lastProfile,profile->handle);
    rebuild_profile_list(0);
}

/* Partial recovery of main.c:2490, 0x40929c..0x40b3e4.  This keeps the
 * oracle's renderer phases in source: floor plane, animated character,
 * particles, rewards, advertising image, and score/status overlays. */
void draw_frame(BITMAP *dst)
{
    Tplayer *p;
    int x;
    int y;
    int fy;
    int fx1;
    int fx2;
    int frame;
    int color;

    clear_to_color(dst,makecol(10,16,28));
    for (y=0;y<32;y++) {
        if (map.room[y].empty!=0)
            continue;
        getFloorData(&map,(29-y)*16,&fy,&fx1,&fx2);
        color=makecol(70+(map.room[y].tiles*8),48,20);
        rectfill(dst,fx1,fy,fx2,fy+15,color);
        line(dst,fx1,fy,fx2,fy,makecol(210,170,90));
    }

    for (x=0;x<512;x++) {
        if (stars[x].intensity>0)
            putpixel(dst,(int)stars[x].x,(int)stars[x].y,stars[x].color);
    }
    p=ply[player_id];
    if (p) {
        frame=p->frame%15;
        if (frame<0) frame+=15;
        if (custom.frame[frame])
            draw_sprite(dst,custom.frame[frame],(int)p->x,(int)p->y);
        else
            rectfill(dst,(int)p->x,(int)p->y,(int)p->x+16,(int)p->y+32,
                     makecol(240,210,80));
        textprintf_ex(dst,data[53].dat,12,12,-1,-1,"SCORE %d",p->score);
        textprintf_right_ex(dst,data[53].dat,628,12,-1,-1,"FLOOR %d",p->level);
        if (p->in_combo)
            textprintf_centre_ex(dst,data[51].dat,320,38,makecol(255,220,80),-1,
                                 "%d COMBO",p->in_combo);
    }
    if (reward_bmp && reward_time>0)
        draw_reward(dst);
    if (pFLDAdBitmap)
        draw_sprite(dst,pFLDAdBitmap,540,400);
}

int play(void)
{
    int playing;
    int i;
    Tplayer *p;

    log2file("PLAY");
    update_frame();
    startGameMusic();
    playing = 1;
    while (playing && !closeButtonClicked) {
        cycle_count = 0;
        poll_control(&ctrl, 0);
        if (is_pause(&ctrl)) {
            clear_keybuf();
            while (is_pause(&ctrl) && !closeButtonClicked) {
                poll_control(&ctrl, 0);
                rest(2);
            }
            clear_keybuf();
        }

        p = ply[player_id];
        handle_player_input(&ctrl);
        update_player(p);
        for (i = 0; i < 512; i++)
            update_particle(&stars[i]);

        switch (collision_type) {
        case 0: handle_player_collision_vector_2((int)p->x, (int)p->y); break;
        case 1: handle_player_collision_vector((int)p->x, (int)p->y); break;
        case 2: handle_player_collision_old((int)p->x, (int)p->y); break;
        case 3: handle_player_collision_original((int)p->x, (int)p->y); break;
        default: handle_player_collision_combo((int)p->x, (int)p->y); break;
        }
        draw_frame(screen);
        blit_to_screen(screen);
        if (p->dead > 299)
            playing = 0;
        while (!cycle_count && !closeButtonClicked)
            rest(2);
    }
    if (profile)
        save_profile(profile);
    stopGameMusic();
    return 0;
}

/* Oracle: main.c:5367, 0x40bc44..0x40bf59.  The editor owns only its
 * temporary backing bitmap; callers retain the supplied string and screen. */
int get_string(BITMAP *bmp, char *string, int w, int max_chars, FONT *f,
               int pos_x, int pos_y, int colour, int bg_color)
{
    BITMAP *block;
    char letters[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    int i;
    int tick;
    int c;

    block = create_bitmap(w, text_height(f) + 2);
    if (!block)
        return -1;
    i = strlen(string);
    blit(bmp, block, pos_x - 1, pos_y - 1, 0, 0, block->w, block->h);
    while (key[KEY_LCONTROL] || key[KEY_RCONTROL])
        ;
    clear_keybuf();
    tick = 0;
    for (;;) {
        while (!cycle_count)
            rest(2);
        if (closeButtonClicked) {
            destroy_bitmap(block);
            return 0;
        }
        tick++;
        cycle_count = 0;
        checkMenuFocus();
        string[i] = (tick & 8) ? '|' : ' ';
        string[i + 1] = 0;
        vsync();
        blit(block, bmp, 0, 0, pos_x - 1, pos_y - 1, block->w, block->h);
        if (bg_color >= 0)
            rectfill(bmp, pos_x, pos_y, pos_x + block->w - 1,
                     pos_y + block->h - 3, bg_color);
        textout_ex(bmp, f, string, pos_x + 2, pos_y, colour, -1);
        blit_to_screen(bmp);
        if (!keypressed())
            continue;
        c = readkey();
        if ((c >> 8) == KEY_ESC) {
            string[i] = 0;
            destroy_bitmap(block);
            return -2;
        }
        if ((c >> 8) == KEY_ENTER) {
            string[i] = 0;
            destroy_bitmap(block);
            return 0;
        }
        if ((c >> 8) == KEY_BACKSPACE) {
            if (i)
                i--;
            continue;
        }
        if (i < max_chars - 2 && strchr(letters, c) &&
            text_length(f, string) < w - 9)
            string[i++] = (char)c;
    }
}

void pwd_garble_string(char *str, int key)
{
    int i;
    int len_i;

    len_i = strlen(str);
    for (i = 0; i < len_i; i++)
        str[i] ^= key - i;
}

int line_intersect(int ax, int ay, int bx, int by, int cx, int cy, int dx, int dy,
                   int *ix, int *iy)
{
    float r, s, denom;

    denom = (dy - cy) * (bx - ax) + (cx - dx) * (by - ay);
    r = ((dx - cx) * (ay - cy) + (cy - dy) * (ax - cx)) / denom;
    s = ((ay - cy) * (bx - ax) + (ay - by) * (ax - cx)) / denom;
    if (r < 0.0f || s < 0.0f || r > 1.0f || s > 1.0f)
        return 0;
    *ix = ax + (int)(r * (bx - ax) + 0.5);
    *iy = ay + (int)(r * (by - ay) + 0.5);
    return 1;
}

void draw_progress_bar(void)
{
    int size;
    int ypos;
    static int value;
    int maxVal;

    if (itrcheck)
        return;
    size=value*4;
    maxVal=212;
    if (size>maxVal)
        size=maxVal;
    acquire_screen();
    ypos=400;
    rectfill(screen,108,ypos,532,ypos+10,makecol(150,150,150));
    rectfill(screen,320-size,ypos,320+size,ypos+10,makecol(100,100,100));
    rectfill(screen,0,420,639,430,makecol(255,255,255));
    textout_centre_ex(screen,font,last_log,320,420,makecol(150,150,150),makecol(255,255,255));
    release_screen();
    value++;
}

void datafile_callback_slow(DATAFILE *d)
{
    static int p;

    if (!(p & 15))
        draw_progress_bar();
    p++;
}

void datafile_callback(DATAFILE *d)
{
    draw_progress_bar();
}

void color_map_callback(int pos)
{
    if (!(pos & 15))
        draw_progress_bar();
}

SAMPLE *getSampleFromOggDatafile(DATAFILE *df, int id)
{
    return logg_load_memory(df[id].dat, df[id].size);
}

void log2file(const char *format, ...)
{
    static pthread_mutex_t sLogMutex = PTHREAD_MUTEX_INITIALIZER;
    static char logfilename[1024];
    va_list ptr;
    PACKFILE *fp;
    if (itrcheck) return;
    pthread_mutex_lock(&sLogMutex);
    if (!logfilename[0]) get_logfile_path(logfilename, sizeof(logfilename));
    fp = fopen(logfilename, "at");
    if (fp) {
        va_start(ptr, format);
        vfprintf(fp, format, ptr);
        vsprintf(allegro_error, format, ptr);
        fputc('\n', fp);
        fclose(fp);
    }
    pthread_mutex_unlock(&sLogMutex);
}

void end_game(void)
{
    log2file(" freeing custom data");
    destroy_custom_data(&custom);
}

void uninit_game(void)
{
    int i;

    log2file("\nUNINIT");
    if (init_ok) {
        log2file("Saving config");
        save_config();
        log2file("Saving profile '%s'",profile->handle);
        syncProfileFromOptions();
        save_profile(profile);
    }
    if (testers)
        destroy_all(testers);
    log2file("Freeing sound memory");
    for (i=0;i<10;i++)
        if (combo_sound[i]) destroy_sample(combo_sound[i]);
    for (i=0;i<3;i++)
        if (jump_sound[i]) destroy_sample(jump_sound[i]);
    for (i=0;i<3;i++)
        if (speaker[i]) destroy_sample(speaker[i]);
    if (menu_sounds[0]) destroy_sample(menu_sounds[0]);
    if (menu_sounds[1]) destroy_sample(menu_sounds[1]);
    for (i=0;i<9;i++)
        if (sounds[i]) destroy_sample(sounds[i]);
    if (bg_beat) destroy_sample(bg_beat);
    if (bg_menu) destroy_sample(bg_menu);
    log2file("Freeing custom character memory");
    for (i=0;i<num_chars;i++)
        if (characters[i].bmp) destroy_bitmap(characters[i].bmp);
    free(characters);
    log2file("Unloading datafile");
    if (data) unload_datafile(data);
    log2file("Free buffer memory");
    if (swap_screen) destroy_bitmap(swap_screen);
    log2file("Free highscore tables");
    for (i=0;i<15;i++)
        if (hisc_tables[i]) destroy_hisc_table(hisc_tables[i]);
    log2file("Free player");
    if (ply[player_id]) free(ply[player_id]);
    set_gfx_mode(GFX_TEXT,0,0,0,0);
    log2file("Exiting Allegro");
    allegro_exit();
}

#ifndef ICYTOWER_SYNTHETIC_LINK
void save_config(void)
{
    FILE *fp;
    char cfgfilename[256];

    log2file("  saving config and scores");
    get_configfile_path(cfgfilename, sizeof(cfgfilename));
    fp = pack_fopen(cfgfilename, "wp");
    if (fp) {
        int i;
        save_options(&options, fp);
        for (i = 0; i < 15; i++)
            save_hisc_table(hisc_tables[i], fp);
        pack_fclose(fp);
    } else {
        log2file("    *** failed");
    }
}

void change_profile(void)
{
    Tprofile *newProfile;

    if (profile) {
        syncProfileFromOptions();
        save_profile(profile);
    }
    newProfile = select_profile(profile, profiles, numProfiles, &ctrl);
    if (newProfile) {
        if (profile) free(profile);
        profile = newProfile;
        strcpy(options.lastProfile, profile->handle);
        syncOptionsFromProfile();
        save_config();
        rebuild_profile_list(0);
    }
}

#endif

inline void update_reward(void)
{
    if (reward_time > 60)
        reward_scale += 3277;
    else if (reward_time <= 9)
        reward_scale -= 6554;
    reward_time--;
}

void myDeleteFile(char *path, char *file)
{
    char buf[2048];
    sprintf(buf, "%s%s", path, file);
    delete_file(buf);
}

void set_current_avatar(void)
{
    int i;
    for (i=0; i<num_chars; i++) {
        if (!stricmp(characters[i].name, ((Tavatar_profile *)profile)->avatar)) {
            curr_char=i;
            play_char=i;
        }
    }
}

#ifndef ICYTOWER_SYNTHETIC_LINK
void update_frame(void)
{
    Tplayer *p;
    if (reward_time) {
        if (reward_time>60)
            reward_scale+=3277;
        else if (reward_time<=9)
            reward_scale-=6554;
        reward_time--;
    }
    p=ply[player_id];
    if (p->dead && p->dead<=299)
        p->dead+=8;
    else {
        if (p->edge)
            p->edge_drawn++;
        if (logic_count%10==0)
            p->frame++;
    }
}
#endif

void checkMenuFocus(void)
{
    if (in_replay_menu)
        return;
    if (lastFocus==hasFocus)
        return;
    if (hasFocus)
        startMenuMusic();
    else
        stopMenuMusic();
    lastFocus=hasFocus;
}

int check_dir(char *filename, int attrib, void *param)
{
    char name[1024];
    char *n=get_filename(filename);
    log2file(filename);
    if ((attrib & FA_DIREC) && *n!='.') {
        sprintf(name, "%s/%s.txt", filename, n);
        if (exists(name))
            num_chars++;
    }
    return 0;
}

void for_each_directory(char *basedir,
                        int (*cb)(const char *filename, int attrib, void *param))
{
    char dir_and_wildcard[256];
    strncpy(dir_and_wildcard, basedir, sizeof(dir_and_wildcard));
    strcat(dir_and_wildcard, "*");
    for_each_file_ex(dir_and_wildcard, FA_DIREC, 0, cb, NULL);
}

#ifndef ICYTOWER_SYNTHETIC_LINK
void play_jump_sound(Tplayer *p)
{
    if (p->sy < -22.0f)
        play_sound(custom.jump_sound[2], 1, 1);
    else if (p->sy < -15.0f)
        play_sound(custom.jump_sound[1], 1, 1);
    else
        play_sound(custom.jump_sound[0], 1, 1);
}
#endif

#ifndef ICYTOWER_SYNTHETIC_LINK
void run_demo(char *file_name)
{
    int fo;

    if (file_name) {
        if (demo)
            destroy_replay(demo);
        demo = load_replay(file_name);
    }
    if (demo) {
        if (!itrcheck) {
            fo = profile->start_floor;
            profile->start_floor = 0;
        }
        else
            fo = 0;
        if (new_game()) {
            play();
            end_game();
        }
        if (!itrcheck) {
            profile->start_floor = fo;
            floors.value = fo;
        }
    }
}

#endif

int add_profile(const char *filename, int attrib, void *param)
{
    char buf[1024];
    char *file;

    file = get_filename(filename);
    if (*file != '.') {
        get_profile_dir_for_profile(buf, sizeof(buf), file);
        sprintf(buf, "%s%s", buf, file);
        if (exists(buf)) {
            numProfiles++;
            if (profiles)
                profiles = realloc(profiles, numProfiles * sizeof(*profiles));
            else
                profiles = malloc(sizeof(*profiles));
            strcpy(profiles[numProfiles - 1].handle, file);
        }
    }
    return 0;
}

int rebuild_profile_list(Tavailable_profile **profs)
{
    char profiledir[1024];

    if (profiles) {
        free(profiles);
        profiles = NULL;
    }
    profiles = malloc(sizeof(*profiles));
    strcpy(profiles[0].handle, "CREATE NEW PROFILE");
    numProfiles = 1;
    get_profiles_dir(profiledir, sizeof(profiledir));
    strcat(profiledir, "/*");
    for_each_file_ex(profiledir, FA_DIREC, 0, add_profile, NULL);
    if (profs)
        *profs = profiles;
    return numProfiles;
}

#ifndef ICYTOWER_SYNTHETIC_LINK
BITMAP *loadScrambled(char *fileName)
{
    int fileSize;
    char *data;
    FILE *fp;
    char *password;
    int pLen;
    int i;
    int j;
    char *newFile;
    PALETTE pal;
    BITMAP *png;

    fileSize = file_size_ex(fileName);
    data = malloc(fileSize);
    if (!data)
        return NULL;
    fp = fopen(fileName, "rb");
    if (!fp)
        return NULL;
    fread(data, fileSize, 1, fp);
    fclose(fp);
    password = "%2hJd8#9NsM/";
    pLen = strlen(password);
    for (i = 0; i < fileSize; i += pLen)
        for (j = 0; j < pLen; j++)
            data[i + j] ^= password[j];
    newFile = "data/com/temp.dat";
    fp = fopen(newFile, "wb");
    if (!fp)
        return NULL;
    fwrite(data, fileSize, 1, fp);
    fclose(fp);
    png = load_png(newFile, pal);
    delete_file(newFile);
    return png;
}

#endif

#ifndef ICYTOWER_SYNTHETIC_LINK
int check_beta_tester(void)
{
    int i;
    Tbeta *b;
    FILE *fp;
    char pwd[16] = "12345678\0";

    fp = fopen("password.txt", "rt");
    if (!fp) {
        allegro_message("password.txt not found");
        return 0;
    }
    fread(pwd, 8, 1, fp);
    fclose(fp);
    garble_string(pwd, 8);
    b = testers;
    the_tester = NULL;
    while (b) {
        if (!strncmp(pwd, b->code, 8))
            the_tester = b;
        b = b->next;
    }
    if (the_tester)
        return 1;
    log2file("no tester match found");
    return 0;
}

#endif

int check_characters(void)
{
    int i;
    char base_char_dir[256];
    size_t base_char_dir_len;
    char additional_char_dir[256];
    int has_additional_char_dir;

    getcwd(base_char_dir, sizeof(base_char_dir));
    base_char_dir_len = strlen(base_char_dir);
    strcpy(base_char_dir + base_char_dir_len, "/characters/");
    has_additional_char_dir = get_custom_characters_dir(
        additional_char_dir, sizeof(additional_char_dir));
    log2file("Searching '%s'", base_char_dir);
    for_each_directory(base_char_dir, check_dir);
    if (has_additional_char_dir) {
        log2file("Searching '%s'", additional_char_dir);
        for_each_directory(additional_char_dir, check_dir);
    }
    if (!num_chars)
        return 0;
    characters = malloc(num_chars * sizeof(*characters));
    for_each_directory(base_char_dir, load_character);
    if (has_additional_char_dir)
        for_each_directory(additional_char_dir, load_character);
    if (!num_chars)
        return 0;
    curr_char = num_chars - 1;
    for (i = 0; i < num_chars; i++)
        characters[i].ok = characters[i].bmp != NULL;
    set_current_avatar();
    return 1;
}

int load_character(const char *filename, int attrib, void *param)
{
    char *name;

    name = get_filename(filename);
    if ((attrib & FA_DIREC) && *name != '.') {
        char buf[1024];

        sprintf(buf, "%s/%s.txt", filename, name);
        if (exists(buf)) {
            characters[count].bmp = load_character_bmp(name,
                &characters[count].uses_datafile, characters[count].pal);
            log2file(" %s (%s): %s", name, filename,
                characters[count].bmp ? "ok" : "error");
            if (characters[count].bmp) {
                strcpy(characters[count].name, name);
                count++;
                return 0;
            }
            else {
                num_chars--;
                *allegro_errno = 0;
            }
        }
    }
    return 0;
}

void drawSlot(BITMAP *dst, int x, int y, char *title, char *text, int color)
{
    textout_ex(dst, data[54].dat, title, x, y - 16, makecol(0, 0, 0), -1);
    rectfill(dst, x - 1, y - 1, x + 340, y + 18, makecol(255, 255, 255));
    rect(dst, x - 1, y - 1, x + 340, y + 18, makecol(80, 80, 80));
    textout_ex(dst, data[54].dat, text, x + 2, y, color, -1);
}

int start_reward(int lev)
{
    int r;
    int i, p;

    reward_time = 80;
    reward_scale = 0;
    if (lev <= 6) r = 0;
    else if (lev <= 14) r = 1;
    else if (lev <= 24) r = 2;
    else if (lev <= 34) r = 3;
    else if (lev <= 49) r = 4;
    else if (lev <= 69) r = 5;
    else if (lev <= 99) r = 6;
    else if (lev <= 139) r = 7;
    else if (lev > 199) r = 9;
    else r = 8;
    if (!itrcheck) {
        if (!options.flash && r > 2) {
            for (i = 0; i < (r - 2) * 16; i++) {
                p = create_particle(stars, 320, 360);
                stars[p].sy = (((new_rand() % 500) + 500) << 16) / 100;
                stars[p].sx = ((((new_rand() % 1000) - 500) << 16) * (r - 2)) / 100;
            }
        }
        reward_bmp = data[90 + r].dat;
    }
    play_sound(combo_sound[r], 0, 0);
    return r;
}

void handle_player_collision_original(int lastX, int lastY)
{
    int solid1;
    int solid2;

    solid1=is_solid(&map,(int)ply[player_id]->x-11,(int)ply[player_id]->y);
    solid2=is_solid(&map,(int)ply[player_id]->x+11,(int)ply[player_id]->y);
    any11=solid1;
    any12=solid2;
    any23=0;
    any22=0;
    any21=0;
    if (solid1+solid2==0) {
        if (ply[player_id]->status==2 || ply[player_id]->status==0)
            ply[player_id]->status=3;
        return;
    }
    if (ply[player_id]->status==1) return;
    if (ply[player_id]->status==2) return;
    if (ply[player_id]->status)
        play_sound(combo_sound[0],1,1);
    ply[player_id]->status=0;
    ply[player_id]->sy=0;
    if (solid1) {
        ply[player_id]->y-=solid1-9999;
        ply[player_id]->rotate=0;
        if (solid1==solid2) {
            ply[player_id]->edge=0;
            return;
        }
        ply[player_id]->edge=1;
        return;
    }
    if (solid2) {
        ply[player_id]->y-=solid2-9999;
        ply[player_id]->rotate=0;
        ply[player_id]->edge=2;
        return;
    }
    ply[player_id]->rotate=0;
    ply[player_id]->edge=0;
}

/* Oracle: main.c, 0x407fd8..0x408358.  The legacy mode first tests the
 * current feet, then sweeps a midpoint when the player moved downward. */
void handle_player_collision_old(int lastX, int lastY)
{
    Tplayer *p;
    int x, y, dx, dy;
    int solid1, solid2;

    p = ply[player_id];
    x = (int)p->x;
    y = (int)p->y;
    dx = lastX - x;
    if (dx < 0) dx = -dx;
    dy = lastY - y;
    if (dy < 0) dy = -dy;
    if ((int)p->x < lastX) x = lastX - dx / 2;
    else x = lastX + dx / 2;
    if ((int)p->y < lastY) y = lastY - dy / 2;
    else y = lastY + dy / 2;

    solid1 = is_solid(&map, (int)p->x - 11, (int)p->y);
    solid2 = is_solid(&map, (int)p->x + 11, (int)p->y);
    any11 = solid1;
    any12 = solid2;
    any23 = 0;
    any22 = 0;
    any21 = 0;
    if (solid1 + solid2 == 0) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
        if (y <= lastY)
            return;
        goto sweep;
    }

resolve:
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
    if (solid2) {
        p->y -= solid2 - 9999;
        p->rotate = 0;
        p->edge = 2;
        return;
    }
    p->rotate = 0;
    p->edge = 0;
    return;

sweep:
    solid1 = is_solid(&map, x - 11, y);
    solid2 = is_solid(&map, x + 11, y);
    any21 = solid1;
    any22 = solid2;
    if (solid1 + solid2 == 0) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
        return;
    }
    if (p->status == 1 || p->status == 2)
        return;
    any23 = 1;
    goto resolve;
}

/* Partial recovery of main.c, 0x408d08..0x409137.  The normal path is the
 * oracle's floor-segment intersection; its collision-debug line drawing is
 * intentionally left for the presentation recovery pass. */
void handle_player_collision_vector(int lastX, int lastY)
{
    Tplayer *p;
    int floor_y = -12345678;
    int floor_x1 = 0, floor_x2 = 0;
    int left_x, left_y, right_x, right_y;
    int left, right;
    int current_x, current_y;

    p = ply[player_id];
    current_x = (int)p->x;
    current_y = (int)p->y;
    getFloorData(&map, current_y, &floor_y, &floor_x1, &floor_x2);
    if (floor_y == -12345678) {
        getFloorData(&map, lastY, &floor_y, &floor_x1, &floor_x2);
        if (floor_y == -12345678) {
            if (p->status == 2 || p->status == 0)
                p->status = 3;
            return;
        }
    }

    left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        lastX - 11, lastY, current_x - 11, current_y + 1, &left_x, &left_y);
    right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        lastX + 11, lastY, current_x + 11, current_y + 1, &right_x, &right_y);
    if (!left && !right) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
        return;
    }
    p->edge = left == right ? 0 : (left ? 1 : 2);
    if (p->status != 2 && p->status != 3)
        return;
    if (left && right &&
        (left_x < -10000 || right_x < -10000 || left_x > 10000 || right_x > 10000))
        return;

    play_sound(combo_sound[0], 1, 1);
    p->status = 0;
    p->sx = 0;
    p->sy = 0;
    p->y = floor_y - 1;
    p->x = left ? left_x + 11 : right_x - 11;
    p->rotate = 0;
}

/* Partial recovery of main.c, 0x4088c8..0x408d08.  This variant retries the
 * floor segment four pixels lower before transitioning to falling state. */
void handle_player_collision_vector_2(int lastX, int lastY)
{
    Tplayer *p;
    int floor_y = -12345678;
    int floor_x1 = 0, floor_x2 = 0;
    int left_x, left_y, right_x, right_y;
    int left, right;
    int current_x, current_y;

    p = ply[player_id];
    current_x = (int)p->x;
    current_y = (int)p->y + 1;
    getFloorData(&map, (int)p->y, &floor_y, &floor_x1, &floor_x2);
    if (floor_y == -12345678) {
        getFloorData(&map, lastY, &floor_y, &floor_x1, &floor_x2);
        if (floor_y == -12345678) {
            floor_y = 0;
            floor_x1 = 0;
            floor_x2 = 0;
        }
    }

    left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        (int)p->x - 11, current_y, lastX - 11, lastY, &left_x, &left_y);
    right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        (int)p->x + 11, current_y, lastX + 11, lastY, &right_x, &right_y);
    if (!left && !right) {
        floor_y += 4;
        left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
            (int)p->x - 11, current_y, lastX - 11, lastY, &left_x, &left_y);
        right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
            (int)p->x + 11, current_y, lastX + 11, lastY, &right_x, &right_y);
    }
    if (!left && !right) {
        if (p->status == 2 || p->status == 0)
            p->status = 3;
        p->edge = 0;
        return;
    }
    p->edge = left == right ? 0 : (left ? 1 : 2);
    if (p->status != 2 && p->status != 3)
        return;

    play_sound(combo_sound[0], 1, 1);
    p->status = 0;
    p->sx = 0;
    p->sy = 0;
    p->y = floor_y - 1;
    p->x = left ? left_x + 11 : right_x - 11;
    p->rotate = 0;
}

/* Partial recovery of main.c, 0x408358..0x4088c8.  Combo mode uses ordinary
 * solid-foot correction first, then a floor-segment landing intersection. */
void handle_player_collision_combo(int lastX, int lastY)
{
    Tplayer *p;
    int floor_y = -12345678;
    int floor_x1 = 0, floor_x2 = 0;
    int left_x, left_y, right_x, right_y;
    int solid1, solid2, left, right;

    p = ply[player_id];
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
    getFloorData(&map, (int)p->y, &floor_y, &floor_x1, &floor_x2);
    if (floor_y == -12345678) {
        getFloorData(&map, lastY, &floor_y, &floor_x1, &floor_x2);
        if (floor_y == -12345678) {
            floor_y = 0;
            floor_x1 = 0;
            floor_x2 = 0;
        }
    }
    left = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        (int)p->x - 11, (int)p->y + 1, lastX - 11, lastY, &left_x, &left_y);
    right = line_intersect(floor_x1, floor_y, floor_x2, floor_y,
        (int)p->x + 11, (int)p->y + 1, lastX + 11, lastY, &right_x, &right_y);
    if (!left && !right) {
        p->edge = 0;
        return;
    }
    p->edge = left == right ? 0 : (left ? 1 : 2);
    if (p->status != 2 && p->status != 3)
        return;

    play_sound(combo_sound[0], 1, 1);
    p->status = 0;
    p->sx = 0;
    p->sy = 0;
    p->y = floor_y - 1;
    p->x = left ? left_x + 11 : right_x - 11;
    p->rotate = 0;
}

/* Partial recovery of main.c, 0x40b3e4..0x40b6bc.  This is the oracle's
 * normal-control path; replay control recording remains to be restored. */
void handle_player_input(void *control)
{
    Tcontrol *input = (Tcontrol *)control;
    Tplayer *p;

    if (!input)
        return;
    p = ply[player_id];
    if (is_left(input)) {
        if (p->sx < 0.0)
            p->sx *= 0.8;
        p->sx -= 0.1;
    }
    else if (is_right(input)) {
        if (p->sx > 0.0)
            p->sx *= 0.8;
        p->sx += 0.1;
    }
    else
        p->sx *= 0.9;

    if (is_fire(input)) {
        if (!p->jump_key && jump_player(p, 0)) {
            p->jump_key = -1;
            play_jump_sound(p);
        }
        return;
    }
    p->jump_key = 0;
}

/* Partial recovery of main.c:1375, 0x40e7dc..0x40fe78.  The oracle starts
 * with packfile/network state, command-line processing, and the platform
 * subsystems before it exposes the datafile-backed game globals. */
int init_game(int argc, char **argv)
{
    int i;

    log2file("INIT GAME");
    packfile_password(NULL);
    init_ok=0;
    closeButtonClicked=0;
    in_replay_menu=0;
    hasFocus=1;
    lastFocus=1;
    memset(&cmdline,0,sizeof(cmdline));
    for (i=1;i<argc;i++) {
        if (!stricmp(argv[i],"-windowed")) options.full_screen=0;
        else if (!stricmp(argv[i],"-fullscreen")) options.full_screen=1;
        else if (!stricmp(argv[i],"-replay")) cmdline.jumps=1;
    }

    if (allegro_init()!=0) return 0;
    set_color_depth(32);
    if (set_gfx_mode(options.full_screen ? GFX_AUTODETECT_FULLSCREEN :
                     GFX_AUTODETECT_WINDOWED,640,480,0,0)!=0)
        return 0;
    if (install_timers()!=0) return 0;
    if (install_keyboard()!=0) return 0;
    install_mouse();
    got_joystick=(install_joystick(JOY_TYPE_AUTODETECT)==0);
    install_sound(DIGI_AUTODETECT,MIDI_AUTODETECT,NULL);
    init_control(&ctrl);

    packfile_password("CHEESE");
    data=load_datafile("data/data.dat");
    if (!data) return 0;
    swap_screen=create_bitmap(SCREEN_W,SCREEN_H);
    if (!swap_screen) {
        unload_datafile(data);
        data=NULL;
        return 0;
    }
    init_ok=1;
    return 1;
}

/* Partial recovery of main.c:5761, 0x415f10..0x4166a2.  This preserves the
 * oracle's initialization/game/teardown lifecycle while menu dispatch is
 * recovered from its source-line branches. */
int _mangled_main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    log2file("INIT");
    if (!init_game(argc,argv)) {
        log2file("Initialization failed");
        uninit_game();
        return 1;
    }
    startMenuMusic();
    clear_keybuf();
    if (new_game()) {
        play();
        end_game();
    }
    stopMenuMusic();
    uninit_game();
    return 0;
}

#ifndef ICYTOWER_SYNTHETIC_LINK
END_OF_MAIN()
#endif
