/* Partial historical fld_adspot.c recovery. */
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <direct.h>
#include <sys/stat.h>
#include <pthread.h>
#include "directories.h"
#include "csv.h"

typedef struct FLDAdSpot {
    char *pRemoteImageURL;
    char *pLocalImagePath;
    char *pVisitURL;
    float fFrequency;
} FLDAdSpot;

pthread_t gFLDADThread;
pthread_mutex_t gFLDADMutex;
int giAdCacheSize;
FLDAdSpot *gpAdCache;

static char localFilename[256];

void fldads_destroy_cache(void)
{
    if (gpAdCache) {
        int i;
        for (i = 0; i < giAdCacheSize; i++) {
            free(gpAdCache[i].pLocalImagePath);
            free(gpAdCache[i].pRemoteImageURL);
            free(gpAdCache[i].pVisitURL);
        }
        free(gpAdCache);
        gpAdCache = NULL;
        giAdCacheSize = 0;
    }
}

char *fldads_get_local_cache_name(char *pFileName)
{
    get_adcache_dir(localFilename, sizeof(localFilename));
    mkdir(localFilename);
    strcat(localFilename, pFileName);
    return localFilename;
}

void fldads_dump_local_cache(void)
{
    FILE *fp = fopen(fldads_get_local_cache_name("ads.csv"), "w");
    if (fp) {
        int i;
        pthread_mutex_lock(&gFLDADMutex);
        for (i = 0; i < giAdCacheSize; i++) {
            fprintf(fp, "%s,%s,%.1f\n", gpAdCache[i].pRemoteImageURL,
                    gpAdCache[i].pVisitURL, gpAdCache[i].fFrequency);
        }
        pthread_mutex_unlock(&gFLDADMutex);
        fclose(fp);
    }
}

char *get_url_filename(char *pURL)
{
    char *p;
    p = pURL + strlen(pURL) - 1;
    while (*(p - 1) != '/') {
        p--;
    }
    return p;
}

char *fldads_get_local_filename_from_url(char *pRemoteName)
{
    return fldads_get_local_cache_name(get_url_filename(pRemoteName));
}

void fldads_load_cache_from_csv(CSVParseContext *pCsv)
{
    FLDAdSpot *pCache = NULL;
    int iCacheSize = 0;

    if (pCsv) {
        while (csv_next(pCsv) == 3) {
            char *localFilename = fldads_get_local_filename_from_url(pCsv->pFieldPtrs[0]);
            struct stat statFile;
            if (stat(localFilename, &statFile)) {
                log2file("Warning: local file missing for %s, ad will not be shown", pCsv->pFieldPtrs[0]);
            } else {
                FLDAdSpot *pAd;
                pCache = realloc(pCache, sizeof(*pCache) * (iCacheSize + 1));
                pAd = pCache + iCacheSize;
                pAd->pRemoteImageURL = strdup(pCsv->pFieldPtrs[0]);
                pAd->pLocalImagePath = strdup(fldads_get_local_filename_from_url(pAd->pRemoteImageURL));
                pAd->pVisitURL = strdup(pCsv->pFieldPtrs[1]);
                pAd->fFrequency = strtof(pCsv->pFieldPtrs[2], NULL);
                iCacheSize++;
            }
        }
        pthread_mutex_lock(&gFLDADMutex);
        fldads_destroy_cache();
        gpAdCache = pCache;
        giAdCacheSize = iCacheSize;
        pthread_mutex_unlock(&gFLDADMutex);
    }
}

void fldads_load_local_cache(void)
{
    CSVParseContext *pCsv = csv_open(fldads_get_local_cache_name("ads.csv"));
    if (pCsv) {
        fldads_load_cache_from_csv(pCsv);
        csv_destroy(pCsv);
    }
}
