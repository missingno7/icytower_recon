# draw_buffer profile: isolated TU findings

Scope: `game-profile/draw_buffer`, historical VA `0x4191c8`, 185 bytes. Maintained source and generated proof state were not edited.

## Probe collapse and exact neighbors

The historical-order control, a no-`c` direct-dereference body, and removal of the redundant explicit `makecol` prototype all preserve 11 exact profile functions and deduplicate to the same effective emission (`c87e157d5dda279a`). The target remains `DIFFER`: 181 candidate bytes, first raw mismatch at function offset `+27`, 126 differing bytes, 4/4 raw relocation windows unequal, frame `0x12c`, five branches, two calls. No neighbor gains or losses occurred.

Exact neighbors in all three receipts: `hash2`, `generate_profile_checksum`, `get_rank_id`, `get_rank`, `set_next_rank_message`, `profile_data_page_advanced`, `profile_data_page_basic`, `profile_data_page_extra`, `save_profile`, `load_profile`, and `delete_profile`.

Receipts:

- `docs/attempts/tu-context/game-profile/draw-buffer-historder-20260924.json`
- `docs/attempts/tu-context/game-profile/draw-buffer-deref-20260924.json` and `draw-buffer-deref-20260924/body.c`
- `docs/attempts/tu-context/game-profile/draw-buffer-makecol-prototype-20260924.json` (receipt contains the removed prototype and declaration evidence)

Comparison reports are in the matching `build/tu-context/game-profile/<label>/comparison.json` folders. Effective grouping command: `python tools/effective_outcomes.py game-profile draw_buffer --pattern 'draw-buffer-*.json' --response --compact`.

## `+27` and the source-level delta

At original `0x4191e1` (function `+25`), the instruction is `je 0x419274` (`0f 84 8d 00 00 00`). Byte `+27` (`0x8d`) is inside its 32-bit relative displacement; it targets the shared epilogue at `+0xac`. The candidate instruction at function `+25` is `je +0xa8` (`0f 84 89 00 00 00`), so `+27` is a branch-distance consequence of the 4-byte-shorter candidate, not a distinct conditional opcode.

The concrete body delta is pointer fetch/update ordering in both loop paths. Original normal-character path uses `mov al,[ebx+1]` then `inc ebx` (four bytes total); the candidate uses `inc ebx` then `mov al,[ebx]` (three bytes). The newline path has the same one-byte difference. The original also has a three-byte `lea esi,[esi+0]` alignment nop before its epilogue; candidate has a one-byte `nop`. These account for the 4-byte size delta and therefore the `+27` displacement change. The current no-`c` source overlay emits the same effective candidate.

## DWARF type/scope check and next step

Original DWARF gives parameters `BITMAP * bmp`, `char * buffer`, `int x`, `int y`; function-scope locals are `int pos`, `char tempBuf[256]` at frame offset `-288`, and `int tempPos`. Candidate DWARF for the no-`c` overlay reports the same parameter/local types, the same `tempBuf` frame offset, and no lexical blocks. This rules out a type or nested-scope explanation for the observed shortening. The additional source `char c` in maintained code is absent from the original variable list, but removing it did not change output.

The next evidence-backed investigation is the historical loop expression/source-line shape that makes GCC emit the `buffer+1` load before pointer advancement in both paths. The existing `docs/attempts/game-profile/draw_buffer.jsonl` already contains pointer-update/source-form attempts (including `buffer[1]` before `buffer++`, preincrement, and update-before-load forms) that remain DIFFER. No further probe was run because a new body form was not supported by distinct DWARF or instruction evidence; repeating those source variants would only duplicate known outcomes. The current unresolved `.rdata` owner at offset 105/addend 133 remains a separate strict-promotion blocker and does not prove layout-only equality.

