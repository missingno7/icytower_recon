# `get_string` result sentinel replay in `main.c` — 2026-09-24

## Scope and control

Isolated original-evidence review at HEAD `520e4a27cc02f5e9ad75df31bd834876ac193687`. No production `src/`, `tools/`, ledger, or generated current files were edited. The original caller instructions were disassembled from the user-supplied `assets/icytower15.exe` with the locked TDM-2 objdump; line rows and local DIE/location evidence came from the checked-in census and focused `do_replay_menu` card.

The starting `force_create_profile` note establishes a caller-specific distinction: the original `get_string` result `-1` selects the “create profile later” path there, while an empty entered name is tested separately and retries. That does not establish that other callers should retry on empty input.

## Remaining callers and original CFG

All three other calls in reconstructed `main.c` are inside `do_replay_menu` (original VA `0x410f98`, size 2661). The focused card has current state `DIFFER`, 2657 candidate bytes, first byte difference at function offset `+397` (`0x411125`; original byte `0x95`, candidate `0xbd`). The result-handling branches occur later. The card’s DWARF inventory places `action` in the `do_replay_menu` lexical scope and gives it fragmented register locations; the original call sequences independently show the return value moved from EAX to EDI before caller-specific handling. The three call sites map through original DWARF line rows to source lines 5525/5526, 5548/5553, and 5571/5574.

### Name field (`pname`), call at `0x41141d` / function offset `+0x485`

Original instructions call `_get_string`, copy EAX to EDI, call `replaceBadCharacters`, increment EDI, and branch on zero to the cancel status. Thus only result `-1` is special after the increment; every other result, including zero, advances to filename entry. There is no empty-name test. Current C does `action++` and tests `!action`, preserving precisely that result partition.

### Filename field (`fname`), call at `0x4115bb` / function offset `+0x623`

Original instructions likewise preserve EAX, sanitize the field, increment the saved result, and branch on zero to the cancel status. All non-`-1` results proceed to the next status, including an empty result. There is no post-editor empty-filename retry. Current C uses `action == -1` for the same partition. The optional default filename is prepared before this call only when the filename is empty and the player name is nonempty.

### Optional comment field, call at `0x41176f` / function offset `+0x7d7`

Original instructions compare the returned EAX first with `-1` (cancel), then with `-2` (guest-specific skip), then route all other values to status 3. Empty comments are accepted. Current C expresses the same ordered `-1`, `-2`, otherwise partition.

The retained instruction excerpts are in `original-get-string-result-cfg.txt` (SHA-256 `592d93c69ba03b8b80d28c66382960993438ba6a3e5390fcf2f7f6458fd0b0a`). They include the original call/return sequences and their immediate branches. The checked-in line mapping rows around the calls are at `0x411424` (line 5525), `0x411434` (line 5526), `0x4115c2` (line 5548), `0x4115d2` (line 5553), `0x411774` (line 5571), and `0x41177d` (line 5574).

## Probe selection and outcome

No full-TU probe was run. The three unresolved call sites do not share the force-profile mismatch signature: in each, `-1` is a cancel sentinel, and in the optional comment field `-2` is an additional skip sentinel. The current source already encodes these original CFG partitions, and the original has no empty-name/empty-field retry edge at these sites. Adding the force-profile empty-name guard here would change behavior without original-instruction support. The focused `do_replay_menu` mismatch begins at `+397`, before the first editor call, and is a register-selection mismatch rather than a sentinel/empty-input branch mismatch.

Outcome class: **evidence-only / no applicable source-shape probe**. No effective output was generated, so no peer-count change or duplicate output is claimed. The documented main-TU baseline remains 64/82 exact peers; `do_replay_menu` remains `DIFFER` at 2657/2661.

## Blocker and next experiment

The force-profile caller’s corrected sentinel/empty-name distinction does not transfer to the replay editor. Keep all three replay field result partitions as currently expressed. Continue `do_replay_menu` from the concrete `+397` register-selection difference or its already-documented scoped-local/frame-layout issues; do not spend a full-TU probe on an unsupported empty-field guard. Revisit replay call handling only if new original source, CFG, or lexical-scope evidence identifies an unrepresented result edge.
