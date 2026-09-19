/* Historical CU: F:\projects\icytower\trunk\source\options.c
 * Ownership: GAME
 * UNKNOWN: load_options @ 0x0041839c, 70 bytes
 * UNKNOWN: save_options @ 0x004183e4, 58 bytes
 */

unsigned int hash3(unsigned int a)
{
    a = (a ^ 0x3dU) ^ (a >> 16);
    a *= 9U;
    a ^= a >> 4;
    a *= 668265261U;
    a ^= a >> 15;
    return a;
}

typedef struct {
    int flash, checksum, jump_hold, full_screen;
    int floor_shrink, floor_size, start_speed, speed_increase, gravity;
    int msc_volume, snd_volume, sort_method;
    char updateDate[16], posterDate[16], posterUrl[256], posterSrc[256];
    int posterSize;
    char lastProfile[32];
    int timesStarted;
} Toptions;

extern char *strcpy(char *dst,const char *src);
extern int file_size_ex(const char *filename);

void reset_options(Toptions *o)
{
    o->flash=0;
    o->full_screen=0;
    o->jump_hold=1;
    o->msc_volume=150;
    o->snd_volume=150;
    o->floor_shrink=1;
    o->speed_increase=1;
    o->start_speed=5;
    o->floor_size=1;
    o->gravity=1;
    o->timesStarted=0;
    o->sort_method=1;
    strcpy(o->updateDate,"2001-12-22");
    strcpy(o->lastProfile,"guest");
    strcpy(o->posterDate,"1111-22-33");
    strcpy(o->posterUrl,"http://www.freelunchdesign.com/?src=it15_game");
    strcpy(o->posterSrc,"default.dat");
    o->posterSize=file_size_ex("data/com/default.dat");
}

int generate_options_checksum(Toptions *o)
{
    int cs,i;
    int values[11] = {
        o->flash, o->full_screen, o->jump_hold, o->msc_volume, o->snd_volume,
        o->floor_size, o->floor_shrink, o->gravity, o->start_speed,
        o->speed_increase, o->posterSize
    };

    for (i=0,cs=0;i<11;i++) cs+=(values[i]+i)*17;
    for (i=0;i<8;i++) cs+=o->updateDate[i];
    for (i=0;i<16;i++) cs+=o->updateDate[i]+o->posterDate[i];
    for (i=0;i<256;i++) cs+=o->posterUrl[i]+o->posterSrc[i];
    return hash3(cs);
}
