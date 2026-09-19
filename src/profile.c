/* Historical CU: F:\projects\icytower\trunk\source\profile.c
 * Ownership: GAME
 * Source recovery pending. This file intentionally defines no fallback code.
 * EXACT: hash2 @ 0x004189cc, 71 bytes
 * DIFFER: generate_profile_checksum @ 0x00418a14, 112 bytes
 * DIFFER: get_rank_id @ 0x00418a84, 75 bytes
 * DIFFER: get_rank @ 0x00418ad0, 82 bytes
 * DIFFER: set_next_rank_message @ 0x00418b24, 431 bytes
 * UNKNOWN: draw_profile_selector @ 0x00418cd4, 1268 bytes
 * DIFFER: draw_buffer @ 0x004191c8, 185 bytes
 * DIFFER: profile_data_page_advanced @ 0x00419284, 332 bytes
 * EXACT: profile_data_page_basic @ 0x004193d0, 637 bytes
 * EXACT: profile_data_page_extra @ 0x00419650, 85 bytes
 * UNKNOWN: profile_data_page_general @ 0x004196a8, 1091 bytes
 * UNKNOWN: view_profile @ 0x00419aec, 2249 bytes
 * UNKNOWN: save_profile @ 0x0041a3b8, 1073 bytes
 * DIFFER: load_profile @ 0x0041a7ec, 188 bytes
 * CODEGEN_SIMILAR: delete_profile @ 0x0041a8a8, 222 bytes
 * DIFFER: create_profile @ 0x0041a988, 823 bytes
 * UNKNOWN: select_profile @ 0x0041acc0, 3070 bytes
 */

unsigned int hash2(unsigned int a)
{
    a = (a ^ 0x3dU) ^ (a >> 16);
    a *= 9U;
    a ^= a >> 4;
    a *= 668265261U;
    a ^= a >> 15;
    return a;
}
typedef struct Tprofile_rank {
    unsigned char before_score[0x4c];
    int score;
    int combo;
    unsigned char before_ccc[4];
    int ccc;
    unsigned char before_nml[0x2c];
    int no_combo_lost;
} Tprofile_rank;

extern int rankFloors[16];
extern int rankCombos[16];
extern int rankCCCs[16];
extern int rankNMLs[16];
extern char *rankLables[16];

inline int get_rank_id(Tprofile_rank *profile)
{
    int i;

    for (i = 11; i >= 0; i--) {
        if (profile->score < rankFloors[i]) continue;
        if (profile->combo < rankCombos[i]) continue;
        if (profile->ccc < rankCCCs[i]) continue;
        if (profile->no_combo_lost < rankNMLs[i]) continue;
        return i;
    }
    return 0;
}
inline char *get_rank(Tprofile_rank *profile)
{
    return rankLables[get_rank_id(profile)];
}
typedef struct Tprofile_checksum {
    unsigned char before_checksum[0x28];
    int checksum;
    unsigned char remainder[0x554 - 0x2c];
} Tprofile_checksum;

int generate_profile_checksum(Tprofile_checksum *p)
{
    int i, cs;
    int oldCS;
    int *pos;

    oldCS = p->checksum;
    pos = (int *)p;
    p->checksum = 0;
    cs = 0;
    for (i = 0; i < 0x154; i++) {
        cs += *pos * (i + 1);
        pos++;
    }
    p->checksum = oldCS;
    return hash2(cs);
}

typedef struct Tprofile_extra {
    unsigned char before_total_jumps[0xd8];
    int total_jumps;
} Tprofile_extra;

char *profile_data_page_extra(Tprofile_extra *p)
{
    char *data;

    data = malloc(2048);
    data[0] = 0;
    sprintf(data, "%sTotal jumps:    %d\n", data, p->total_jumps);
    sprintf(data, "%s\n", data);
    return data;
}

typedef struct Tprofile_basic {
    unsigned char before_games_played[0x2c];
    int games_played;
    unsigned char before_total_floors[0xc];
    int total_floors;
    int total_score;
    int total_combos;
    int total_combo_floors;
    int best_floor;
    int best_combo;
    int best_score;
    int no_combo_top_floor;
    int biggest_lost_combo;
    unsigned char before_jc[0x3c];
    int jc[5];
} Tprofile_basic;

extern char *jcLabels[5];

