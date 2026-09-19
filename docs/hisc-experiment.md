# Partial `hisc.c` experiment

`destroy_hisc_table`, `make_hisc_table`, `reset_hisc_table`,
`generate_checksum`, `qualify_hisc_table`, and `sort_hisc_table` are
byte-exact at `-O2`. DWARF establishes the
`Thisc_table` layout as a 32-byte name followed by its five `posts` entries;
the recovered source preserves the allocation/failure paths, ordered `free`
calls, reset loop, checksum recurrence, score qualification, and insertion
sort.

The remaining `hisc.c` functions remain explicit unknowns. The original text
is used only as an oracle by `build/experiments/tdm-2/game-hisc/O2`.
