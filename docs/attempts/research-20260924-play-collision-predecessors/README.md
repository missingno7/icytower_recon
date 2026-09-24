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

## GCC pass trace (2026-09-24)

Diagnostic dump flags were checked on the isolated `split-guards.c` historical-order TU overlay. Locked TDM-GCC 4.4.1 `-O2 -g -mfpmath=387` no-dump, `-fdump-tree-all`, and `-fdump-tree-all -fdump-rtl-all` builds all had `play` at 17,416 bytes (`DIFFER`), 63 `FUNCTION_MATCH`, 18 `DIFFER`, and one `CODEGEN_SIMILAR`. The three effective `play` instruction projections, function relocation and direct-transfer projections, status counts, and complete object relocation counts were equal. Diagnostic flags were byte-neutral for this probe; raw COFF hashes are not used as code equality.

The archived common-guard trial provides the direct load-folding trace. In `main.c.056t.phiprop`, guard and switch have distinct reads: `_598 = collision_type` feeds the unsigned `> 4` check, while `_600 = collision_type` feeds the switch. The first observed pass boundary that removes the switch's second read is `main.c.057t.fre`: the switch operand becomes `_600 = _598`. This is GCC's FRE pass (full redundancy elimination), and it explains why a common bounds check does not preserve an independent table-index load. The pass dumps bracket the change at FRE; they do not expose a deeper internal substep.

For the path-local add-floor trial, optimized GIMPLE through `main.c.126t.final_cleanup` keeps the add-floor check's load separate from the switch-selector PHI. RTL expansion and `main.c.179r.dse2` still show three `collision_type` loads in `play`; `main.c.181r.csa` is the first observed boundary with two. The dropped load is the selector copy on the same add-floor predecessor as its explicit check. The no-floor predecessor has only a selector load in this source, since no no-floor bounds check is present. This is a separate, later RTL fold and does not establish the historical no-floor check's fate.

Outcome: mechanism observed; no source structure hypothesis tested. The common guard spelling and the add-floor-local guard spelling already fail to preserve three reads. A further test would need to restore the historical two-predecessor validation CFG without repeating those guard forms; the present retained body and line/assembly evidence do not yet identify a distinct source-backed mechanism. Candidate remains `DIFFER` (no function/object/CU match claim). The 63 exact peers, `new_game`, and `run_demo` remain preserved in both predecessor probes.

Artifacts: `run_passes.py`, `passes-nodump/`, `passes-tree/`, `passes-treertl/`, `common-guard-passes/tree/`. The `common-guard-passes/treertl/` compile was interrupted before producing an object/comparison; its partial dumps are not used for claims.