char *profile_data_page_basic(Tprofile_basic *p)
{
    char *data;
    int i;

    data = malloc(2048);
    data[0] = 0;
    sprintf(data, "%sBest score ever:    %7d\n", data, p->best_score);
    if (p->games_played > 0)
        sprintf(data, "%sAvg score per game: %7d\n", data,
                p->total_score / p->games_played);
    sprintf(data, "%sTotal score:        %7d\n", data, p->total_score);
    sprintf(data, "%s\n", data);
    sprintf(data, "%sHighest floor ever: %7d\n", data, p->best_floor);
    if (p->games_played > 0)
        sprintf(data, "%sAvg floors per game:%7d\n", data,
                p->total_floors / p->games_played);
    sprintf(data, "%sFloors jumped:      %7d\n", data, p->total_floors);
    sprintf(data, "%s\n", data);
    if (p->no_combo_top_floor) {
        sprintf(data, "%sTop Floor, No Combo:%7d\n", data,
                p->no_combo_top_floor);
        sprintf(data, "%s\n", data);
    }
    sprintf(data, "%sBest combo ever:    %7d\n", data, p->best_combo);
    if (p->games_played > 0)
        sprintf(data, "%sAvg combos per game:%7d\n", data,
                p->total_combos / p->games_played);
    if (p->total_combos > 0)
        sprintf(data, "%sAvg combo length:   %7d\n", data,
                p->total_combo_floors / p->total_combos);
    sprintf(data, "%sCombos jumped:      %7d\n", data, p->total_combos);
    sprintf(data, "%s\n", data);
    if (p->biggest_lost_combo > 0) {
        sprintf(data, "%sLongest Lost Combo: %7d\n", data,
                p->biggest_lost_combo);
        sprintf(data, "%s\n", data);
    }
    for (i = 0; i < 5; i++)
        if (p->jc[i] > 0)
            sprintf(data, "%s%s%7d\n", data, jcLabels[i], p->jc[i]);
    if (p->jc[0] + p->jc[1] + p->jc[2] + p->jc[3] + p->jc[4] > 0)
        sprintf(data, "%s\n", data);
    return data;
}
typedef struct Tprofile_advanced {
    unsigned char before_ccc_num[0x60];
    int cccNum[5];
    int cccTotal[5];
    int ccc[5];
    int jc[5];
    int rewards[10];
} Tprofile_advanced;

extern char *comboNames[10];

char *profile_data_page_advanced(Tprofile_advanced *p)
{
    char *data;
    int i;
    int rows;

    data = malloc(2048);
    data[0] = 0;
    for (i = 1; i < 6; i++)
        if (p->ccc[i - 1] > 0)
            sprintf(data, "%sClock Challenge %d:  %7d\n", data, i,
                    p->ccc[i - 1]);
    if (p->ccc[0] > 0)
        sprintf(data, "%s\n", data);
    for (i = 1; i < 6; i++)
        if (p->ccc[i - 1] > 0 && p->cccNum[i - 1] > 0)
            sprintf(data, "%sAverage CC %d:       %7d\n", data, i,
                    p->cccTotal[i - 1] / p->cccNum[i - 1]);
    if (p->cccTotal[0] > 0)
        sprintf(data, "%s\n", data);
    rows = 0;
    for (i = 0; i < 10; i++)
        if (p->rewards[i] > 0) {
            sprintf(data, "%s%-12s        %7d\n", data, comboNames[i],
                    p->rewards[i]);
            rows++;
        }
    if (rows)
        sprintf(data, "%s\n", data);
    return data;
}

typedef struct Tprofile_datafile {
    void *dat;
    int type;
    long size;
    void *prop;
} Tprofile_datafile;

extern Tprofile_datafile *data;
extern int makecol(int r, int g, int b);
extern void textprintf_ex(void *dst, void *font, int x, int y, int color,
                          int background, const char *format, ...);

int draw_buffer(void *bmp, char *buffer, int x, int y)
{
    int pos;
    char tempBuf[256];
    int tempPos;
    char c;

    pos = y;
    tempPos = 0;
    c = *buffer;
    while (c) {
        if (c == '\n') {
            tempBuf[tempPos] = 0;
            textprintf_ex(bmp, data[53].dat, x, pos, makecol(30, 20, 10),
                          -1, "%s", tempBuf);
            pos += 10;
            tempPos = 0;
        } else {
            tempBuf[tempPos] = c;
            tempPos++;
        }
        c = buffer[1];
        buffer++;
    }
    return pos;
}

void set_next_rank_message(char *buf, Tprofile_rank *p)
{
    int current_rank;
    int next_rank;
    int next_floor;
    int next_combo;
    int next_nml;
    int next_ccc;

    buf[0] = 0;
    current_rank = get_rank_id(p);
    if (current_rank == 11)
        return;
    next_rank = current_rank + 1;
    next_floor = rankFloors[next_rank];
    next_combo = rankCombos[next_rank];
    next_nml = rankNMLs[next_rank];
    next_ccc = rankCCCs[next_rank];
    if (next_floor > p->score && next_floor)
        sprintf(buf, "%s\n - Get to floor %d!", buf, next_floor);
    if (next_combo > p->combo && next_combo)
        sprintf(buf, "%s\n - Make a %d floor combo!", buf, next_combo);
    if (next_ccc > p->no_combo_lost && next_ccc)
        sprintf(buf, "%s\n - Reach floor %d before 1st Hurry Up!", buf,
                next_ccc);
    if (next_nml > p->ccc && next_nml)
        sprintf(buf, "%s\n - Reach floor %d without combos!", buf,
                next_nml);
}

typedef struct Tprofile_load {
    unsigned char before_checksum[0x28];
    int checksum;
    unsigned char remainder[0x550 - 0x2c];
} Tprofile_load;

