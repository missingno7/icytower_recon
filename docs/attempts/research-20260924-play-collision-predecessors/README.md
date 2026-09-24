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

## Two-predecessor CFG hypotheses queued before compilation (2026-09-24)

The original disassembly shows two independent unsigned `collision_type <= 4` checks: one after `add_floor`, one on the no-floor predecessor. Both invalid edges target one error block; both valid edges reach one shared table dispatch, which reloads `collision_type`. Three equivalent source topologies will test whether GCC preserves that separation:

1. **Nested if/else checks.** Place one unsigned invalid test immediately after `add_floor` and the other in the no-floor `else`; branch both failures to a single error label, then execute one shared switch. This follows the two-way source condition directly.
2. **Valid-edge dispatch.** On each predecessor, branch valid values directly to a shared dispatch label and invalid values to the shared error label. This matches the disassembly's two valid edges converging on the dispatch address.
3. **Named predecessor blocks.** Use explicit `no_floor`, `after_floor`, `dispatch`, `unknown`, and `done` labels, with the original floor-condition selecting one predecessor. Each predecessor gets its own unsigned check and an unconditional edge to the common dispatch on success. This makes the CFG join explicit in source.

All forms preserve the same checks, calls, switch cases, and default error behavior. No code-size objective or fabricated side effect is involved. Compile only after recording these hypotheses; report each result separately and deduplicate by effective code identity.

### Precompile topology correction

Before compiling any variants, the source nesting was reconciled with the observed addresses: `add_floor` and its first check are inside the `if (!itrcheck)` game-update block; the no-floor check is after that block. A successful after-floor check must jump past the no-floor check to the shared dispatch, while failed checks join one shared error block. The three forms below supersede the prior high-level topology descriptions above; no probe was compiled from those preliminary descriptions.

1. **Nested floor path plus trailing no-floor check.** Keep the post-floor check immediately after `add_floor`, branch its success to dispatch, then put the no-floor check after the enclosing `if (!itrcheck)` block.
2. **Positive valid-edge branches.** Use `if ((unsigned)collision_type <= 4) goto dispatch;` on each predecessor, with each invalid edge to the shared error label. This tests opposite branch polarity while retaining the two check sites and exact join.
3. **Named predecessor blocks.** A successful floor-condition edge jumps to `after_floor_check`; paths that skip `add_floor` jump to `no_floor_check`. Both successful checks jump to `dispatch`; both failed checks jump to `unknown`.

The distinction is topological: in all forms the post-floor success bypasses the no-floor check, so the source has two checks on the original distinct predecessors rather than one or two sequential checks on the floor path.

## Two-predecessor probe results (2026-09-24)

The three predeclared forms were compiled as isolated historical-order `game-main` TU overlays. Every compile retained all 63 baseline exact functions with no losses; `new_game` and `run_demo` remained `FUNCTION_MATCH`. All three `play` candidates remained `DIFFER` at 17,444 versus 17,420 bytes, with the same first mismatch at offset 8 (candidate `0x1c`, original `0xfc`).

Effective-code deduplication produced two outcomes: `nested` and `valid_edges` are identical (`dbad870f110b33f8`); `predecessor_labels` is distinct (`c7f86c9317ba5db5`). Each emits two `collision_type` relocations, versus the three original loads documented at `0x4120e5`, `0x412591`, and `0x41259e`. No tested form recovers the independent dispatch reload.

The first observed fold is `main.c.084t.pre` (GCC partial redundancy elimination / PRE), not FRE or RTL CSA. Through `main.c.083t.crited`, GIMPLE contains three distinct reads: one check read on each predecessor plus a dispatch read. PRE replaces the shared switch's global reload with a PHI of the two predecessor check values; at `main.c.084t.pre`, `prephitmp.4649` is `PHI <collision_type.479_615(...), collision_type.479_617(...)>` and the switch consumes that PHI. RTL expansion, `dse2`, and `csa` consequently each show only the two predecessor loads. The full-dump builds reproduce each probe's effective `play` identity and 63/18/1 status counts.

This answers the blocker precisely: source-level representation of both observed checks plus one shared dispatch still lets GCC PRE forward the checked values into the switch selector. The historical binary retains a later independent dispatch load, so the remaining difference requires a compiler-context or source-CFG distinction not represented by these evidence-backed forms. No further structure form is justified by the current evidence; duplicating the dispatch would conflict with the observed shared dispatch. Artifacts: `two-predecessor-*.c`, `make_two_predecessor_forms.py`, `run_two_predecessor_passes.py`, `passes-two-pred-nested/`, `passes-two-pred-labels/`, and the three `build/tu-context/game-main/research-play-two-pred-*/` receipts.

## Audited explicit-predecessor candidate for a possible serial TU_CONTEXT gate

The complete retained candidate is `play-two-predecessor-labels.c`; `tu-context-spec-two-predecessor-labels.json` is a research-only spec using historical order. It is not queued or planned as a production task.

### Why this form

All three tested forms express the evidenced behavior, but `predecessor_labels` is the most auditable representation: it gives explicit `after_floor_check`, `no_floor_check`, `unknown_collision_type`, and `collision_dispatch` blocks. The original instruction CFG independently verifies those predecessor/check/join edges. The source form does not invent a side effect or rely on output size. The exact historical C spelling is not established; only the runtime-relevant branches and shared destinations are evidenced. This is therefore a source-backed research candidate, not an asserted recovery of historical syntax.

### Precise semantic delta from maintained `play`

Maintained `src/main.c` has `if (!itrcheck) { ... add_floor(&map); }`, then continues to `lastY = level` and the collision switch without the two unsigned validation blocks. The candidate adds, after `add_floor`, `if ((unsigned)collision_type > 4) goto unknown_collision_type;`, and adds the same check on the path that skipped the enclosing `if (!itrcheck)`. Successful after-floor flow jumps over the no-floor check; both successful paths join once before `switch (collision_type)`. Both failures share `allegro_message("unknown collision type")`, then continue past the dispatch. The switch default reaches that same message block. These are the two original `collision_type <= 4` predecessor checks and common destinations; the separate original dispatch reload is semantically represented by the C switch, but GCC PRE forwards the checked values into it.

No other behavior or helper was changed for this probe. The neighboring `new_game` and `run_demo` bodies remain exact in the whole-TU receipt.

### Strict receipt and outcome

The exact retained candidate was compiled in historical `game-main` TU order as `research-play-two-pred-labels-20260924`. Receipt: `build/tu-context/game-main/research-play-two-pred-labels-20260924/comparison.json`; concise strict summary: `two-predecessor-results.json`.

- `play`: `DIFFER`, 17,444 bytes vs 17,420 original; first difference offset 8 (`0x1c` vs `0xfc`).
- Whole-TU function states: 63 `FUNCTION_MATCH`, 18 `DIFFER`, 1 `CODEGEN_SIMILAR`; no exact peers lost. `new_game` and `run_demo`: `FUNCTION_MATCH`.
- Candidate `play` has two `collision_type` references vs three in the original.
- First observed merge: `main.c.084t.pre`; PRE replaces the shared switch reload with a PHI of the two checked predecessor values.
- Strict class: `DIFFER`; no function, object, or CU match claim. A serial TU_CONTEXT run would test only context effects and cannot cure or reclassify this body-local mismatch without new evidence.
