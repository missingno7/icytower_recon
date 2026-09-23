# `draw_frame` retained-context follow-up

Scope: isolated historical-order `main.c` research. No maintained source, build state, or recovery status was changed.

## Evidence reviewed

- Focused card: `docs/current/functions/main/draw_frame.json`. `draw_frame` is `DIFFER`, 8203/8518 bytes; the first mismatch is frame allocation (`sub $0x1cc,%esp` vs `$0x1dc`). The historical predecessor `line_alert` is exact, but the whole prefix is not.
- Original function evidence: `docs/current/function-evidence/main/draw_frame.json` and retained trace `docs/attempts/research-20260923-draw-next/README.md`.
- Historical direct `custom.frame[0]` height reads are at function offsets 1924, 2315, 2615, 3391, and 6051. They belong to distinct positive-speed/reset, status-zero accepted, status/pose, negative-speed/reset, and frame-cap predecessors. The indexed pose lookup is separate.
- Original `p_im` DWARF locations cover the positive reset (`0x4099dd–0x409a46`), status/pose (`0x409c9d–0x409d06`), negative reset (`0x409fc1–0x409ff4`), and cap (`0x40aa26–0x40aa58`) sequences. No listed `p_im` location covers the status-zero load at `0x409ba7`; the range resumes at `0x409bb5`. At the cap load, `%esi` is live and is set to 1 only afterward.

## Compiler and candidate outcome

In the retained candidate, `dom1` duplicates the common height load onto `p_im == 8`; `128r.expand` and `179r.dse2` contain five loads. The first saved dump with four is `181r.csa`: it folds the positive status-zero arm into the negative arm's common accepted-path load. This is consistent with the original's single status-zero accepted-path read and does not account for the separate missing speed/reset predecessor.

The combined historical-order probe records `csa-context-speed-path-height-20260923.json` and `csa-context-live-speed-height-20260923.json` both preserve 63 exact functions, with `new_game` and `run_demo` exact and no exact-function losses. The first retains four direct frame-zero reads at 8204 bytes because later common assignment makes the branch-local values dead. The second emits three at 8040 bytes and changes call count 107 to 104. The cap-order probe in `research-20260923-draw-next/README.md` deduplicates to the 8203-byte status-zero-sign candidate and also preserves 63 exact functions.

## Boundary

No new source probe is justified by the retained evidence. Status-zero duplication is already explained by the original shared accepted path and GCC's observed factoring. Positive/negative speed-path computations already have two discriminating historical-order probes: one is dead, while bypassing the later common computation changes topology and loses a read. The remaining question is the historically faithful CFG/liveness join that preserves those reset computations without changing surrounding routes. Current line-table and DWARF evidence does not identify the required source distinction, and the saved pass dumps only bracket the status-arm fold between `179r.dse2` and `181r.csa`.

Next progress requires new evidence for the reset-arm state distinction or predecessor join (for example, additional historical source/CFG or an informative pass snapshot inside that interval). Do not add cosmetic duplicated reads or repeat the tested arm spellings.
