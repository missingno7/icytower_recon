# Partial `profile.c` experiment

`hash2` is recovered as a complete 71-byte exact function at `-O2`. It applies the historical xor-shift mix with the `668265261` multiplier; the remaining profile persistence and UI bodies are still pending. The target compiles reconstructed source only and uses the original executable solely as a comparison oracle.

get_rank_id is recovered semantically: it scans rank 11 through 0 and requires score, combo, CCC, and no-lost-combo thresholds. Its 75-byte candidate differs only in the compiler register chosen for the profile pointer, so it remains `DIFFER`.

`get_rank` returns the label for the recovered rank index. Its 82-byte candidate differs only in the compiler register chosen for the profile pointer and is recorded as `DIFFER`.