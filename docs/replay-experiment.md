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
hash mixer. The initial accumulator is `(biggest_lost_combo * 17 +
no_combo_top_floor * 127 + 17) * 2`: the original carries the `17`
before doubling, contributing 34 at this stage. Historical DWARF also types
its `sum` local as `unsigned int` even though the function returns `int`; that
restores the original unsigned timing-curve conversions and brings the `-O2`
candidate from 656 to 675 bytes. Its remaining byte and arithmetic scheduling
differ from the historical 676-byte body. A fully stepwise initial accumulation
(`biggest_lost_combo * 17 + 17`, then the no-combo term, then doubling) extends
the matching prefix from 19 to 21 bytes, but materializes `sum` in `edx` rather
than the original `ecx`; the resulting 675-byte object remains `DIFFER`. The
undoubled single-expression form regresses at byte 16, so neither probe is
retained as source.

`load_replay` now reconstructs the ITR140 reader. It opens once to validate the
six-byte header and allocate the event buffer from its size, then reopens and
loads every persisted field in historical wire order. It rejects invalid headers,
failed second opens, and checksum mismatches after logging the stored and
computed values. The candidate is the original 1,136-byte length but remains
`DIFFER` because its setup and call scheduling differ.

`get_replay_property` is now reconstructed as the lightweight file-list reader.
It distinguishes ITR140 from the historical ITR130 and ITR011 formats, reports
their original error values, reads the common score/floor/combo prefix, and logs
the requested property. Its 1,143-byte candidate remains `DIFFER` against the
historical 1,147-byte routine.

`save_replay` now reconstructs the ITR140 writer. It builds the saved path,
preserves an existing replay date or emits the legacy timestamp format, sets the
requested event count, recalculates the checksum, and writes the same complete
field sequence consumed by `load_replay`. Its candidate reaches the historical
1,227-byte length and remains `DIFFER` only in instruction scheduling.

`my_strcmp` now recovers the 24-byte replay-post layout and comparator behavior: directory entries rank ahead of replay files, file rows use the selected score/floor/combo property when sorting modes 2â€“4 are active, and the remaining names compare case-insensitively. The original's `lea`/unsigned-range check establishes the property-mode test as `(unsigned)(sort_method - 2) <= 2`; the recovered source now preserves that form. Its 123-byte candidate still differs from the historical 128-byte body because the pinned compiler places the directory-mismatch return path differently, so the comparison inventory records it as `DIFFER`.

`update_file_list` matches its complete 184-byte body. It frees and clears all existing 24-byte posts, resets the independently typed 1,024-entry list, scans the original `"%s/*"` pattern through `add_itr_file`, and sorts with `my_strcmp`. Every data, string, callback, and call relocation resolves exactly.

`add_itr_file` is now recovered semantically. It ignores the current-directory marker, allocates each 24-byte post with the original filename slack, admits directories and `.itr` files, preserves the parent marker, and stores replay-version errors other than the two sentinel failures. The `-O2` candidate is 357 bytes against the historical 360 because block ordering differs; it remains recorded as `DIFFER`.

create_replay is `CODEGEN_SIMILAR` at the historical 254-byte extent. It allocates the 0x8ac-byte replay object, initializes its fixed header, default name/date, score/floor/combo state, and replay-event storage. The fixed `ITR140` header is a file-local mutable data object, restoring the historical pair of data loads into the six-byte destination; allocating event storage from the initialized `r->size` field restores the original load-and-LEA path. The masked code stream and all named transfers match. The header's local data-section placement is not independently established, so it receives no exact-function credit.
