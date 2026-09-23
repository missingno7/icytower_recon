# `init_game` literal and initialization sequence probes — 2026-09-24

Isolated historical-order `game-main` research with locked GCC 4.4.1 (`-O2`, no generated prototypes), plus retained historical-order `play` and `draw_frame` candidates. No maintained source, generated current state, or recovery ledger changed.

## Evidence and probes

- The current focused card first differs at `init_game+32`: candidate `src/main.c:2308` passes `"INIT GAME"`, while the historical operand resolves to `"\nINIT GAME"`. The content is source-visible and independently confirmed by the historical `main.c:1393` line; literal owner/placement remains unproven in its card. The isolated newline probe changes the first mismatch to `+126`, with 5666 candidate bytes versus 5788 historical. It preserves 63 exact functions.
- Historical `function_lines.py --source-view 1413 1416` decodes the original instructions at `+158`, `+168`, `+178` as zeroing `play_char.max`, `play_char.value`, `play_char.bmp`. The current body instead assigns `curr_char=0`, `play_char.value=0`, `characters=NULL` at candidate lines 2318–2320. This is stronger than a guessed field mapping: all three instructions and their symbol+field addends are explicit in the original disassembly.
- The one-field probe replacing only `curr_char=0` with `play_char.max=0` made candidate relocation `+160` resolve to the original `_play_char+4`. Replacing both incorrect destinations with `play_char.max=0` and `play_char.bmp=NULL` made candidate references at `+160/+170/+180` resolve to `_play_char+4/+0/+8`. Both variants stayed DIFFER and preserved 63 exact functions.
- The combined body applies the leading newline and the three historical field resets together. It stays 5666/5788 bytes, remains DIFFER, and moves the first mismatch to `+126`; its function-level byte-difference count is 4770. No exact-function gains/losses; 63 remain exact.

## What follows at `+126`

At `+126`, the candidate and original encode the `WSAStartup` failure branch with different displacements. The original target is at function offset `+3092`; its historical line row is `main.c:1404`, the `log2file` failure path. The combined candidate target is at `+2980` (`_init_game+0xba4`), mapped to its corresponding `WSAStartup` failure log. This branch lands on the matching source action; the displacement difference reflects the still shorter/reordered function layout and does not identify another missing guard or call. The next version-check path is separately present in both CFGs. No further CFG rewrite is supported by this branch evidence.

## Neighbor safety and downstream context

Across newline-only, field-only, and combined probes: the historical-order overlay retains all 63 exact functions (82 total), with no gains or losses. Comparing field-only to combined, `load_character` candidate instruction bytes are identical (DIFFER, 330/330 bytes, 92 instructions, 18/18 relocations equal). `check_dir` candidate instructions are identical and remain exact (FUNCTION_MATCH, 103 bytes, 32 instructions, 5/5 relocations). Thus the literal change does not perturb the immediate downstream targets' effective output in this context.

## Artifacts

- Bodies: `baseline.c`, `leading-newline.c`, `play-char-max.c`, `play-char-init-fields.c`, and `historical-leading-block.c` in this folder.
- Receipts: `docs/attempts/tu-context/game-main/init-game-literal-newline-20260924.json`, `init-game-play-char-max-20260924.json`, `init-game-play-char-fields-20260924.json`, and `init-game-historical-leading-block-20260924.json`.
- Full comparisons and compiler dumps: `build/tu-context/game-main/init-game-literal-newline-20260924/`, `init-game-play-char-max-20260924/`, `init-game-play-char-fields-20260924/`, and `init-game-historical-leading-block-20260924/`.
- Historical line evidence: `python tools/function_lines.py game-main init_game --source-view 1413 1416`; original CFG and locals are available through `python tools/function_lines.py game-main init_game --lines --blocks`.

Disposition: retain these as source-backed fixes for the research candidate, not accepted body changes. After them, the next first mismatch is the `WSAStartup` error-branch displacement caused by broader layout/CFG differences. Do not pad code to force it; further changes need new historical source evidence.

## Follow-up beyond the `+126` displacement

- Compared the original disassembly and candidate `objdump -d -l` successors. The original `jne` at `+124` goes to the historical line-1404 WSAStartup error log at `+3092`; the combined candidate goes to its same error log at `+2980`. The original and candidate version checks at `+140` and `+152` likewise reach the line-1408 error log and rejoin the normal path. Calls and operations agree on these paths; their encoded displacements reflect the shorter candidate body.
- The first later source-order discrepancy in the historical lines is the `-all` option: original rows 1513–1516 store `keys`, `jumps`, `combos`, `sd`, while the current source stores `jumps`, `combos`, `sd`, `keys`. The isolated historical order variant emits exactly the same `init_game` instructions as the combined candidate. This source ordering difference is optimized away and is deduplicated, not an effective code fix.
- Historical DWARF records local `checkFile` at function offsets `[584,603)` in EDI, `[603,626)` in EAX, and `[626,1324)` in EDI. Current source repeatedly forms `argv[i]` instead of retaining that loop value. A source-supported isolated candidate assigns `checkFile=argv[i]` and uses it for the option tests, keeping the newline and three `play_char` field fixes. Receipt: `init-game-checkfile-lifetime-20260924.json`.
- The `checkFile` variant is a distinct effective output: candidate size grows from 5666 to 5688 bytes, while first strict mismatch moves to `+14` (entry register assignment: candidate loads `argc` to ESI and `argv` to EDI; historical loads `argv` to ESI). It remains DIFFER. The 63 exact functions are preserved with no gains/losses. `load_character` remains DIFFER and its candidate instruction bytes change due the predecessor context; `check_dir` remains FUNCTION_MATCH with its independently resolved instructions/relocations exact. No current evidence supports a missing call or guard after the WSAStartup path. The next concrete blocker is the entry allocation choice: even with the historically evidenced `checkFile` lifetime, GCC assigns ESI to `argc` while history reserves it for `argv`; the wider body remains 100 bytes shorter than history and its source tree/allocation is unresolved.

Additional artifact: `checkfile-lifetime.c` and `build/tu-context/game-main/init-game-checkfile-lifetime-20260924/`.
