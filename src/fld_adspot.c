/* Partial historical fld_adspot.c recovery. */
#include <string.h>
#include <direct.h>
#include "directories.h"
#include "csv.h"

static char localFilename[256];
void fldads_load_cache_from_csv(CSVParseContext *pCsv);

char *get_url_filename(char *pURL)
{
    char *p;
    p = pURL + strlen(pURL) - 1;
    do {
        p--;
    } while (*p != '/');
    return p;
}

char *fldads_get_local_cache_name(char *pFileName)
{
    get_adcache_dir(localFilename, sizeof(localFilename));
    mkdir(localFilename);
    strcat(localFilename, pFileName);
    return localFilename;
}

char *fldads_get_local_filename_from_url(char *pRemoteName)
{
    return fldads_get_local_cache_name(get_url_filename(pRemoteName));
}

void fldads_load_local_cache(void)
{
    CSVParseContext *pCsv = csv_open(fldads_get_local_cache_name("ads.csv"));
    if (pCsv) {
        fldads_load_cache_from_csv(pCsv);
        csv_destroy(pCsv);
    }
}
