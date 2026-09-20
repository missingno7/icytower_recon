/* Generated from locked DWARF; do not hand-edit. */
#ifndef RECOVERED_TBETA_H
#define RECOVERED_TBETA_H
#include <stddef.h>
#ifndef RECOVERED_STATIC_ASSERT
#define RECOVERED_STATIC_ASSERT(expr, name) typedef char recovered_static_assert_##name[(expr) ? 1 : -1]
#endif
typedef struct node {
    char email[128];
    char name[128];
    char code[16];
    struct node *next;
} Tbeta;
RECOVERED_STATIC_ASSERT(sizeof(Tbeta) == 276, Tbeta_size);
RECOVERED_STATIC_ASSERT(offsetof(Tbeta, email) == 0, Tbeta_offset_email);
RECOVERED_STATIC_ASSERT(offsetof(Tbeta, name) == 128, Tbeta_offset_name);
RECOVERED_STATIC_ASSERT(offsetof(Tbeta, code) == 256, Tbeta_offset_code);
RECOVERED_STATIC_ASSERT(offsetof(Tbeta, next) == 272, Tbeta_offset_next);
#endif
