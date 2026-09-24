# `create_profile` follow-up decision (2026-09-24)

## Result

No new compile was justified in this bounded follow-up. The fresh generated focused card remains `DIFFER`, 823 bytes versus 823, with the first strict byte mismatch at function offset `+69`: the original loads `overwrite` from `[ebp+12]` into ESI and tests ESI; the candidate loads it into EDI and tests EDI. The focused strict card records 11/17 exact functions in `game-profile`, 823/823 function bytes for this body, and no relocation mismatches. No source, recovery ledger, or generated current state was changed here.

I mechanically regrouped the retained 2026-09-24 `create_profile` probe set with:

```powershell
python tools/effective_outcomes.py game-profile create_profile --pattern 'create-profile-*20260924*' --response --compact
```

It found 16 probes and one effective function outcome, `e9b312015907a283`: all remain `DIFFER`, 823 bytes, first mismatch `+69`, with 2 differing bytes and 0/23 unequal relocations. The effective group retains 11/17 exact functions. This grouping is search evidence, not acceptance.

## Previously tested causal families

The retained probes already cover four equivalent guard forms, local declaration ordering/grouping, current versus historical TU emission order, canonical versus alias pointer spelling, local versus `sizeof` type spelling, and the `flash`/`start_floor` independent initialization order. They collapse to the same current function output. The candidate-only `-fdump-rtl-ira` observation shows `overwrite` still entering from `[ebp+12]`; the final EDI selection is at reload/code emission. A diagnostic-only dump flag was checked against a byte-identical control object. There is no original IRA/reload/pass dump to compare.

Source-order evidence places exact `delete_profile` immediately before `create_profile` in both candidate and history. Existing probes of TU order do not move the mismatch. The focused source/DWARF inventory gives no alternate parameter type, nested scope, or local alias that explains the ESI choice.

## Prediction and next-decision impact

Before compiling, the prediction for another guard, local declaration permutation, typedef spelling, or current/historical function-order variant would be the already-seen effective output `e9b312015907a283`, leaving the same +69 register pair and all 11 exact peers. These dimensions have been tested directly; selecting another spelling in one of them would not discriminate the remaining explanation. I therefore did not spend another compile on that family.

The next useful discriminator requires new evidence about the historical GCC allocator input or pass state: ideally a historical GCC IRA/reload dump, or an independently authenticated original profile object plus exact compiler/build context. Without that evidence, a parameter temporary or artificial lifetime change would be unsupported and could manufacture register pressure rather than recover source. Thus this follow-up does **not** change the next recovery decision: keep `create_profile` unresolved and do not promote it. The local source-spelling search is converged; no strict win or recovery credit resulted.

## Artifacts

- Current source/card: `src/profile.c`, `docs/current/functions/profile/create_profile.json`.
- Batched guard/declaration/order and candidate IRA evidence: `docs/attempts/research-20260924-create-profile-batch/README.md` and its `passes/` artifacts.
- Canonical type batch: `docs/attempts/research-20260924-create-profile-luna-high/README.md`.
- Retained effective-outcome receipts: labels matching `create-profile-*20260924*` under `build/tu-context/game-profile/` and their diagnostics under `docs/attempts/tu-context/game-profile/`.

Current maintained source SHA-256: 6174D0AA0DE3C0D8BEF5338C50DA012B8B24E8403C7B2344878C4C73E4B9CF90.
