# `load_character_bmp` failure-layout follow-up

Research only. No maintained files or ledger entries changed.

## Result

`load_character_bmp` remains **DIFFER** (candidate 1993 bytes, historical 1992; first mismatch +134). The whole-TU probe retains all nine exact peers: `init_custom`, `destroy_custom_data`, `loadCustomSoundFILE`, `loadCustomSoundDF`, `clear_trailing_whitespace`, `get_string_data`, `load_sounds`, `custom_alert`, and `load_frames`. The exact historical predecessor is `load_frames`.

The new source-backed probe nested the success body under `if (fp)` and kept the historical failure log/return in `else`. Original line-table evidence places that failure log at +1389 and the later parser at +1440, while the guard’s first differing branch is +134. The probe compiled successfully, but its candidate object identity is identical to the retained baseline candidate identity; it produced no new effective loader output.

Earlier research already tested three parser-loop exit spellings and compiler alignment controls. The source spellings either collapse or remain 1993-byte DIFFER. `-fno-align-jumps` loses seven exact peers. The historical line table shows the `[datafile]` whitespace scan begins at +1548, naturally aligned; the existing candidate assembly introduces loop alignment before the corresponding header.

## Current blocker

We have historical line/CFG ordering and DWARF variable scopes, but not the original C spelling/tree or compiler pass trace that explains the source of the extra alignment/layout and cold-block placement. The tested guard arrangement collapses at GCC normalization. Further source spelling is low-information until a historically evidenced local lifetime/scope or source extract distinguishes the original CFG.

See `status.json` for exact paths, preserved peers, evidence, and the next discriminating experiment.
