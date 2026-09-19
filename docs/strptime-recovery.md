# `strptime.c` recovery map

`src/strptime.c` is a vendor-owned parser unit from the historical build. It
is compiled as `game-strptime` with the pinned TDM-GCC 4.4.1 toolchain.

Two functions are independently recovered:

- `first_day` at `0x41f5c4` is an exact 20-byte `regparm(1)` helper. It
  returns the historical weekday base, 4 through 1970 and 1 afterward. The
  source retains it explicitly while its unrecovered sole caller is absent;
  that retention attribute does not change the emitted function bytes.
- The public 35-byte `strptime` wrapper at `0x41fe2c` initializes one
  stack-resident state word and invokes the internal `__strptime` parser.
  Its first three arguments use GCC `regparm(3)` (`eax`, `edx`, and `ecx`);
  the state pointer is the fourth stack argument.

The current comparison resolves the wrapper call directly to `0x41f640` and
reports `FUNCTION_MATCH` for both recovered functions. `match_string` (103
bytes) and `__strptime` (2028 bytes) remain unrecovered, so this compilation
unit is not yet complete.
