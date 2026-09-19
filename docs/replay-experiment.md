# Partial `replay.c` experiment

`get_sort_method`, `set_sort_method`, `hash`, and `destroy_replay` are
byte-exact at `-O2`.
The accessors read and write the DWARF-confirmed external `int sort_method`
storage; `hash` uses the recovered xor-shift mix and multiplier;
`destroy_replay` frees the replay payload at offset `0x8a8` then its owner.
`calc_replay_checksum_131` now has a source-derived partial implementation
covering the 2220-byte replay layout and its checksum arithmetic; its final
loop still differs only in independent-load scheduling. The selector,
persistence, and file-list routines remain pending; this target compiles only
reconstructed source and uses the original executable as its comparison oracle.
