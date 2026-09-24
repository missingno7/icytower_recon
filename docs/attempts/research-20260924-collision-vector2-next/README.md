# `handle_player_collision_vector_2` recovery checkpoint

## Decision

No new source-level experiment was selected. The prior evidence-backed candidates
already cover the available, historically supported causes for the first target
mismatch: declaration order, point/local spellings, cached versus direct player
access, `ply2` liveness, and the lifetime of the cached player pointer. New
variants in those families would repeat known outputs or require unsupported
aliases. The branch is closed pending new historical source or compiler evidence.

## Reproduced whole-TU controls

Both controls used `src/main.c`, locked `tdm-2` GCC 4.4.1, `-O2` (project
configuration also preserves `-g -mfpmath=387`), historical whole-TU order,
production-equivalent `--no-prototypes`, and the strict whole-CU comparator.
The current-order control was included to verify context parity.

| Label | Order | Exact functions | Target |
| --- | --- | ---: | --- |
| `collision-vector2-next-control-current-noproto-20260924` | current | 64/82 | DIFFER, 1057/1086 bytes, first mismatch +16 |
| `collision-vector2-next-control-historical-noproto-20260924` | historical | 64/82 | DIFFER, 1057/1086 bytes, first mismatch +16 |

The two controls deduplicate to one effective target output (`df653dfc11e305de`).
Neither gains nor loses a strict function match. Their full receipts contain the
complete 82-function CU comparison and object details, including sections,
symbols, common/BSS allocations, and relocations:

- `docs/attempts/tu-context/game-main/collision-vector2-next-control-current-noproto-20260924.json`
- `docs/attempts/tu-context/game-main/collision-vector2-next-control-historical-noproto-20260924.json`
- `build/tu-context/game-main/collision-vector2-next-control-current-noproto-20260924/comparison.json`
- `build/tu-context/game-main/collision-vector2-next-control-historical-noproto-20260924/comparison.json`

Shared maintained source identity: 311,717 bytes,
SHA-256 `2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044`.
The candidate function remains 1,057 bytes versus the 1,086-byte oracle and
strictly DIFFER; no recovery credit is claimed. Historical line inlining is
still one extra `line` edge. The card's raw first mismatch is at +16, where the
current candidate does not copy `lastY` into EDI at entry as the oracle does.

## Established facts and scoped negatives

- Historical `lastY` enters in EDI, then remains live through most of the
  function. The retained IRA dump assigns baseline pseudo `lastY` to memory.
- Removing cached `Tplayer *p` causes an entry copy but chooses EBX, grows the
  body to 1,117 bytes, and remains DIFFER.
- Splitting the pointer lifetime also fails to select EDI and grows the body to
  1,109 bytes.
- Historical local names, declaration order, and direct/cached access forms
  produce multiple compiler outcomes, but all preserve the +16 mismatch. Some
  variants change effective code in unchanged peers; none is eligible for
  promotion.
- The original and candidate retry CFGs agree. Existing reports identify no
  missing retry edge that explains the register choice.
- An earlier auto-prototype control was exploratory only. It is excluded from
  the parity result above; both final controls used `--no-prototypes`.

Prior research and isolated bodies:

- `docs/attempts/research-20260924-collision-vector2/README.md`
- `docs/attempts/research-20260924-collision-vector-next/README.md`
- `docs/attempts/research-vector2-20260923/README.md`
- `docs/attempts/research-20260924-collision-vector2/`
- `docs/attempts/research-vector2-20260923/`
- `docs/attempts/tu-context/game-main/`

## Next discriminating experiment

Resume only if new historical evidence constrains a source form that can cause
IRA to put `lastY` in EDI while preserving the exact 64 peer functions. Otherwise
spend recovery time on another independently recoverable function. Do not run a
declaration/name/pointer spelling sweep: the retained trials already show those
variants either collapse, select the wrong register, or shuffle code while
remaining strict mismatches.
