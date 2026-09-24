# `main.c` FLDAdSpot type view review (2026-09-24)

## Decision

Close this type-view branch. The maintained inline declaration already has the
owning-CU historical member types and layout: `char *` at offsets 0, 4, and 8,
`float` at 12, total size 16. The source-backed repair from the earlier
`view_fld_adspot_FLDAdSpot` task changed the three `const char *` members to
`char *`; its fresh whole-CU interface receipt reported no emitted
code/data/BSS/symbol/relocation changes and was promoted. The current pending
`view_main_FLDAdSpot` card proposes replacing this inline declaration with the
generated header, which adds no historical type evidence.

The generated-header substitution was tested against the latest source in an
isolated whole-TU probe. It retained 64/82 exact functions, the same 79/82
historical predecessors, and produced no gains or losses. The summary reported
raw code differences in `init_game` and `play`, while effective comparison was
unavailable for those functions and several others. It therefore does not
establish emission preservation and grants no recovery credit. The prior
header-replacement interface attempt also failed the full emitted-contribution
gate; its diagnostic identifies `WinMain` literal displacement and `_mangled_main`
code changes.

## Probe inputs and receipts

- Maintained source: `src/main.c`, 311,717 bytes,
  SHA-256 `2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044`.
- Canonical header: `include/recovered/FLDAdSpot.h`, SHA-256
  `3e5263b31865a61ca566a7068f2a1cb99a30f61d1bef826fef67a4f6b70f382b`.
- Isolated header candidate: `main-header-include.c`, SHA-256
  `3748894e1dc9afba5cec3db371c3ba17fafdfc3d1a66e1c35fe9e3bbc783fe86`.
- Current-order control summary: `docs/attempts/tu-context/game-main/research-20260924-view-main-fldadspot-control.json`;
  object `build/tu-context/game-main/research-20260924-view-main-fldadspot-control/unit.o`,
  SHA-256 `d02910bb9668cc48defa04c8350c2be011d5a320cbfe90aa5739c0fc2f54ad96`.
- Header candidate summary: `docs/attempts/tu-context/game-main/research-20260924-view-main-fldadspot-header-latest.json`;
  strict comparison `build/tu-context/game-main/research-20260924-view-main-fldadspot-header-latest/comparison.json`;
  object SHA-256 `6a41ece8970ab87a79b6e7a76366358d241b1cc71ca5ef528562876d35d95035`.
- Both probes used `tools/tu_context_probe.py`, current definition order,
  `--no-prototypes --no-dumps`, and the locked `tdm-2` whole-main-TU compile.
  Both controls report 64/82 exact functions and no new implicit declarations.
- Earlier header-replacement failure receipt:
  `docs/attempts/interface-diagnostics/view_fld_adspot_FLDAdSpot/game-main-ae0b87874863e43dc33a2580709916e40284fbd2fef8b527ee2e066e723811ee.json`.
- Earlier successful inline-member correction:
  `docs/attempts/interfaces/view_fld_adspot_FLDAdSpot.jsonl` (`PROMOTED_CANONICAL_VIEW_MATCH`).

## Prediction and scoped negatives

The discriminator is whether the generated-header form adds any recovered type
facts or strict exact functions while preserving every existing exact peer and
the full object contributions. Expected result: no type fact beyond the current
inline layout and no strict function gain. Observed: no gains, no losses, same
64/82 set; raw differences remain in `init_game`/`play`, and the full text
contribution is unequal. Since effective comparison is unavailable for those
functions, this probe cannot be described as an emission-preserving header
repair.

No member-type, layout, body, declaration-order, or compiler-flag variants were
tested. No production source, generated current file, or recovery ledger was
edited. Next discriminator: none for this branch absent new historical evidence
that identifies a distinct `FLDAdSpot` declaration in this owning CU; continue
with an independent recovery task.
