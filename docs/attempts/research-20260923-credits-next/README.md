# `show_credits` follow-up (2026-09-23)

## Result

No strict candidate. One new isolated TDM-2 `-O2` probe changed the `while` loop to a `for` loop with `vol-=vol_step` in the update clause. It emitted the same effective function identity as baseline: `7f11e57156718292`, 654 bytes versus the historical 634. The focused TU receipt is `docs/attempts/tu-context/game-main/luna-show-credits-update-clause-20260923.json`; the object and comparison are under `build/tu-context/game-main/luna-show-credits-update-clause-20260923/`.

Candidate source: `update-clause.c`.

## What the probe establishes

Moving the decrement from the loop body to GCC's `for` update edge does not change the effective output. This is consistent with the existing pass evidence: ordinary `while` and explicit-goto inputs reach the same loop-header-copy (`ch`) behavior, and the sink pass moves `vol_43 = vol_300 - vol_step_4` beyond the copied Esc/count test. A guarded `do` starts with two tests in original GIMPLE, avoids another `ch` copy, but still has the sink move the subtraction. The emitted outcomes remain 654 bytes for baseline/goto/update-clause and 658 bytes for the guarded-do pair. The two historical ledger forms remain 627 and 624 bytes but have different iteration ordering and are not CFG candidates.

The historical source-line map places `show_credits` at `main.c:5027-5036`; its signature, local types (`double vol`, `double vol_step`, signed `int gc`, `BITMAP *logoBMP`), and call set are already resolved in the focused card. Definition order/context is not implicated: position 48 and exact predecessor `show_instructions` are stable, and historical-order probes did not change the outcome. Treat byte 26's `_screen` operand as data layout, not a body mismatch.

## Next useful direction

The source-spelling family has converged. Further useful work should inspect historical build provenance or prove a compiler-pass/context difference that explains why the original retains decrement-before-guard ordering. A diagnostic pass toggle may localize causality, but it must remain labeled as diagnostic and must not be accepted as a build option or function-match evidence. No body change or recovery promotion was made.