extern int get_profile_dir_for_profile(char *buffer, unsigned int buflen,
                                       const char *profile);
extern void *get_controls(void);
extern void load_control(void *control, void *fp);

Tprofile_load *load_profile(char *handle)
{
    char file[1024];
    void *fp;
    Tprofile_load *p;
    int cs;

    get_profile_dir_for_profile(file, 1024, handle);
    sprintf(file, "%s%s.itp", file, handle);
    fp = fopen(file, "rb");
    if (!fp)
        return 0;
    p = malloc(0x550);
    fread(p, 0x550, 1, fp);
    load_control(get_controls(), fp);
    fclose(fp);
    cs = generate_profile_checksum(p);
    if (cs != p->checksum) {
        free(p);
        p = 0;
    }
    return p;
}

void delete_profile(char *handle)
{
    char file[1024];

    get_profile_dir_for_profile(file, 1024, handle);
    strcat(file, "replays");
    rmdir(file);
    get_profile_dir_for_profile(file, 1024, handle);
    sprintf(file, "%s%s.itp", file, handle);
    delete_file(file);
    get_profile_dir_for_profile(file, 1024, handle);
    sprintf(file, "%s%s.itr", file, handle);
    delete_file(file);
    get_profile_dir_for_profile(file, 1024, handle);
    rmdir(file);
}

typedef struct Tprofile_create {
    char header[6];
    char handle[32];
    unsigned char before_checksum[2];
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
    int rewards[10];
    int total_jumps;
    char best_replay_names[32][32];
    int flash;
    int jump_hold;
    char last_avatar[64];
    int start_floor;
    int msc_volume;
    int snd_volume;
    char creationDate[16];
    char saveDate[16];
} Tprofile_create;

typedef struct Tprofile_tm {
    int tm_sec, tm_min, tm_hour, tm_mday, tm_mon, tm_year;
} Tprofile_tm;

extern int exists(char *file);
extern void log2file(char *format, ...);
extern long time(long *t);
extern Tprofile_tm *localtime(long *t);
extern void init_control(void *control);
extern int save_profile(Tprofile_create *p);

Tprofile_create *create_profile(char *handle, int overwrite)
{
    char file[1024];
    Tprofile_create *p;
    int i;
    long now;
    Tprofile_tm *my_time;
    int year, month, day;

    get_profile_dir_for_profile(file, 1024, handle);
    sprintf(file, "%s%s.itp", file, handle);
    if (!overwrite && exists(file)) {
        log2file("Overwrite is false and %s already exists", file);
        return 0;
    }
    p = malloc(sizeof(Tprofile_create));
    p->header[0] = 'I';
    p->header[1] = 'T';
    p->header[2] = 'P';
    p->header[3] = '1';
    p->header[4] = '4';
    p->header[5] = '0';
    strcpy(p->handle, handle);
    p->custom_games_played = 0;
    p->games_played = 0;
    p->games_quit = 0;
    p->seconds_spent_playing = 0;
    p->best_score = 0;
    p->best_combo = 0;
    p->best_floor = 0;
    p->total_combo_floors = 0;
    p->total_combos = 0;
    p->total_score = 0;
    p->total_floors = 0;
    p->no_combo_top_floor = 0;
    p->biggest_lost_combo = 0;
    p->cccTotal[4] = 0;
    p->cccTotal[3] = 0;
    p->cccTotal[2] = 0;
    p->cccTotal[1] = 0;
    p->cccTotal[0] = 0;
    p->cccNum[4] = 0;
    p->cccNum[3] = 0;
    p->cccNum[2] = 0;
    p->cccNum[1] = 0;
    p->cccNum[0] = 0;
    p->ccc[4] = 0;
    p->ccc[3] = 0;
    p->ccc[2] = 0;
    p->ccc[1] = 0;
    p->ccc[0] = 0;
    p->jc[4] = 0;
    p->jc[3] = 0;
    p->jc[2] = 0;
    p->jc[1] = 0;
    p->jc[0] = 0;
    for (i = 0; i < 10; i++)
        p->rewards[i] = 0;
    for (i = 0; i < 32; i++)
        p->best_replay_names[i][0] = 0;
    p->total_jumps = 0;
    p->flash = 1;
    strcpy(p->last_avatar, "harold_the_homeboy");
    p->jump_hold = 0;
    p->start_floor = 0;
    p->msc_volume = 150;
    p->snd_volume = 150;
    now = time(0);
    my_time = localtime(&now);
    year = my_time->tm_year;
    month = my_time->tm_mon + 1;
    day = my_time->tm_mday;
    sprintf(p->creationDate, "%d-%s%d-%s%d", year + 1900,
            month < 10 ? "0" : "", month, day < 10 ? "0" : "", day);
    strcpy(p->saveDate, p->creationDate);
    init_control(get_controls());
    if (save_profile(p) < 0) {
        log2file("failed to create profile %s", handle);
        free(p);
        return 0;
    }
    return p;
}
