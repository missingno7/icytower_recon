# Partial `options.c` experiment

`hash3` is byte-exact at `-O2`. Its shift/xor and multiply recurrence is
verified against the original historical CU through
`build/experiments/tdm-2/game-options/O2`.

The remaining options functions are explicit unknowns, with original text used
only as a comparison oracle.
