/* Partial historical fld_adspot.c recovery. */
#include <string.h>

char *get_url_filename(char *pURL)
{
    char *p;
    p = pURL + strlen(pURL) - 1;
    do {
        p--;
    } while (*p != '/');
    return p;
}
