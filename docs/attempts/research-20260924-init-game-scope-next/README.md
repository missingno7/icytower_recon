# init_game joystick DWARF-scope probe — 2026-09-24

Research-only historical-order whole-TU probe. Production source, accepted bodies,
recovery ledger, generated state, and oracle were not modified.

## Question and frozen prediction

Current source kept `pad` and `i` at function scope. Original DWARF places
`gp:Tgamepad *` separately at source lines 1765 and 1779, and a second `i:int`
in the first gamepad configuration arm (line 1772). Before compiling, predicted
a potentially distinct GCC allocation/emission class if these lifetimes affected
reuse. Recovery success required changing the historical `init_game +14` ESI
role while preserving all 64 exact peers.

## Result

The body scopes `gp` separately to each arm and scopes the first arm's loop `i`
locally. Compiled the complete current `src/main.c` TU with locked `tdm-2`
(GCC 4.4.1, `-O2`), historical definition order, no added prototypes, and only
an `init_game` body overlay.

- Exact functions: 64/82 before and after; gained none, lost none.
- `init_game`: DIFFER, 5780/5788 bytes; first historical mismatch remains +14.
- At +14, candidate loads `argc` (`8(%ebp)`) into ESI; historical code loads
  `argv` (`12(%ebp)`) into ESI.
- Differing bytes changed 5321 → 5310; unequal relocation count remains 419.
  The 11-byte reduction is diagnostic only.
- Effective function identity is
  `313d88cd7b6220b8d31a497f6db3f60e6a878f6ae5f2daff3907eaa1ac0dd484`, already
  observed for the declaration-count B/C/D corners. This scope candidate adds
  no new effective class and no target-correlated residue change.

## Decision

Close this joystick `gp`/`i` lifetime hypothesis under the pinned TU context.
It does not alter the next recovery decision for the +14 register mismatch.
Do not promote. Other independently evidenced scopes (for example the original
nested graphics locals) remain separate hypotheses and were not tested here.

## Artifacts

- `plan.md`: predictions and controls frozen before compile.
- `candidate.c`, `generate.py`: retained complete body overlay and reproducible
  extraction/transform.
- `results.json`, `analyze.py`: strict peer set, target residue, and effective
  identity compared with `init-decl-count-control-20260924`.
- Receipt: `docs/attempts/tu-context/game-main/init-game-scope-gp-i-dwarf-20260924.json`.
- Compiler report/object/dumps: `build/tu-context/game-main/init-game-scope-gp-i-dwarf-20260924/`.
