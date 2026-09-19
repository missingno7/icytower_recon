/* Original cross-CU interfaces, recovered from DWARF. Implementations remain
 * in their historical CUs; this header introduces no substitute behavior. */
#ifndef ICYTOWER_GAME_SERVICES_H
#define ICYTOWER_GAME_SERVICES_H
#include <stddef.h>
#include <allegro.h>
#include "directories.h"
void log2file(const char *format, ...);
SAMPLE *getSampleFromOggDatafile(DATAFILE *df, int id);
SAMPLE *logg_load(const char *filename);
#endif
