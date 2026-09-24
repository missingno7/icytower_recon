# `init_game` declaration-count control (2026-09-24)

This is one isolated whole-`main.c` GCC 4.4.1 experiment. Maintained source,
generated current state, and the recovery ledger were unchanged. The current
strict baseline is 64/82 exact functions in `game-main`; `init_game` remains
`DIFFER`.

## Question and control

The earlier prototype-context study changed both duplicate declaration count
and later source locations. Here `control.c` is an exact copy of the current
`src/main.c`. `blanked.c` replaces the 81 declaration lines in each of 14
repeated legacy blocks with equal-length spaces. It keeps the first legacy and
final historical blocks. Both inputs have 311,717 bytes and 6,667 lines. Every
retained token keeps its byte offset, line, and column. The historical-order,
no-added-prototype TU builder preserves that invariant: its two compiled
overlays have exactly the same 41,202 changed byte positions as the two input
snapshots, and no other difference. Both builds use the locked `tdm-2` profile.

`generate.py` records the input hashes in `inputs.json` and reproduces the two
local source snapshots from this commit's `src/main.c`. The two strict TU
receipts are retained; compiler objects and pass dumps remain local. No
production prototype count is proposed by this experiment.

## Strict and effective outcomes

| Output | Full 16 blocks | 14 legacy blocks blanked |
|---|---:|---:|
| Exact `main.c` functions | 64/82 | 64/82 |
| `init_game` | DIFFER, 5780/5788, first historical mismatch +14 | DIFFER, 5780/5788, first historical mismatch +14 |
| `init_game` effective identity | `556ba3421a62e9b5` | `313d88cd7b6220b8` |
| `play` | DIFFER, 17396/17420 | DIFFER, 17396/17420 |
| `play` effective identity | `bd705b3885b45e8a` | `d051a652b7fa5f35` |
| Exact gains/losses; new implicit declarations | 0/0; 0 | 0/0; 0 |

Both targets have two distinct effective emitted outcomes. Their sizes, frames,
branch counts, and call counts stay the same within each target. The first
`init_game` instruction difference *between these variants* is at +0x248:
the control emits `mov $1,%ebx` before two zero stores, while the blanked
variant emits the second zero store first. This is separate from each
candidate's historical mismatch at +14. It does not make either target exact.

## Compiler trace

`pass_probe.py` rebuilt each overlay at its original probe path with
`-fdump-tree-all -fdump-rtl-expand`. The dump and no-dump object SHA-256 hashes
match individually, so the diagnostic flags did not change emitted objects.
See `pass-neutrality.json`.

After normalizing only GCC-generated `D.N` labels, the `003t.original`
`init_game` sections are identical. At `023t.ssa`, the first parser-loop PHIs
have the same inputs but different statement order:

| Control | Blanked |
|---|---|
| `check`, `replay_path`, `i` | `replay_path`, `i`, `check` |

At `123t.optimized`, the independent initializations appear as
`i; replay_path; check` in the control and `check; i; replay_path` in the
blanked variant. The code order at +0x248 follows this difference. This trace
shows a declaration-count effect through SSA and optimized statement order
while line and byte locations are held fixed. It does not identify the exact
GCC UID or pass rule responsible, or prove that PHI ordering alone causes the
final instruction order.

## Recovery decision

The experiment removes line/location movement as the explanation for this
specific compiler sensitivity. It changes the **diagnostic focus** to
declaration visibility/UID state at or before SSA. It does **not** select a
historical prototype multiplicity, resolve `init_game`'s +14 parameter-register
mismatch, improve `play`, or justify a source edit or promotion. The next
recovery decision remains to seek historical declaration evidence or a
separately supported upstream source change; arbitrary count tuning would not
be strict recovery.

Smallest artifacts: `inputs.json`, `pass-neutrality.json`, `pass-order.json`,
`generate.py`, `analyze_pass.py`, and strict receipts
`docs/attempts/tu-context/game-main/init-decl-count-{control,blanked}-20260924.json`.
The full compiler dumps and objects are under the corresponding
`build/tu-context/game-main/` labels.
