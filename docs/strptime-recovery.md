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

## Provenance frontier

The observed table names, `match_string` and `first_day` structures identify the
KTH/Newlib/Heimdal `strptime` family. The independently matched helper bytes
also establish the historical compiler's interpretation of the family's
weekday expression. The original string table uses `"March"`, placing its
lineage after the early `"Mars"` spelling found in the 1999 source.

The remaining parser is not an unmodified drop of a published revision. Its
fourth `gmt` state argument and `%Z` path share the older FreeBSD-style
`_strptime` timezone handling, while its English tables and week-number helpers
come from the KTH family. Public family revisions are therefore research
references only: no candidate body is adopted unless its TDM-GCC comparison
reports `FUNCTION_MATCH` for the complete 2028-byte `_strptime` extent.

Research references: the [2002 Newlib import](https://github.com/mirror/newlib-cygwin/blob/dea7e25ca71e6a6c690f09a43b04f2858c1c348d/newlib/libc/time/strptime.c), the
[1999 Heimdal source](https://github.com/heimdal/heimdal/blob/0d3fc31121aa/lib/roken/strptime.c), and the
[FreeBSD-style stateful parser](https://git.brainchurts.com/uBixOS/ubixos/blob/f6a7e39c29077265516ce890cf998c46b957136e/src/lib/libc/stdtime/strptime.c).
