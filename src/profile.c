/* Historical CU: F:\projects\icytower\trunk\source\profile.c
 * Ownership: GAME
 * Source recovery pending. This file intentionally defines no fallback code.
 * EXACT: hash2 @ 0x004189cc, 71 bytes
 * DIFFER: generate_profile_checksum @ 0x00418a14, 112 bytes
 * DIFFER: get_rank_id @ 0x00418a84, 75 bytes
 * DIFFER: get_rank @ 0x00418ad0, 82 bytes
 * UNKNOWN: set_next_rank_message @ 0x00418b24, 431 bytes
 * UNKNOWN: draw_profile_selector @ 0x00418cd4, 1268 bytes
 * DIFFER: draw_buffer @ 0x004191c8, 185 bytes
 * DIFFER: profile_data_page_advanced @ 0x00419284, 332 bytes
 * UNKNOWN: profile_data_page_basic @ 0x004193d0, 637 bytes
 * DIFFER: profile_data_page_extra @ 0x00419650, 85 bytes (CODEGEN_SIMILAR)
 * UNKNOWN: profile_data_page_general @ 0x004196a8, 1091 bytes
 * UNKNOWN: view_profile @ 0x00419aec, 2249 bytes
 * UNKNOWN: save_profile @ 0x0041a3b8, 1073 bytes
 * UNKNOWN: load_profile @ 0x0041a7ec, 188 bytes
 * UNKNOWN: delete_profile @ 0x0041a8a8, 222 bytes
 * UNKNOWN: create_profile @ 0x0041a988, 823 bytes
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
