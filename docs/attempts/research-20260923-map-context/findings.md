# Isolated map-floor research — 2026-09-23

## Strict state

`game-map/add_floor` remains `DIFFER` / `SOURCE_DIFFER`, with the current maintained candidate still 608 bytes and the first difference at offset 297 (historical `mov 0x8c(%eax),%esi`, candidate `%edi`). This research did not produce a promotion candidate. The four exact neighboring functions (`reset_map`, `is_solid`, `get_level`, `getFloorData`) remained strict matches in every TU probe. Whole-text equality was false.

`getFloorData` is already current `FUNCTION_MATCH` at 107/107 bytes; the stale B009 task is satisfied and must not be repeated. Historical definition order is `reset_map`, `add_floor`, `is_solid`, `get_level`, `getFloorData`.

## Prior attempt classes reviewed

- Nine prior FAST attempts in `docs/attempts/game-map/add_floor.jsonl` retained the same offset 297 `%edi` versus `%esi` mismatch; the supervisor block records no further DWARF-supported body lever.
- Historical-order baseline retained four exact neighbors and `add_floor` DIFFER at 608/608 bytes.
- Inverting the shrink condition selected the historical `%esi` guard load, but changed branch layout and produced a 613-byte function with a new mismatch at offset 306.
- Explicit `goto` fallthrough normalized to the 608-byte baseline output.
- Moving `add_floor` to a different textual definition position did not change its output or the four neighboring matches.
- The prior compiler-flag trial is documented as rejected and is not repeated.

## New causal experiment

Tested `width=get_demo()->floor_shrink; if (width)` as a use of the existing DWARF local, preserving the source branch shape and historical definition order. GCC 4.4.1 `-O2` emitted the exact same 184-instruction `add_floor` machine-code sequence as the baseline capture: 608 bytes, identical instruction records, same offset 297 mismatch, and the same `peephole2` scratch choice (`di`). The extra temporary assignment is eliminated before it can affect allocation. This rules out routing the guard through `width` as a register-allocation lever.

All three strict neighboring functions plus `getFloorData` stayed `FUNCTION_MATCH`; their historical predecessor context was retained. Source body and compiler dumps are isolated under this directory. No maintained source, generated state, ledger, or external research repo was edited.

## Artifact paths

- `add_floor-guard-through-width.c`: exact body overlay for the new trial.
- `game-map/luna-map-baseline-capture-20260923.json` and corresponding `build/game-map/.../comparison.json`: fresh baseline and focused comparison.
- `game-map/luna-map-width-guard-20260923.json` and corresponding `build/game-map/.../comparison.json`: new trial and focused comparison.
- Each build folder also retains `unit.o`, `.cgraph`, `.r.csa`, `.r.peephole2`, DWARF, and compile dependencies.
- `probe-runner.py`: small wrapper redirecting all probe outputs into this unique directory.

## Blocker and next discriminating experiment

The useful source-level result remains the same: selecting `%esi` through branch inversion requires a CFG layout that diverges from the historical body; equivalent guard assignment and explicit-flow spellings collapse to the baseline. Definition order does not account for the register selection. Further cosmetic expression variants have no support from the current DWARF/card evidence.

The remaining blocker is the coupling between historical CFG/block layout and GCC's register allocation at the `floor_shrink` guard. A next investigation should compare original/candidate RTL or obtain new evidence for the original branch form. Historical RTL is not available from the PE fixture, so the smallest useful next step is inspect any newly located original-source/declaration evidence; absent that, route this to supervisor rather than repeat body guesses. The existing required locals are only `i`, `width`, and nested `max_w`.
