# beta.c reconstruction checkpoint

All seven functions are implemented from original DWARF and disassembly.
All seven are FUNCTION_MATCH at -O2, and the complete 1141-byte text
contribution matches including padding and resolved relocations. Object and
debug metadata equality remain unproven.

The 276-byte Tbeta structure is struct node: email[128], name[128], code[16],
and a four-byte next pointer. There are no beta globals. File modes and all
initialized sections are retained in the complete comparison report.
Historical unchecked I/O behavior is preserved; this is not hardened input
handling. No original code is embedded or called.

The matching source required signed-byte checksum operands in their
observed expression order, modulo in the garble expression, and chained
node assignments in the binary loader. Cleanup frees the first node then
walks the remaining nodes. A simple do/while and tail-recursive source
produced different code. None of these observations proves original source
spelling, but each proposed source is compiled and independently verified.

The final loader difference was the source guard: `i < 8` instead of the
equivalent `i != 8` within a nine-iteration loop. GCC 4.4.1 produces different
register allocation from those source forms. A bounded comparison of guard,
loop and assignment forms found the matching code without compiler changes.
The earlier six-match report is preserved in
`docs/experiments/game-beta-before-loader-fix.json`.

With ordinary object order beta, control, csv, timer, the synthetic integration
PE places beta, control and csv at their original addresses and extents.
That prefix spans 2576 bytes from 0x401318 to 0x401d28, where custom.c is
still absent. Addresses/extent agreement is not literal linked-byte equality:
the synthetic PE has different reference targets.

Reports: `docs/experiments/game-beta-O2.json`, `optimization-matrix.json`,
and `integration-layout.json`. Remaining work is historical declarations,
source line/header layout, and debug metadata equality.
