# Partial `replay.c` experiment

`get_sort_method`, `set_sort_method`, and `hash` are byte-exact at `-O2`.
The accessors read and write the DWARF-confirmed external `int sort_method`
storage; `hash` uses the recovered xor-shift mix and multiplier. The replay
checksum, selector, persistence, and file-list routines remain pending; this
target compiles only reconstructed source and uses the original executable as
its comparison oracle.
