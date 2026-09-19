# Partial `options.c` experiment

`hash3`, `generate_options_checksum`, and `reset_options` are byte-exact at
`-O2`. The checksum recovery includes the eleven-value accumulator table,
fixed-buffer loops, and inlined hash. The reset recovery
includes the full `Toptions` layout, default string buffers, `file_size_ex`
call, and original field-assignment order. The hash's shift/xor and multiply
recurrence is verified against the original historical CU through
`build/experiments/tdm-2/game-options/O2`.

The remaining options functions are explicit unknowns, with original text used
only as a comparison oracle.
