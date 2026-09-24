# init_game joystick-scope discriminator — 2026-09-24

## Hypothesis and predictions (frozen before compile)

The current body keeps `pad` and `i` at function scope. Original DWARF instead
records `gp` at source lines 1765 and 1779 in separate lexical blocks, plus a
second `i` at line 1772 in the `gamepad.txt` arm. Test one semantics-preserving
scope reconstruction: declare a `Tgamepad *gp` in each branch, and give the
first arm's button loop its own `int i`. These variables are only read within
their respective blocks; the outer `i` remains for the parser/high-score/wait
loops.

Prediction: if these original lifetimes affect GCC 4.4.1 allocation, the
effective `init_game` emission may differ from the control. Recovery-facing
success specifically requires changing the historical +14 ESI argv/argc
residue while preserving all 64 exact peers. A changed effective function
class that leaves +14 unchanged is only a scoped diagnostic and closes this
local hypothesis unless a new target-correlated residue appears. An identical
effective outcome rules out this variable-scope mechanism under the pinned
whole-TU context.

## Controls

Use current `src/main.c` as the sole whole-TU base; replace only the complete
`init_game` body; compile with locked tdm-2, historical definition order, and
no added prototypes. Check source/context hashes and exact peers against the
fresh 64/82 declaration-count control before interpreting results. Do not
change production source, ledgers, or recovery status.
