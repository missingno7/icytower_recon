# Isolated `game-map/add_floor` follow-up — 2026-09-24

## Scope and proof boundary

Research-only whole-TU probes. No maintained `src/`, generated current state, recovery ledger, or protected body was edited. Current authoritative card remains `docs/current/functions/map/add_floor.json`: `DIFFER` / `SOURCE_DIFFER`, 608 bytes, first differing byte offset 297 (historical `mov 0x8c(%eax),%esi`, candidate `%edi`). Four neighbors remain strict matches in the TU probes: `reset_map`, `is_solid`, `get_level`, and `getFloorData`. The focused card/receipt must remain the source of truth for current status.

## Evidence read

- Read `AGENTS.md`, `README.md`, `docs/grinder.md`, `docs/progress.json`, `docs/blockers.json`, and `docs/current/grinder-queue.json` before extending research.
- Reviewed the focused card's source scope, function disassembly, local DIEs, lexical ranges, branch context, exact-neighbor list, and routed supervisor reason.
- Read all 12 entries in `docs/attempts/game-map/add_floor.jsonl`. The nine FAST records have the same mismatch. The task's latest record is `BLOCKED_SUPERVISOR`; it documents the prior `-fno-reorder-blocks` rejection and states that prior fixes already preserve unconditional `rand()`, the float comparison before integer conversion, block-scoped `max_w`, and the historical width-ladder order.
- Reviewed `docs/attempts/research-luna-map-floor/findings.md` and `docs/attempts/research-20260923-map-context/findings.md`: condition inversion produced a distinct 613-byte DIFFER; explicit goto/fallthrough and `width=get_demo()->floor_shrink` collapsed to baseline; moving `add_floor` in textual definition order did not change the output.
- Historical DWARF records `i` at function scope, `width` at function scope (declared line 29), and `max_w` at line 83 under lexical block DIE 146337 with ranges at `0x1048`.

## New probes

Both used `tools/tu_context_probe.py game-map src/map.c ... --body add_floor=... --no-prototypes --focus add_floor --no-dumps`, TDM-GCC 4.4.1 `-O2`, with complete surrounding map TU context.

1. `luna-map-maxw-split-init-20260924`: keep `max_w` in its DWARF block and split `int max_w=(int)...` into a declaration and subsequent assignment. This tested whether the initialized-declaration form changes the local's lifetime/allocation while preserving its recorded scope. Result: 608-byte `DIFFER`, first mismatch 297; exact four neighbors unchanged.
2. `luna-map-explicit-zero-test-20260924`: spell the signed-int `floor_shrink` guard as `!= 0`, preserving value and CFG semantics. Result: 608-byte `DIFFER`, first mismatch 297; exact four neighbors unchanged.

`tools/effective_outcomes.py game-map add_floor --pattern 'luna-map-*-20260924.json' --compact` deduplicates the two probes to one effective outcome identity, `1e27f4a8f9c444b6`, with two labels. Both report 206 differing bytes/instructions in diagnostic sequence alignment. For both, `functions_total=5`, `function_matches=4`, and `whole_text_contribution_equal=false`; no promotion candidate exists.

## Blocker / handoff

The additional source-backed declaration-form and explicit signed-zero forms collapse to the same object. Together with the earlier isolated results, this provides no evidence for a new source-level lever consistent with the historical locals and CFG. The remaining mismatch is the historical `%esi` versus candidate `%edi` register/allocation and associated 206-byte code-shape divergence; the prior inversion shows the guard layout can affect that choice, but did not reproduce the original body. Further cosmetic expression variants are not justified by the evidence available here. Current block stands: resolving it requires new original-source/declaration/compiler-context evidence or a fresh RTL/context hypothesis, not acceptance of any probe output.

## Artifacts

- `body-baseline.c`
- `body-maxw-split-init.c`
- `body-explicit-zero-test.c`
- `build/tu-context/game-map/luna-map-maxw-split-init-20260924/comparison.json` and `.o`
- `build/tu-context/game-map/luna-map-explicit-zero-test-20260924/comparison.json` and `.o`
- Earlier comparator context: `docs/attempts/research-luna-map-floor/findings.md` and `docs/attempts/research-20260923-map-context/findings.md`
