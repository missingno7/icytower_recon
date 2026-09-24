# `play` collision predecessor guard probe (2026-09-24)

Scope: isolated `game-main` TU probes only. No maintained source or recovery/status file was edited.

## Evidence and hypothesis

The historical DWARF line table assigns both validation fragments and the jump-table load to `main.c:3814` (`python tools/function_lines.py game-main play --source-view 3808 3832`). Original instructions show two predecessor-specific unsigned bounds checks and a separate table-index load:

- After `_add_floor`, `0x4120e5` compares `collision_type` against 4 and branches to the dispatch at `0x41259e`; invalid values fall through to the shared `allegro_message` block at `0x4120f2`.
- The no-floor path at `0x412591` has a second compare, branching to the same error block or the dispatch.
- `0x41259e` then loads `collision_type` into EAX and jumps through the table at `0x4d60c4`.

The retained candidate's switch emitted two references in its `play` body, while the original emitted three. Prior `play-collision-guard-trial-20260923` added a common unsigned guard and still emitted only two; it did not model the `add_floor` predecessor. New hypothesis: a path-local validation after `add_floor`, converging on the switch's shared error label, might preserve an independent dispatch load and recover the third reference.

## Probe and result

`control.c` is the retained body. `split-guards.c` adds the bounds guard only inside the conditional `add_floor` path and routes both that guard and switch default to one shared message label. Both were compiled as a whole historical-order TU with `--no-prototypes`; the probe focused on `play`, `new_game`, and `run_demo`.

- Control `research-play-collision-control-20260924`: 63 exact functions, zero losses; `play` remains `DIFFER` at 17,400 bytes. `new_game` and `run_demo` are `FUNCTION_MATCH`.
- Variant `research-play-collision-split-guard-20260924`: still 63 exact functions, zero losses; `new_game` and `run_demo` remain `FUNCTION_MATCH`. `play` is `DIFFER` at 17,416 bytes versus 17,420 historical; first recorded mismatch remains offset 8 (frame size: candidate byte `0x1c`, original `0xfc`). Whole text remains unequal.
- The variant object still has only two `collision_type` loads in `play`: one load feeds the post-`add_floor` compare; the no-floor load is reused as the switch index. GCC therefore folded the path-local predicate into the switch selector on one predecessor. The intended third load was not recovered. No exact-function or match claim follows from this diagnostic probe.

This eliminates the simple path-local guard rewrite. Further source spelling in this family is not useful without a historical CFG or compiler-pass explanation for why the original keeps its bounds compare separate from the table-index load.

## Artifacts

- `control.c`, `split-guards.c`
- `build/tu-context/game-main/research-play-collision-control-20260924/comparison.json`
- `build/tu-context/game-main/research-play-collision-split-guard-20260924/comparison.json`
- Variant disassembly: `build/tu-context/game-main/research-play-collision-split-guard-20260924/unit.o`
- Historical instruction evidence: original EXE at `0x4120e5..0x4120fe` and `0x412591..0x4125aa`; historical line/block evidence from `function_lines.py` above.
