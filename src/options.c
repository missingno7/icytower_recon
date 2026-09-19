/* Historical CU: F:\projects\icytower\trunk\source\options.c
 * Ownership: GAME
 * UNKNOWN: generate_options_checksum @ 0x004181cc, 254 bytes
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
