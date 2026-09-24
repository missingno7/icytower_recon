# `add_floor` pass-level follow-up — 2026-09-24

Research only. No maintained source, generated current state, recovery ledger, or protected body was edited.

## Strict results

- `mapfloor-pass-baseline-20260924-agent`: `add_floor` remains `DIFFER`, 608/608 bytes, first mismatch +297; four neighboring functions remain exact.
- `mapfloor-pass-invert-20260924-agent`: `add_floor` remains `DIFFER`, 613/608 bytes; four neighboring functions remain exact.
- Both probes used the locked TDM-2 `-O2` TU path with `--no-prototypes`; their receipts and complete comparison reports are in `docs/attempts/tu-context/game-map/` and `build/tu-context/game-map/`.

## New pass evidence

Compared the two retained candidate RTL snapshots around `get_demo()->floor_shrink`:

- At `.181r.csa`, both forms have the same memory compare against zero and the same implicit scratch-free shape. The only local difference is the branch predicate/target: baseline `eq` branches to label 129, inverted form `ne` branches to label 79. This captures the corresponding CFG inversion before the later scratch-register insertion.
- At `.182r.peephole2`, GCC inserts a load of `floor_shrink` into `%di` for baseline and `%si` for the inverted form, then tests that register. This pins the candidate-side register-choice divergence to the peephole2 interval after the identical pre-insertion memory compare. It does not identify which internal heuristic or historical source form caused the original `%si` choice.
- The source/type evidence still pins `floor_shrink` as signed 32-bit `int` at `Treplay` offset 140, and historical locals to `i`, `width`, and inner-block `max_w`. `max_w` split initialization and explicit `!= 0` already converge to the baseline effective outcome `1e27f4a8f9c444b6` (two probes, one output).

## Stop point and next discriminator

The local spelling family has converged, while branch inversion is the only tested CFG form that changes the scratch register; it also changes code layout and remains five bytes too long. The current evidence supports stopping body/type spelling probes. A next investigation should inspect the locked compiler's peephole2 `peep2_find_free_register` selection and its live-register/cursor inputs for these snapshots, or locate independent original block/declaration evidence that predicts the historical CFG. Historical RTL is unavailable, so this comparison establishes only where the candidate variants diverge from each other, not a historical cause or a layout-only match. Do not promote either probe.
