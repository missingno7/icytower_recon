# custom.c recovery

All ten historical functions now have independent C implementations, reconstructed
from the original disassembly, DWARF types, lexical scopes and function order.
At `-O2`, nine functions match after independent relocation resolution, including
the 2392-byte `load_frames` and 1729-byte `load_sounds`. The remaining function,
`load_character_bmp`, differs. Its 1,993-byte candidate matches the historical
prologue, all local layouts, and early parsing transfers through byte 133; the
first mismatch is the `fopen`-failure branch target. The original places that
error block at offset `0x56d`, while the pinned compiler moves the equivalent
block to the function tail at `0x77b`, causing the later layout drift. This is
not complete text, object or CU equality.

The original 1260-byte Tcustom layout is declared in `include/custom.h`.
Its frame array, palette, sounds and datafile fields retain historical offsets.
The four initialized bytes of pink and the 645-byte read-only contribution
match independently. Black is a four-byte common with a 16-byte allocation.

Code generation depended on explicit fgets prefetch loops, the lexical scope
of the temporary palette, and historical Allegro inline draw_sprite expansion.
The original sound-loading control flow includes separate mid and midi tests;
the reconstruction retains that behavior. GUI color assignments were checked
against named original globals, rather than inferred from screen appearance.

The initial six-match attempt is retained in
`docs/experiments/game-custom-first.json`. The current full function, data,
symbol and relocation inventory is `docs/experiments/game-custom-O2.json`.
The five optimization levels are recorded in the optimization matrix.

Custom is included in the ordinary recovered-game source link, while its real
directory, main-helper, logg and audio-library dependencies also resolve in a
separate synthetic custom-audio link. Its one differing function and natural
layout work remain unresolved.
No substitutes or original-code fallbacks were added. Historical source lines,
debug metadata and final common/data ordering remain unproven.
