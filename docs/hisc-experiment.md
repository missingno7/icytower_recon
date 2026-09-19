# Partial `hisc.c` experiment

`destroy_hisc_table`, `make_hisc_table`, `reset_hisc_table`, and
`generate_checksum` are byte-exact at `-O2`. DWARF establishes the
`Thisc_table` layout as a 32-byte name followed by its five `posts` entries;
the recovered source preserves the allocation/failure paths, ordered `free`
calls, reset loop, and checksum recurrence.

The remaining `hisc.c` functions remain explicit unknowns. The original text
is used only as an oracle by `build/experiments/tdm-2/game-hisc/O2`.
