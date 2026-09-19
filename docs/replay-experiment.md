# Partial `replay.c` experiment

`get_sort_method` and `set_sort_method` are byte-exact at `-O2`. They read
and write the DWARF-confirmed external `int sort_method` storage. The replay
checksum, selector, persistence, and file-list routines remain pending; this
target compiles only reconstructed source and uses the original executable as
its comparison oracle.
