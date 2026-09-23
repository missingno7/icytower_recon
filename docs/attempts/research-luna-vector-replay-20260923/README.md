# `handle_player_collision_vector` lifetime replay (2026-09-23)

## Result

The combo cache finding transfers in part. Historical vector disassembly also caches player x as a double near entry and materializes integer endpoints after the `getFloorData` retry. It does **not** cache both x and y in the same way as combo: historical `ply1` is the y conversion value and lives in EDI from the post-increment point over almost the rest of the function, while the x double is stored and converted later. `fy2`, `ply2`, `pry1`, and `pry2` have no DWARF locations; the original call argument builds show direct reuse of `fy1`, `ply1`, and `lastY` registers, as documented in the prior vector finding.

The vector2 pointer-lifetime result is only a partial analogy. It shows that retaining/removing the candidate `Tplayer *p` can change when `lastY` is materialized in vector2; vector’s strongest direct live-range evidence is instead `ply1` (converted player y) in EDI across the floor-data call and later intersection uses. Historical vector has no `p` DIE; its current body does use `p`. These are distinct values and distinct functions, so the vector2 result does not by itself explain vector’s allocation.

## Current-order probes

Ran locked GCC 4.4.1 `tu_context_probe.py` in current order with `--no-prototypes`; all variants preserved the production exact-function set at **63/82**, with no gains or losses.

| Variant | Candidate / historical | First difference | Frame | Effective result |
|---|---:|---:|---:|---|
| Production body control | 1021 / 1071 | +8 | `0x9c` | DIFFER |
| Retained DWARF-shaped evidence body | 1007 / 1071 | +13 | `0x8c` | DIFFER |
| Retained body plus entry cached-x double, used for both endpoint conversions | 1003 / 1071 | +13 | `0x8c` | DIFFER |

The last probe is source-backed by the original entry-time double load and later conversion. It changes the retained candidate output (not a match); the candidate frame matches the original reservation, but its code and first mismatch remain different. It does not support attributing vector’s entire code gap to x-cache lifetime. No maintained file or recovery state was modified.

## Evidence and artifacts

- Current card: `docs/current/functions/main/handle_player_collision_vector.json` (DIFFER, 1021/1071; candidate frame 0x9c vs original 0x8c)
- Original DWARF ranges and disassembly-derived evidence: `docs/current/function-evidence/main/handle_player_collision_vector.json`
- Prior source/CFG/live-range findings, including the EDI `ply1` range and unnamed call-argument reuse: `docs/attempts/game-main/handle_player_collision_vector-finding.md`
- Related vector2 pointer-lifetime results: `docs/attempts/research-vector2-20260923/README.md`
- Comparison family: combo lifetime note `docs/attempts/research-luna-combo-context-20260923/README.md`
- Isolated inputs: `probes/current-control.c`, `probes/retained-evidence-body.c`, `probes/retained-with-cached-x.c`
- Probe receipts: `docs/attempts/tu-context/game-main/luna-vector-current-control-20260923.json`, `luna-vector-retained-current-order-20260923.json`, `luna-vector-cache-x-current-order-20260923.json`
- Full function/CU reports and object files: `build/tu-context/game-main/luna-vector-{current-control,retained-current-order,cache-x-current-order}-20260923/`

The strongest unresolved mechanism remains source-level scheduling of the y conversion that becomes `ply1` and survives `getFloorData` in EDI. The prior one-shot source form that computes/reuses `ply1` moved code size only from 1000 to 1007 in historical-order experiments; this current-order replay also remains DIFFER. Further pointer-local experiments are not justified by this evidence alone.
