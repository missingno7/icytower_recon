# `draw_scroller` historical-order recheck — 2026-09-24

## Question and prediction

Could placing the four unchanged definitions in historical source declaration order change the six call-argument register choices while retaining all exact peers? Prediction: if definition order is causal, the target's effective instructions or strict peer set will differ from a fresh current-order whole-TU control. Both probes use `tdm-2`, `-O2`, no generated prototypes, and the complete `game-scroller` translation unit.

## Result

The experiment adds no new outcome class. Historical `DW_AT_decl_line` order is `init_scroller`, `draw_scroller`, `scroll_scroller`, `restart_scroller`, which is already the maintained source order. Both probes retain 3/3 exact neighboring functions; `draw_scroller` stays 396 bytes and `DIFFER`. The historical and candidate emission orders are both `scroll_scroller`, `restart_scroller`, `draw_scroller`, `init_scroller`; the target remains after exact `restart_scroller`. There are no gains, losses, or effective code changes versus the control.

This confirms the local order branch is exhausted; it does not explain the six mismatches at offsets 93, 96, 100, 103, 107, and 110. The outcomes duplicate the historical-order class already archived in `research-20260924-scroller-context-causal` and `research-20260924-scroller-luna-high`. No recovery decision changes: keep the strict status `DIFFER` and do not continue source-order or register-spelling sweeps. The next useful evidence would be a validated historical object with relocations and compiler provenance, or historical RTL/cgraph/pass dumps around `restart_scroller` and the first vertical `set_clip_rect` call.

## Artifacts

- `baseline.c` and `historical-order.c`: identical source snapshot, SHA-256 `2d4cfaa016569e53ce0acf179bc2fa0b8c00872f9e1885b574cdd97c50d22d5e`.
- `current.json` and `historical-order.json`: fresh whole-TU receipts, source/toolchain identities, strict function outcomes, emission-order and peer summaries.
- Current focused card: `docs/current/functions/scroller/draw_scroller.json`.
- Prior independent order/control evidence: `docs/attempts/research-20260924-scroller-context-causal/README.md` and `docs/attempts/research-20260924-scroller-luna-high/README.md`.

No maintained source, current generated state, or recovery ledger was edited. This is diagnostic compiler-context evidence only; no function match is claimed.
