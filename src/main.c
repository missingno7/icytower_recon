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

typedef struct Treplay Treplay;
Treplay *demo;
Tcontrol ctrl;

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
