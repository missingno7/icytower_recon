# `strptime.c` recovery map

`src/strptime.c` is a vendor-owned parser unit from the historical build. It
is compiled as `game-strptime` with the pinned TDM-GCC 4.4.1 toolchain.

Three functions are independently recovered:

- `first_day` at `0x41f5c4` is an exact 20-byte `regparm(1)` helper. It
  returns the historical weekday base, 4 through 1970 and 1 afterward.
- `match_string` at `0x41f5d8` is an exact 103-byte `regparm(2)` helper. It
  compares the parser cursor against its null-terminated string table with
  `strncasecmp`, advances the cursor when it finds a match, and returns the
  table index or -1.
- The public 35-byte `strptime` wrapper at `0x41fe2c` initializes one
  stack-resident state word and invokes the internal `__strptime` parser.
  Its first three arguments use GCC `regparm(3)` (`eax`, `edx`, and `ecx`);
  the state pointer is the fourth stack argument.

`first_day` and `match_string` are retained explicitly only while their sole,
unrecovered caller is absent; the retention annotations do not alter their
emitted function bytes. The current comparison reports `FUNCTION_MATCH` for
all three recovered functions. `__strptime` (2028 bytes) remains unrecovered,
so this compilation unit is not yet complete.
