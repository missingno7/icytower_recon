/* Historical CU: F:\projects\icytower\trunk\source\strptime.c
 * Ownership: VENDORED_UPSTREAM
 * Partial recovery: the public strptime wrapper is independently matched;
 * the parser body remains unavailable.
 * UNKNOWN: match_string @ 0x0041f5d8, 103 bytes
 * UNKNOWN: _strptime @ 0x0041f640, 2028 bytes
 */
#include <time.h>

char *_strptime(const char *buf, const char *format, struct tm *tm,
                int *state) __attribute__((regparm(3)));

char *strptime(const char *buf, const char *format, struct tm *tm)
{
    int state = 0;

    return _strptime(buf, format, tm, &state);
}

static int first_day(int year) __attribute__((regparm(1)));

static int __attribute__((regparm(1), used)) first_day(int year)
{
    int ret = 1;

    if (year <= 1970)
        ret = 4;
    return ret;
}
