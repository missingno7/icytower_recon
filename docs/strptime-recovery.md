# `strptime.c` recovery map

`src/strptime.c` is a vendor-owned parser unit from the historical build. The
public 35-byte `strptime` wrapper at `0x41fe2c` is independently recovered and
compiled as `game-strptime` with the pinned TDM-GCC 4.4.1 toolchain.

The wrapper initializes one stack-resident state word and invokes the internal
`__strptime` parser. Its first three arguments use GCC `regparm(3)` (`eax`,
`edx`, and `ecx`); the state pointer is the fourth stack argument. The
comparison resolves that call directly to `0x41f640` and reports
`FUNCTION_MATCH` for all 35 bytes.

The parser implementation remains unrecovered: `first_day` (20 bytes),
`match_string` (103), and `__strptime` (2028). The public wrapper does not
make this compilation unit complete, but it preserves the historical API and
calling convention for dependent recovery work.
