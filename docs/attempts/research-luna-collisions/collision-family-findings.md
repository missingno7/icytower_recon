# Collision family research — 2026-09-23

Scope: isolated `tu_context_probe.py` runs in historical definition order. No maintained source, `src/recovery.json`, current cards, or promotion state was edited. The current generated ledger remains 208 `FUNCTION_MATCH`, 43 `DIFFER`, 2 `CODEGEN_SIMILAR`.

## Probe receipts

- Baseline: `docs/attempts/tu-context/game-main/research-luna-collision-baseline-20260923.json`; CU comparison and object are in `baseline/`.
- DWARF-shaped vector candidate: `docs/attempts/tu-context/game-main/research-luna-collision-vector-evidenced-20260923.json`; source is the retained `docs/attempts/game-main/bodies/handle_player_collision_vector.c`; comparison and object are in `vector-evidenced/`.
- Anonymous x-value lifetime probe: `docs/attempts/tu-context/game-main/research-luna-collision-vector-cache-x-20260923.json`; source is `vector-cache-x.c`; comparison and object are in `vector-cache-x/`.
- Original executable disassembly slices: `*-original-disasm.txt`; complete saved vector asm in `vector-original-disasm.txt`.

## Results

- Historical-order baseline compiles the current `game-main` TU with 62/82 strict function matches. All five collision handlers are `DIFFER`. No gains or losses versus the pre-probe historical-order CU. `run_demo` is `FUNCTION_MATCH`.
- `handle_player_collision_vector` baseline is 1021/1071 bytes with candidate stack allocation `0x9c` vs historical `0x8c`; first mismatch is frame byte offset 8.
- The retained evidence-shaped vector body names the located locals, removes the unsupported cached player pointer, and reuses already-held call arguments. It compiles to 1007/1071, restores the historical `0x8c` frame, and moves the first mismatch to offset 13: candidate loads `lastY` into `%ebx`, original loads it into `%esi`. It remains `DIFFER`; all-CU losses/gains are empty and `run_demo` remains exact.
- Original vector disassembly establishes the historical value lifetime: it stores player `x` as a double at `-0x50(%ebp)` before `getFloorData`, converts cached `y` before that call into `%edi`, then uses `%edi` as `ply1` (incremented once) afterward. `fy1` is loaded into `%ebx` after the call and `lastY` stays in `%esi` for line-intersection arguments.
- An isolated `double cached_x` representation of the anonymous `-0x50(%ebp)` value compiles to 1003/1071. Frame remains `0x8c`; first mismatch remains the `lastY` register at offset 13. Fixed-offset raw differences decrease 954→863, proving a new effective compiler outcome and that the missing x lifetime affects later code, but it is not an exact candidate.
- `handle_player_collision_original` is 449/456 with 154 raw fixed-offset difference positions; the offset-205 first byte is a destination-register choice for the status-path `ply[player_id]` load (`%eax` historical vs `%edx` candidate), not a 7-byte layout-only gap.
- Other baseline frame facts: `_old` historical/candidate `0x3c`/`0x4c`; `_combo` `0x9c`/`0x7c`; `_vector_2` `0x9c`/`0x9c`, but candidate delays the `lastY` load while the original loads it into `%edi` at entry. These are body/source-shape mismatches, not proven layout-only cases.

## Family fact established

For `_combo`, both historical `line_intersect` argument builds reuse the same existing values: `%ebx` carries `fy1` for both `ay`/`by`, `%edi` carries `ply1` for `cy`, and `%esi` carries `lastY` for `dy`. The four no-location DWARF names `fy2`, `ply2`, `pry1`, `pry2` therefore need no independent copies in the source; call-argument construction proves reuse. This parallels the earlier `_vector` finding. Full original call windows are preserved in `combo-original-disasm.txt`.

## Remaining blocker and next useful experiment

Local source changes now expose two mechanisms: the historical pre-call value lifetimes (cached x and y) and a separate register-allocation difference at the vector entry (`lastY`: `%esi` vs `%ebx`). The first is partially represented in the anonymous x-cache probe; the second survives both tested vector shapes, so more cosmetic spelling variants are not justified. Next discriminating work should inspect historical lexical declaration/order evidence for the x/y temporaries and compare caller/TU predecessors only if a probe changes the target code without changing its body. Do not claim any collision function recovered; all five remain strict `DIFFER`.
