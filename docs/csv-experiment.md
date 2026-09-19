# Complete CSV CU text

The six original csv.c functions and the complete 680-byte text contribution
match at -O2. The 24-byte CSVParseContext layout, parameter qualifiers, source
function order, and body behavior were recovered from DWARF and disassembly.
Ownership remains AMBIGUOUS: this reconstruction does not establish an
upstream author or license, nor count the CU as game-owned.

The parser mutates its copied buffer in place. csv_next skips comment and
blank lines, splits comma or previously nulled separators, and restores the
previous newline. csv_rewind resets the cursor so those nulled separators
can be revisited. Historical unchecked allocation/I/O behavior is retained.

The rb mode string appears seven times in original read-only data. A unique
content search alone cannot resolve its relocation. Original COFF preserves
the csv.c FILE group and its .text and .rdata contribution symbols, including
the three-byte .rdata logical size. The verifier selects the FILE group by
filename AND original text address, requires equal section logical lengths,
then resolves from that independent .rdata symbol. It never reads the tested
instruction operand to choose a target. This also avoids ambiguity between
same-named library and game source files.

A negative test moves that COFF anchor to a different identical rb string
while retaining every original instruction byte. Masked equality stays at
six functions, but resolved equality drops to five and full text is rejected.
Complete data content is verified separately. No object or DWARF equality
is claimed.

The ordinary beta/control/csv link order extends the natural address/extent
prefix to 2576 bytes. The next absent CU is custom.c; timer is linked only as
an integration dependency and is not yet at its original address.
