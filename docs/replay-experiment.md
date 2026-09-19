# Partial `replay.c` experiment

`get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, and `update_file_list` are
byte-exact at `-O2`.
The accessors read and write the DWARF-confirmed external `int sort_method`
storage; `hash` uses the recovered xor-shift mix and multiplier;
`destroy_replay` frees the replay payload at offset `0x8a8` then its owner.
`calc_replay_checksum_131` now has a source-derived partial implementation
covering the 2220-byte replay layout and its checksum arithmetic; its final
loop still differs only in independent-load scheduling. The selector and
persistence routines remain pending; this target compiles only
reconstructed source and uses the original executable as its comparison oracle.

`calc_replay_checksum` is now behaviorally reconstructed from the historical
DWARF layout and the 676-byte body. It includes every integrity input: replay
settings, score and combo counters, the three 100-element timing curves,
name/date/comment bytes, and packed input records, before applying the local
hash mixer. The `-O2` candidate is 656 bytes; its arithmetic scheduling differs
from the historical body, so the inventory records it as `DIFFER`.

`load_replay` now reconstructs the ITR140 reader. It opens once to validate the
six-byte header and allocate the event buffer from its size, then reopens and
loads every persisted field in historical wire order. It rejects invalid headers,
failed second opens, and checksum mismatches after logging the stored and
computed values. The candidate is the original 1,136-byte length but remains
`DIFFER` because its setup and call scheduling differ.

`my_strcmp` now recovers the 24-byte replay-post layout and comparator behavior: directory entries rank ahead of replay files, file rows use the selected score/floor/combo property when sorting modes 2–4 are active, and the remaining names compare case-insensitively. Its candidate is 127 bytes against the historical 128 because the compiler places the directory-mismatch return path differently; the comparison inventory records it as `DIFFER`.

`update_file_list` matches its complete 184-byte body. It frees and clears all existing 24-byte posts, resets the independently typed 1,024-entry list, scans the original `"%s/*"` pattern through `add_itr_file`, and sorts with `my_strcmp`. Every data, string, callback, and call relocation resolves exactly.

`add_itr_file` is now recovered semantically. It ignores the current-directory marker, allocates each 24-byte post with the original filename slack, admits directories and `.itr` files, preserves the parent marker, and stores replay-version errors other than the two sentinel failures. The `-O2` candidate is 357 bytes against the historical 360 because block ordering differs; it remains recorded as `DIFFER`.

create_replay is behaviorally reconstructed. It allocates the 0x8ac-byte replay object, initializes its fixed header, default name/date, score/floor/combo state, and replay-event storage. The candidate remains `DIFFER` while its six-byte header-copy lowering and loop alignment differ from the historical 254-byte body.
