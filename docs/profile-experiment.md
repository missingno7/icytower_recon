# Partial `profile.c` experiment

`hash2` is recovered as a complete 71-byte exact function at `-O2`. It applies the historical xor-shift mix with the `668265261` multiplier; the remaining profile persistence and UI bodies are still pending. The target compiles reconstructed source only and uses the original executable solely as a comparison oracle.

get_rank_id is recovered semantically: it scans rank 11 through 0 and requires score, combo, CCC, and no-lost-combo thresholds. Its 75-byte candidate differs only in the compiler register chosen for the profile pointer, so it remains `DIFFER`.

`get_rank` returns the label for the recovered rank index. Its 82-byte candidate differs only in the compiler register chosen for the profile pointer and is recorded as `DIFFER`.

generate_profile_checksum temporarily clears the profile checksum at offset `0x28`, accumulates all 340 profile words weighted from 1 through 340, restores it, then applies hash2. Its 110-byte candidate is recorded as DIFFER against the historical 112-byte body. The historical DWARF record fixes the complete source-local sequence as `i`, `cs`, `oldCS`, and `int *pos`; the reconstructed declarations and pointer type agree. The remaining two bytes come from the original maintaining separate `i` and word-position registers in the loop, whereas the candidate proves their relation and folds the position into the index. One-based, pre-increment, and post-increment source-equivalent loop probes produced 115-, 111-, and 110-byte nonmatches, so no code-generation-shaped source variant was retained.

profile_data_page_extra is an exact 85-byte match. It allocates a 2 KiB string, appends the profileâ€™s `total_jumps` at offset `0xd8`, then appends a blank line. The recovered formatter literals now form a uniquely verified contiguous read-only-data contribution.

draw_buffer is behaviorally recovered. It splits newline-terminated lines into a 256-byte temporary buffer, draws each through `data[53].dat` in the recovered brown color, advances by 10 pixels per line, and returns the final Y coordinate. Its candidate differs by four bytes because the compiler advances the input pointer before loading the next character, while the original loads first and then advances it; it remains `DIFFER`.

profile_data_page_advanced is behaviorally recovered. It formats Clock Challenge counts and averages for all populated entries, followed by each named earned reward. The historical DWARF record proves the sole locals are `data`, `i`, and `rows`, matching the reconstruction. In the 332-byte oracle, the average loop spills `i` across `sprintf` before testing the next clock-challenge row; the 320-byte candidate keeps it in a register. Both preserve the historical positive gates for the initial Challenge-1 separator, each count, each average divisor, and the reward-row total. It remains `DIFFER` because the spill induces a different block layout.

profile_data_page_basic is an exact 637-byte match. It formats score, floor, combo, no-combo, and jump statistics from the recovered profile layout. Its cold no-combo branch is represented as one source block, matching the historical compiler layout.

set_next_rank_message is behaviorally recovered. It chooses the next rank and updates the supplied buffer with the highest-priority unmet nonzero floor, combo, CCC, or no-combo-floor requirement. Its 345-byte candidate retains a different inline rank-scan and branch layout from the 431-byte historical body, so it is recorded as `DIFFER`.

load_profile is behaviorally recovered as a 188-byte candidate, equal in size and control-flow shape to the historical function. It creates the profile path, reads the 0x550-byte profile plus controls, checks the stored checksum at offset 0x28, and frees rejected data. The only comparison differences are the two unverified read-only-data addresses for its locally reconstructed pathname and file-mode literals, so the routine is recorded as `DIFFER`.

delete_profile is reconstructed as a 222-byte `CODEGEN_SIMILAR` candidate. It removes the replay directory, profile data, replay data, and then the profile directory. Every instruction matches after masking the two local format-string relocations, while the local string addresses remain independently unverified.

create_profile is behaviorally reconstructed from the historical 0x550-byte profile layout. It rejects unapproved overwrites, initializes persistent counters, challenges, rewards, replay names, settings, avatar, and timestamps, initializes controls, and persists the result. The recovered field layout places `flash` at `0x4dc` and `jump_hold` at `0x4e0`: initialization sets `jump_hold` to 1 before the avatar copy and clears `flash` afterward, restoring the historical writes. Its 819-byte candidate is recorded as `DIFFER` against the 823-byte historical body: the remaining four-byte code-size difference is the compiler form of the replay-name initialization loop; local format strings also require independent data placement verification.

profile_data_page_general is behaviorally reconstructed. It emits creation date, a normalized elapsed-time string with singular handling, and game totals with the historical spacing convention. Its 1058-byte candidate differs from the 1091-byte historical formatter, chiefly in arithmetic and local-storage choices, so it remains `DIFFER`.

The rank predicate maps the no-combo-floor threshold at offset `0x58` to `rankNMLs` and the clock-challenge threshold at offset `0x88` to `rankCCCs`; this corrects the recovered source’s former array swap.

save_profile is behaviorally reconstructed as a 1080-byte candidate. It creates the profile and replay directories, writes the 0x550-byte profile plus controls, refreshes saveDate and checksum, and writes the profile statistics report. All direct persistence and formatter calls resolve to their historical targets; local literal placement and seven remaining generated bytes keep it at `DIFFER`.


draw_profile_selector is reconstructed from the 0x418cd4 renderer: it draws the profile frame and scrollbar assets, clips a 32-byte-name list, highlights the selected profile, labels the current profile, and restores the full bitmap clip rectangle. Its recovered scan loop preserves the offset and max-post limits recorded in the original code.
