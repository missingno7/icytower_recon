/* Partial historical main.c recovery. Other original entities remain absent. */
#include <stdio.h>
#include <stdarg.h>
#include <pthread.h>
#include <allegro.h>
#include "control.h"
#include "directories.h"
#include "game_services.h"

/* This exported extension belongs to the separately reconstructed logg CU. */
SAMPLE *logg_load_memory(void *pData, size_t iSize);

/* Declared at original line 92; log2file suppresses output while it is set. */
int itrcheck;
double seed;
int hasFocus;
int closeButtonClicked;

typedef struct Treplay {
    unsigned char reserved[140];
    int floor_shrink;
    int floor_size;
    int start_speed;
    int speed_increase;
    int gravity;
} Treplay;
Treplay *demo;
Tcontrol ctrl;

typedef struct Toptions {
    int flash;
    unsigned char reserved0[4];
    int jump_hold;
    unsigned char reserved1[24];
    int msc_volume;
    int snd_volume;
} Toptions;

typedef struct Tprofile {
    unsigned char reserved0[1244];
    int flash;
    int jump_hold;
    unsigned char reserved1[68];
    int msc_volume;
    int snd_volume;
} Tprofile;

Toptions options;
Tprofile *profile;
SAMPLE *bg_menu;
SAMPLE *menu_sounds[2];

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

void new_srand(int s)
{
    seed=s;
}

void syncProfileFromOptions(void)
{
    profile->msc_volume = options.msc_volume;
    profile->snd_volume = options.snd_volume;
    profile->jump_hold = options.jump_hold;
    profile->flash = options.flash;
}

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

int is_custom_replay(Treplay *r)
{
    return r->floor_shrink != 1 || r->floor_size != 1 ||
           r->start_speed != 5 || r->speed_increase != 1 || r->gravity != 1;
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

void play_sound(SAMPLE *sound, int randomized, int panned);

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

void draw_progress_bar(void);

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
    FILE *fp;
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
