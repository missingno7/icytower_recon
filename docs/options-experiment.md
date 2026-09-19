# `options.c` experiment

All five functions in `options.c` are byte-exact at `-O2`, including its
complete 666-byte historical `.text` contribution. `load_options` and
`save_options` preserve the original packed-record checksum, reset, and
sort-method flow. The checksum routine uses its historical local declaration
and zero-initialization order, which reproduces the observed register setup.

The recovery is verified against the original historical CU through
`build/experiments/tdm-2/game-options/O2`; the original executable remains an
oracle only.
