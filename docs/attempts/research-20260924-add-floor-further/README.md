# `add_floor` bounded follow-up — 2026-09-24

## Decision

No new GCC compile was run. The retained evidence does not support a source/context variant whose predicted effect would recover the original `+297` register choice while retaining the historical CFG. Another speculative compile would not discriminate an evidenced historical explanation.

## Pinned relevant state

- Current focused card: `docs/current/functions/map/add_floor.json` (`DIFFER`, 608 bytes, first historical difference `+297`, original `%esi`, candidate `%edi`).
- Current source body identity in the retained control record: `src/map.c` SHA-256 `8d0c526c4080275819460dbf680d2fde58761562a24d8f59e055e3e054ac5a82` (3108 bytes).
- Exact neighboring functions in the whole map CU: `reset_map`, `is_solid`, `get_level`, and `getFloorData`.
- Existing whole-TU control: `docs/attempts/research-20260924-add-floor/README.md`, receipt `docs/attempts/tu-context/game-map/add-floor-control-20260924.json`.

## Discriminating evidence already present

The baseline and guarded-inversion RTL snapshots agree at `.181r.csa` on the memory compare and differ in branch predicate/target. At `.182r.peephole2`, baseline inserts `%di`, inversion inserts `%si`. The full-TU prefixes have the same preceding peephole scratch choices, so the earlier-TU cursor explanation is not supported for this pair. The internal peephole eligibility/live-register/rejected-register state is absent from the current dumps.

The inversion is not a historical candidate: it is 613 bytes versus 608, has its first mismatch at `+306`, and changes branch layout. The baseline remains 608 bytes with first mismatch at `+297`. Thus matching `%esi` under the inverted form does not distinguish the historical residue at `+297` from the surrounding CFG mismatch.

DWARF supports only `i`, `width`, and inner-block `max_w` as locals; their types and `max_w` scope match current source. Prior split initialization, explicit zero test, local reuse through `width`, source-order, and declaration-context probes already converge to baseline. The only useful new experiment would require a diagnostic TDM GCC build that records `peep2_find_free_register` live-before, cursor, and rejected-register state. That would explain the candidate's mechanism, but without historical RTL or source evidence it still would not select a historical source reconstruction.

## Effect on next recovery decision

No change. Keep `add_floor` unresolved at the supervisor/compiler-diagnostic boundary; do not continue body spelling variants or treat the inverted `%esi` as recovery. Revisit only if historical source/CFG evidence or an instrumented locked compiler yields a new discriminating fact.

## Receipts reviewed

- `docs/attempts/research-20260924-add-floor/README.md`
- `docs/attempts/research-20260924-add-floor-followup/README.md`
- `docs/attempts/research-20260924-map-add-floor/findings.md`
- `docs/attempts/research-20260924-map-add-floor/pass-analysis-20260924-agent.md`
- `docs/attempts/research-20260924-map-add-floor/cursor-eligibility-20260924-agent.md`
- `docs/attempts/research-20260924-ira-systemic/README.md`
