/* Generated from locked DWARF; do not hand-edit. */
#ifndef RECOVERED_CSVPARSECONTEXT_H
#define RECOVERED_CSVPARSECONTEXT_H
#include <stddef.h>
#ifndef RECOVERED_STATIC_ASSERT
#define RECOVERED_STATIC_ASSERT(expr, name) typedef char recovered_static_assert_##name[(expr) ? 1 : -1]
#endif
typedef struct CSVParseContext {
    unsigned char *pDoc;
    unsigned int iDocSize;
    unsigned char *pLineStart;
    int iFields;
    int iFieldCapacity;
    char **pFieldPtrs;
} CSVParseContext;
RECOVERED_STATIC_ASSERT(sizeof(CSVParseContext) == 24, CSVParseContext_size);
RECOVERED_STATIC_ASSERT(offsetof(CSVParseContext, pDoc) == 0, CSVParseContext_offset_pDoc);
RECOVERED_STATIC_ASSERT(offsetof(CSVParseContext, iDocSize) == 4, CSVParseContext_offset_iDocSize);
RECOVERED_STATIC_ASSERT(offsetof(CSVParseContext, pLineStart) == 8, CSVParseContext_offset_pLineStart);
RECOVERED_STATIC_ASSERT(offsetof(CSVParseContext, iFields) == 12, CSVParseContext_offset_iFields);
RECOVERED_STATIC_ASSERT(offsetof(CSVParseContext, iFieldCapacity) == 16, CSVParseContext_offset_iFieldCapacity);
RECOVERED_STATIC_ASSERT(offsetof(CSVParseContext, pFieldPtrs) == 20, CSVParseContext_offset_pFieldPtrs);
#endif
