/* Partial historical main.c recovery. Other original entities remain absent. */
#include <stdio.h>
#include <stdarg.h>
#include <pthread.h>
#include <allegro.h>
#include "control.h"
#include "custom.h"
#include "directories.h"
#include "game_services.h"
#include "timer.h"

/* This exported extension belongs to the separately reconstructed logg CU. */
SAMPLE *logg_load_memory(void *pData, size_t iSize);

/* Declared at original line 92; log2file suppresses output while it is set. */
int itrcheck;
double seed;
int hasFocus;
int closeButtonClicked;
int lastFocus;
int in_replay_menu;

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

typedef struct Tavatar_profile {
    unsigned char reserved[0x4e4];
    char avatar[1];
} Tavatar_profile;

typedef struct Tcharacter {
    unsigned char reserved0[0x408];
    char name[1];
    unsigned char reserved1[0x88c-0x409];
} Tcharacter;

typedef struct Tplayer {
    double x;
    double y;
    double sx;
    double sy;
    unsigned char reserved1[0x1c];
    int frame;
    unsigned char reserved2[0x0c];
    int dead;
    unsigned char reserved3[0x08];
    int edge;
    int edge_drawn;
} Tplayer;

Toptions options;
Tprofile *profile;
SAMPLE *bg_menu;
SAMPLE *menu_sounds[2];
Tcustom custom;
int reward_time;
fixed reward_scale;
int num_chars;
Tcharacter *characters;
int curr_char;
int play_char;
Tplayer *ply[1000];
int player_id;
int any11;
int fast_forward;
int fast_fast_forward;
int gameMusicVoiceID;
SAMPLE *bg_beat;

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

void end_game(void)
{
    log2file(" freeing custom data");
    destroy_custom_data(&custom);
}

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

/* DWARF signature for the remaining historical main body. */
int _mangled_main(int argc, char **argv);

#ifndef ICYTOWER_SYNTHETIC_LINK
END_OF_MAIN()
#endif
