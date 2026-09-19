/* Historical CU: F:\projects\icytower\trunk\source\strptime.c
 * Ownership: VENDORED_UPSTREAM
 * Partial recovery: the public strptime wrapper is independently matched;
 * the parser body remains unavailable.
 * UNKNOWN: _strptime @ 0x0041f640, 2028 bytes
 */
#include <time.h>
#include <string.h>

static const char *abb_weekdays[] = {
    "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", NULL
};
static const char *full_weekdays[] = {
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday", NULL
};
static const char *abb_month[] = {
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
    "Oct", "Nov", "Dec", NULL
};
static const char *full_month[] = {
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December", NULL
};
static const char *ampm[] = { "am", "pm", NULL };
const int tm_year_base = 1900;

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

static int match_string(const char **buf, const char **strs)
    __attribute__((regparm(2)));

static int __attribute__((regparm(2), used))
match_string(const char **buf, const char **strs)
{
    int i;

    for (i = 0; strs[i] != NULL; i++) {
        int len = strlen(strs[i]);

        if (strncasecmp(*buf, strs[i], len) == 0) {
            *buf += len;
            return i;
        }
    }
    return -1;
}
