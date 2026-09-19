# Partial `hisc.c` experiment

`destroy_hisc_table` is byte-exact at `-O2`. DWARF establishes the
`Thisc_table` layout as a 32-byte name followed by its `posts` allocation;
the recovered source preserves the original ordered `free` calls.

The remaining `hisc.c` functions remain explicit unknowns. The original text
is used only as an oracle by `build/experiments/tdm-2/game-hisc/O2`.
