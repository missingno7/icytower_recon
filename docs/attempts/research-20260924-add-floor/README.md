# `add_floor` focused investigation (2026-09-24)

## Result

A fresh isolated no-change TU control compiled with locked TDM-2 `-O2` reproduced the current strict result: **4/5 functions match exactly**. `reset_map` (53 bytes), `is_solid` (107), `get_level` (40), and `getFloorData` (107) remain exact. `add_floor` remains `DIFFER`, 608 bytes versus 608 historically. Its first difference is function offset **+297** (historical VA `0x416905`): the original loads `get_demo()->floor_shrink` into `%esi` (`8b b0 8c 00 00 00`), while the candidate loads it into `%edi` (`8b b8 8c 00 00 00`); the following `test` and conditional branch consume that register. This is a register/instruction-selection difference, not proof of a layout-only match.

The fresh comparison reports 4 exact functions and 206 differing byte offsets in `add_floor`. Initialized `.data` (20 bytes) and `.rdata` (8 bytes) contributions match. There are no common allocations or BSS symbols. The full text contribution, object, and CU do not match. The candidate has 60 relocations (9 in `.text`, 51 in debug sections); complete relocation entries are in the comparison receipt below.

## Evidence

- Fresh isolated source control: `map-control.c` (copy of maintained `src/map.c`; no maintained files changed).
- TU context receipt: `../tu-context/game-map/add-floor-control-20260924.json`.
- Full strict CU comparison and relocation inventory: `../../../build/tu-context/game-map/add-floor-control-20260924/comparison.json`.
- Focused current evidence: `../../current/function-evidence/map/add_floor.json`.
- Retained body-attempt history: `../game-map/add_floor.jsonl`.
- Retained TU-order probe: `../tu-context/game-map/luna-map-add-floor-last-context-20260923.json`.

The source/DWARF evidence already aligns on the key relevant facts: `m` is in `%ebx`; `i`, `width`, and `max_w` are signed `int`; `max_w` is scoped to the evidenced inner lexical block. The current source includes the previously established expression and control-flow corrections. The existing add-floor-last TU-order probe retained the same 608-byte mismatch and preserved the four exact peers. The retained body records after the initial empty snapshot all have the same full source-body hash, so they do not represent distinct effective source outcomes.

## Stop reason

No untried, concrete DWARF-grounded body or TU hypothesis remained for the `%esi`/`%edi` allocation. Repeating equivalent expressions or changing source shape without historical evidence would be a cosmetic register-allocation gamble. The blocker is the unresolved register choice at `+297` under the locked compiler and evidenced source/type/context; no exact function or layout-only claim is established. Further work needs new historical source/compiler/context evidence or a separately justified interface/context hypothesis.
