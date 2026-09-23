#include "recovered/Tprofile.h"
#include "recovered/Tavailable_profile.h"
extern int stricmp(const char *, const char *);
__attribute__((noinline)) int byte_current(Tprofile *p, const char *name) { return stricmp(name, (char *)p + 6); }
__attribute__((noinline)) int typed_current(Tprofile *p, const char *name) { return stricmp(name, p->handle); }
__attribute__((noinline)) int byte_entry(Tavailable_profile *p, int i, const char *name) { return stricmp(name, (char *)p + i * 32); }
__attribute__((noinline)) int typed_entry(Tavailable_profile *p, int i, const char *name) { return stricmp(name, p[i].handle); }
