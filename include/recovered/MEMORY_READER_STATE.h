/* Generated from locked DWARF; do not hand-edit. */
#ifndef RECOVERED_MEMORY_READER_STATE_H
#define RECOVERED_MEMORY_READER_STATE_H
#include <stddef.h>
#ifndef RECOVERED_STATIC_ASSERT
#define RECOVERED_STATIC_ASSERT(expr, name) typedef char recovered_static_assert_##name[(expr) ? 1 : -1]
#endif
typedef struct {
    const unsigned char *buffer;
    long unsigned int bufsize;
    long unsigned int current_pos;
} MEMORY_READER_STATE;
RECOVERED_STATIC_ASSERT(sizeof(MEMORY_READER_STATE) == 12, MEMORY_READER_STATE_size);
RECOVERED_STATIC_ASSERT(offsetof(MEMORY_READER_STATE, buffer) == 0, MEMORY_READER_STATE_offset_buffer);
RECOVERED_STATIC_ASSERT(offsetof(MEMORY_READER_STATE, bufsize) == 4, MEMORY_READER_STATE_offset_bufsize);
RECOVERED_STATIC_ASSERT(offsetof(MEMORY_READER_STATE, current_pos) == 8, MEMORY_READER_STATE_offset_current_pos);
#endif
