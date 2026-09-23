# Replay read-only data crosswalk

Research-only analysis and GCC 4.4.1/TDM-2 `-O2` isolated overlays. No maintained source, generated current state, function card, or recovery ledger was edited.

## Historical and candidate data structures

The historical replay COFF group's `.rdata` contribution begins at PE address `0x4d7960`.

| Structure | Historical | Reachability candidate | Evidence |
|---|---:|---:|---|
| `replay_selector` switch table | `.rdata+0x1b8..0x304`, 332 bytes / 83 dwords | `.rdata+0x1bc..0x258`, 156 bytes / 39 dwords | Original dispatch at `_replay_selector+0x42d` does `jmp *0x4d7b18(,%eax,4)` after subtracting 3 and checking `eax <= 0x52`. Candidate dispatch at `_replay_selector+0x1a8` does `jmp *0x1bc(,%eax,4)` after subtracting `0x2f` and checking `eax <= 0x26`. All 39 candidate table words have COFF relocations to `.text`; the historical words are linked `.text` target addresses. There is no named variable DIE or COFF symbol in either jump-table span. The xrefs, instruction, and replay_selector function extent establish the generated table's function owner. |
| `save_replay` month-pointer initializer | `_C.110.9301` at `.rdata+0x440`, 48 bytes / 12 absolute string pointers | `_C.112.9499` at `.rdata+0x380`, 48 bytes / 12 `.rdata` relocations | Both point in Jan–Dec order to their matching month strings. The `save_replay` DWARF local `months` is `char *[12]`, stack located at `DW_OP_fbreg -84`; its compiler-emitted initializer template is the 12-entry static table. Candidate/historical compiler symbol spellings differ. |
| Named replay header | `_REPLAY_HEADER` at `.rdata+0x470`, bytes `ITR140` | `_replay_header` at `.rdata+0x3b0`, bytes `ITR140` | Historical and candidate file-local COFF symbols; matching DWARF type is `const char[6]` in the const-six probes. The pointer table immediately precedes each named header object. |

The switch table accounts for a 176-byte size difference. After it, the candidate error and save strings track the historical contribution at a 172-byte offset difference because the candidate table starts four bytes later and is 176 bytes shorter. The month-pointer initializer then starts 192 bytes earlier in the candidate: after `Dec`, historical has 21 zero bytes before its naturally aligned table, while the candidate has 1 zero byte. Thus the historical/candidate header offset difference is 192 bytes. This explains the observed post-reachability same-section distance mismatch without inserting data or treating bytes as padding instructions.

The current source's reconstructed `replay_selector` switch only generates the 39-entry dense range (key interval 47–85 after the compiler's subtraction). The historical function generates an 83-entry range (key interval 3–85). The exact lower-range case structure must come from a historical control-flow/source reconstruction; it is not an unnamed initialized data object to synthesize by size.

## Why `ITR140` appears twice in the candidate

The candidate source has both the named `static const char replay_header[6] = "ITR140";` initializer and hard-coded `memcmp` literals in `get_replay_property` and `load_replay`. In the warning-reachability object, the separate `.rdata+0x128` literal is reached by `.text` relocations in those two functions; `create_replay` separately references the named array. Historical `create_replay`, `load_replay`, and `get_replay_property` refer to the single `_REPLAY_HEADER` owner at `0x4d7dd0` (e.g. `load_replay` at `0x41ce58`, `get_replay_property` at `0x41e2a9`).

A strict isolated compiler probe changed just the two comparisons to use `replay_header`. The extra `.rdata+0x128` literal disappears. In the combined probe with the selected-row warning assignments, all four warning strings remain at historical offsets, `create_replay` stays `FUNCTION_MATCH`, and the six exact neighbors remain exact; `get_replay_property` also stays `FUNCTION_MATCH`. The named array stays at `.rdata+0x3b0`; consolidation does not repair the independent 192-byte header placement gap. `load_replay` remains `DIFFER` due its other body differences. See `header-reference-summary.json` and `combined-summary.json`.

## Retained source evidence

The root confirmed original line-table/disassembly evidence for the selected-row assignments: `draw_replay_selector` line 521 loads `%esi` from `post+4`, then line 538 reloads the selected post into `%edx`, loads `post+8`, and stores it to the local read at line 583. This supports `show_directory = post->directory` and `selected_version = post->version` in the isolated reachability source. No maintained function was edited.

Files in this folder:

- `warning-reachability-source.c` and `warning-reachability-summary.json`: warnings become reachable and restore `Harold` to contribution offset `0x11e`.
- `header-reference-source.c` and `header-reference-summary.json`: comparison literals use the named array; demonstrates literal removal while retaining the exact helper.
- `combined-source.c` and `combined-summary.json`: both evidence-backed changes together.
- `crosswalk.json`: compact COFF/DWARF/relocation and dispatch-reference summary.
