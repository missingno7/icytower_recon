# `handle_player_collision_vector_2` isolated research

Scope: diagnostic work only. Maintained `src/main.c`, current documents, and
`src/recovery.json` were not edited. Every whole-TU probe used locked TDM GCC
4.4.1 with `-O2`, current definition order, and `--no-prototypes` so the
baseline matches the maintained `game-main` declaration context.

## Starting evidence

- Current queue/card: `docs/current/grinder-queue.json` and
  `docs/current/functions/main/handle_player_collision_vector_2.json`.
- Queue status is `DIFFER` / `SOURCE_DIFFER`, MEDIUM, first mismatch at
  function offset `+0x10` (`candidate 0x15`, `original 0x7d`); historical body
  is 1,086 bytes and current candidate is 1,057 bytes.
- Current retained body: `docs/attempts/game-main/bodies/handle_player_collision_vector_2.c`.
- Historical DWARF DIEs (`evidence/census/dwarf-dies.jsonl`) establish
  parameters at source line 3081, `left/right` at 3082, `fx1/fy1/fx2/fy2`
  at 3085, point locals at lines 3088-3097, and intersection outputs at 3100.
  The three historical `line` inlines occupy function offsets 854-891,
  898-939, and 945-999. This is local/control-flow evidence, not recovered
  source text.
- The historical prologue loads `lastX` and `lastY` into EAX/EDI before
  loading `player_id` and `ply`; current candidate loads `lastX`, then the
  globals, and does not materialize `lastY` there. The subsequent x87
  conversion sequence preserves the expected x87 instructions.
- The prior type-context ledger (`docs/attempts/type-context-probes/game-main/handle_player_collision_vector_2.json`)
  records declaration variants as rejected because they change `play`; it
  supplies no candidate body hypothesis.

## Probe outcomes

| Label | Hypothesis | Result |
| --- | --- | --- |
| `research-vector2-baseline-20260923` | Production-equivalent no-edit baseline | 63 exact functions preserved; target remains DIFFER, 1,057 B, first mismatch +16; no effective unchanged-body code changes. |
| `research-vector2-ply2-live-20260923` | Assign/use the DWARF-evidenced `ply2` alias from function entry to keep `lastY` live | Effective output collapses exactly to baseline (same 1,057 B, same +16 mismatch). GCC eliminates the alias. |
| `research-vector2-exact-local-names-20260923` | Express the collision endpoints and output points through historical local names | New effective output, 1,093 B, still first mismatch +16. Effective unchanged-body code changes appear in `handle_player_collision_vector` and `draw_frame`; this is not a safe isolated body candidate. |
| `research-vector2-no-current-x-20260923` | Remove unused `current_x` | Collapses to baseline. |
| `research-vector2-declaration-order-20260923` | Reorder existing declarations in historical order | Changes local stack slots but keeps the +16 mismatch. |
| `research-vector2-direct-player-20260923` | Remove `p`; use `ply[player_id]` in the body | `lastY` is materialized at entry, but GCC chooses EBX, not historical EDI; 1,117 B and still +16. Exact unchanged-body neighbors are preserved. |
| `research-vector2-p-coordinate-only-20260923` | Keep `p` only for point coordinate setup; use `ply[player_id]` for the primary floor sample onward | Collapses exactly to direct-player output. |
| `research-vector2-p-through-floor-only-20260923` | Keep `p` through primary/fallback floor sampling; use direct expressions afterwards | `lastY` stays delayed as in baseline; 1,109 B and still +16. This changes effective code in unchanged functions, so it is diagnostic only. |
| `research-vector2-direct-ply2-20260923`, `research-vector2-direct-declorder-20260923` | Combine direct player expressions with alias/declaration-order variants | `direct-ply2` collapses to direct-player; declaration order has distinct output but still +16. Neither is a match. |

Effective-output dedup was run with `python tools/effective_outcomes.py
game-main handle_player_collision_vector_2 --pattern 'research-vector2-*.json'
--compact`; the saved reports reduce to seven effective identities. The duplicate
`historical-points` diagnostic is not retained as a candidate because its
first source draft used uninitialized aliases; the `exact-local-names` report
is the corrected, semantically equivalent mapping.

## Pointer/register evidence

The historical target DIE list has no child variable `p`; the baseline candidate
does. Historical `lastY` has loclist offset `0x4bf5`: it is the stack argument
initially, then EDI over most of the optimized range, with brief stack-argument
gaps around block boundaries. The historical entry disassembly loads `lastY`
into EDI. Later, historical EBX is used for floor-y retry arithmetic (including
`floor_y + 4`), ruling it out as the long-lived `lastY` register. In the direct
expression pass dump, GCC assigns `lastY` pseudo 87 to EBX at entry; baseline
leaves `lastY` as a stack operand until later. Thus the pointer family identifies
a real optimizer discriminator: retaining `p` through the first floor-data
sample keeps the delayed materialization; removing it from that point onward
moves materialization to entry. This does not explain historical EDI allocation
or the remaining byte/body mismatch.

The full baseline CU inventory is in
`build/tu-context/game-main/research-vector2-baseline-20260923/comparison.json`:
all 82 function records (63 `FUNCTION_MATCH`, 54 masked-equal),
13 object sections, 428 COFF symbols, 93 common allocations, and all 4,424
object relocations. Its initialized-data comparison records `.data` at 6,664
bytes and `.rdata` at 6,648 bytes, including unresolved data relocations.
Those full records are the report for every function, initialized-data
contribution, common/BSS symbol, and relocation. The object and CU verdicts
remain non-matches.

## Artifacts

- Baseline and probe reports: `docs/attempts/tu-context/game-main/research-vector2-*.json`.
- Full object/comparison/pass dumps: `build/tu-context/game-main/research-vector2-*/`.
- Isolated source overlays are in this directory; their labels match the report filenames.

No candidate reached `FUNCTION_MATCH`. The `ply2` live-parameter hypothesis is
eliminated for this source form. The point-local-name mapping demonstrates
compiler sensitivity but leaves the early parameter/register mismatch intact.
Direct player expressions establish a repeatable register-liveness effect but
are not a promotion candidate.
