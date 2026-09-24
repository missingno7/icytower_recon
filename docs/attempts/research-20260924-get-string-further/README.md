# `get_string` bounded follow-up — 2026-09-24

Research-only. No maintained source or recovery ledger changed.

## Control reproduced

`current-body.c` is retained from the no-key-edge report and matches the current `get_string` body (`if (keypressed())` then the shared cycle wait). A fresh isolated whole-TU control used historical emission order and no added prototypes. Receipt: `docs/attempts/tu-context/game-main/gs-further-control.json`; compiler comparison: `build/tu-context/game-main/gs-further-control/comparison.json`.

Control result: compile OK; `get_string` 784/790, first mismatch +91; exact peers 64/82; no gains or losses. Thus the stated current baseline reproduced.

## Follow-up decision

I considered rewriting the equivalent pre-test wait as `for (; !cycle_count; rest(2)) ;`. Before compiling, the only prediction was that a different C loop form might alter GCC loop recognition. The historical CFG and prior pass evidence do not provide a distinct source/CFG fact that predicts this form will rotate the latch. Parent review also confirmed that another syntax-only loop form would repeat the already exhausted family. I stopped before obtaining a compiler result; the partial candidate overlay has no comparison receipt and provides no evidence.

Decision: this experiment does not change the next recovery decision. Close the local loop-spelling branch. Resume only if new source/DWARF/CFG evidence or an upstream-context mechanism predicts a concrete alternate GIMPLE loop shape. No recovery credit claimed.

Candidate spelling, retained solely as an uncompiled note: `for-increment-poll.c`.
