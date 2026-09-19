# Partial `profile.c` experiment

`hash2` is recovered as a complete 71-byte exact function at `-O2`. It applies the historical xor-shift mix with the `668265261` multiplier; the remaining profile persistence and UI bodies are still pending. The target compiles reconstructed source only and uses the original executable solely as a comparison oracle.

get_rank_id is recovered semantically: it scans rank 11 through 0 and requires score, combo, CCC, and no-lost-combo thresholds. Its 75-byte candidate differs only in the compiler register chosen for the profile pointer, so it remains `DIFFER`.

`get_rank` returns the label for the recovered rank index. Its 82-byte candidate differs only in the compiler register chosen for the profile pointer and is recorded as `DIFFER`.

generate_profile_checksum temporarily clears the profile checksum at offset `0x28`, accumulates all 340 profile words weighted from 1 through 340, restores it, then applies hash2. Its 110-byte candidate is recorded as DIFFER against the historical 112-byte body.

profile_data_page_extra is an exact 85-byte match. It allocates a 2 KiB string, appends the profile’s `total_jumps` at offset `0xd8`, then appends a blank line. The recovered formatter literals now form a uniquely verified contiguous read-only-data contribution.

draw_buffer is behaviorally recovered. It splits newline-terminated lines into a 256-byte temporary buffer, draws each through `data[53].dat` in the recovered brown color, advances by 10 pixels per line, and returns the final Y coordinate. Its candidate differs by four bytes because the compiler advances the input pointer before loading the next character, while the original loads first and then advances it; it remains `DIFFER`.

profile_data_page_advanced is behaviorally recovered. It formats Clock Challenge counts and averages for all populated entries, followed by each named earned reward. Its candidate is recorded as `DIFFER` because its average-loop register allocation differs from the historical body.

profile_data_page_basic is an exact 637-byte match. It formats score, floor, combo, no-combo, and jump statistics from the recovered profile layout. Its cold no-combo branch is represented as one source block, matching the historical compiler layout.
