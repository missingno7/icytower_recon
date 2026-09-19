# Partial `replay.c` experiment

`get_sort_method`, `set_sort_method`, `hash`, and `destroy_replay` are
byte-exact at `-O2`.
The accessors read and write the DWARF-confirmed external `int sort_method`
storage; `hash` uses the recovered xor-shift mix and multiplier;
`destroy_replay` frees the replay payload at offset `0x8a8` then its owner.
The replay checksum, selector, persistence, and file-list routines remain
pending; this target compiles only reconstructed source and uses the original
executable as its comparison oracle.
