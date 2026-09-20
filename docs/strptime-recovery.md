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

The source now also restores the parser's original static table declarations:
eight abbreviated weekdays, eight full weekdays, thirteen abbreviated months,
thirteen full months, and three AM/PM entries (each including its null
terminator), plus `const int tm_year_base = 1900`. DWARF fixes their source
order and dimensions; the literal content comes from their original pointer
tables and strings. With `_strptime` still absent, GCC removes the unused
static arrays, so only the external `tm_year_base` is emitted and verified as
the exact four-byte read-only contribution at `0x004d80cc`. This does not
claim emitted table equality before the parser body references them.

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

The public MapServer `rel-5-6-6` source revision
`d0da3829d7e189e3d49c231e687cbb4ee8671fa9` establishes the closest concrete
family provenance found so far. Its `strptime.c` declares the same five tables
and `tm_year_base` in the same order, and its parser loop begins at source line
204, five lines before the original internal parser's line 209. It is still
rejected as a body candidate: it exposes only a three-argument public
`strptime`, has no `_strptime` state interface or wrapper, spells the full
month `"Mars"`, and retains a different multi-year `first_day` calculation.
Those independently observable differences rule out treating source
provenance as a whole-body recovery.

## Stateful parser boundary

An isolated, untracked adaptation of that public ancestor has now established
the target parser's additional source shape without being admitted to
`src/strptime.c`. With only a mechanical `_strptime` rename, the ancestor's
`first_day` and `match_string` bodies are both `FUNCTION_MATCH`; its parser is
an 1846-byte near ancestor of the target's 2028-byte body. The target DWARF
then fixes a fourth formal named `gmt`, while the 35-byte public wrapper
creates a zero state word and calls the internal function.

The original line table and disassembly further establish two extensions over
the public ancestor: `%c` recursively invokes the wrapper with
`"%a %b %e %H:%M:%S %Y"`; and `%Z` uses locals `cp` and `zonestr`, scans an
uppercase abbreviation, allocates and terminates a temporary token, calls
`tzset`, accepts `"GMT"` by setting `*gmt`, or compares the token with the two
CRT `tzname` entries to set `tm_isdst`. A source-shaped candidate with those
rules retains exact helpers and wrapper but emits a 1983-byte parser, still 45
bytes short. It therefore remains a constrained recovery baseline only; the
complete body is not yet promoted.

Research references: the [2002 Newlib import](https://github.com/mirror/newlib-cygwin/blob/dea7e25ca71e6a6c690f09a43b04f2858c1c348d/newlib/libc/time/strptime.c), the
[1999 Heimdal source](https://github.com/heimdal/heimdal/blob/0d3fc31121aa/lib/roken/strptime.c), and the
[FreeBSD-style stateful parser](https://git.brainchurts.com/uBixOS/ubixos/blob/f6a7e39c29077265516ce890cf998c46b957136e/src/lib/libc/stdtime/strptime.c).
