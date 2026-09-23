# `handle_player_collision_combo` lifetime signature follow-up (2026-09-23)

## Question and result

This isolated follow-up checked whether combo has the `handle_player_collision_old` `dX`/`lastX` register-lifetime signature. It does not. The current focused card is `DIFFER` (candidate 1381 bytes, original 1390; first mismatch +6; stack-frame class). Combo has no `dX` local. Its original `lastX` and `lastY` location lists describe frame/stack locations (`lastX`: `DW_OP_fbreg 0` with EBP+8 ranges; `lastY`: `DW_OP_fbreg 4` with EBP+12 ranges), not the EDI-resident `dX`/register-held `lastX` pattern documented for `collision_old`. Therefore that local mechanism does not transfer.

Combo's own stronger source evidence is an entry-time double snapshot followed by deferred integer geometry materialization. Original disassembly loads `ply[player_id]->x` and `->y` to stack doubles at offsets +12..+32 before color creation and collision calls. Later it converts these values for the foot checks and the intersection geometry. Four historical geometry integers (`plx1`, `plx2`, `prx1`, `prx2`) occupy fixed slots; their writes are after floor-data retry and before debug drawing. `ply1` has loclist ranges. `fy2`, `ply2`, `pry1`, and `pry2` have no `DW_AT_location`; this report makes no value inference from those names.

## Corrected current-order whole-TU probes

All probes used `game-main`, current definition order, `--no-prototypes`, and an isolated complete-body overlay. Exact neighbors remained **63 before and 63 after**, with no gains or losses. None edited maintained source or recovery state.

| Variant | Candidate / historical | First difference | Frame allocation | Result |
|---|---:|---:|---:|---|
| Current-body control | 1381 / 1390 | +6 | `0x7c` | DIFFER |
| Entry cached x/y doubles, used at all coordinate conversions | 1193 / 1390 | +12 | `0x9c` | DIFFER |
| Cached doubles plus five evidenced int geometry locals used by intersections | 1141 / 1390 | +8 | `0xac` | DIFFER |
| Same geometry locals also used in debug drawing | 1141 / 1390 | +8 | `0xac` | DIFFER, same effective output as preceding row |

The actual-use cached-double candidate has the historical `0x9c` frame allocation, but its function bytes still differ substantially and do not establish a match. The two geometry variants deduplicate to the same 1141-byte output (same candidate bytes and relocations), so moving those same values through the debug calls has no further effect. Three distinct candidate output identities were observed across the four corrected rows. No strict function match was found.

### Artifact correction

The first-pass file `probes/cache-xy-both.c` only declared and assigned the cache variables; it did not use them. Its output happened to be the same 1193-byte candidate as the corrected actual-use cached-x/y variant, but must not be cited as evidence that using the values caused that output. The corrected file is `probes/cache-xy-used-v2.c`; its cache identifiers occur at all original `(int)p->x/y` conversions. The initial geometry control in `geometry/manifest.json` is the earlier dead-cache input; use the `v2` variants and receipts listed below for the valid comparison. Previous receipts are retained as experiment history, not overwritten.

## Artifacts

- Current card: `docs/current/functions/main/handle_player_collision_combo.json`
- Original DIE evidence: `docs/current/function-evidence/main/handle_player_collision_combo.json`
- Prior geometry/CFG finding and cautions about absent DWARF locations: `docs/attempts/game-main/handle_player_collision_combo-finding.md`
- Collision-old lifetime comparison: `docs/attempts/research-luna-collision-old-lifetime-20260923/README.md`
- Original disassembly: `docs/attempts/research-luna-collisions/combo-original-disasm.txt`
- Corrected inputs: `probes/current-control.c`, `probes/cache-xy-used-v2.c`, `geometry/intersections-used-v2.c`, `geometry/debug-intersections-used-v2.c`
- Receipts/comparisons: `docs/attempts/tu-context/game-main/luna-combo-v2-control-20260923.json`, `luna-combo-v2-cache-xy-used-20260923.json`, `luna-combo-v2-intersections-used-20260923.json`, `luna-combo-v2-debug-intersections-used-20260923.json`
- Each receipt points to its isolated `build/tu-context/game-main/<label>/comparison.json` and `unit.o`.

The remaining mismatch is not explained by reusing the `collision_old` `dX` register-life hypothesis. Cached doubles reproduce the original frame reservation; adding the evidenced geometry locals increases it beyond the historical frame. Further progress needs evidence that distinguishes the original local lifetime/allocation schedule from these source forms; no additional spelling-only variants are supported by this result.
