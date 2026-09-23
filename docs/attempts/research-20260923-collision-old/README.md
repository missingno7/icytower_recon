# `handle_player_collision_old` local lifetimes and CFG

Scope: read-only inspection of maintained state followed by isolated current-order CU probes. No file under `src/`, generated current state, or recovery ledger was changed. Current card: `docs/current/functions/main/handle_player_collision_old.json`; related collision-family evidence: `docs/attempts/research-luna-collisions/collision-family-findings.md`, `docs/attempts/game-main/handle_player_collision_vector-finding.md`, `docs/attempts/game-main/handle_player_collision_combo-finding.md`, and `docs/attempts/game-main/bodies/handle_player_collision_old.c`.

## Original DWARF ranges

The function begins at `0x407fd8`; DWARF location-list PCs are translated through CU base `0x406960`. The table below gives function-relative ranges and decoded storage:

| Local | Original storage/lifetime | Meaning for this task |
|---|---|---|
| `dX` | `%edi` at `[56,107)`, `[333,338)`, `[472,490)` | Register only; first lifetime ends before the first `is_solid` call (offset 142). The final range is a later reuse. |
| `dY` | fixed `-0x2c(%ebp)` | Absolute y delta is materialized in memory and later read for midpoint y. |
| `midX` | fixed `-0x24(%ebp)` | Midpoint x is stored by either signed-direction arm and reused by the sweep calls. |
| `midY` | `%esi` at `[142,330)`, `[358,469)`, `[490,894)` | Held across the two first-foot calls and then reused as the midpoint sweep y argument. |
| `solid1` | mostly `%edi`, with brief `%ebx` ranges | First collision result reuses a callee-saved register across the second call and later resolution. |
| `solid2` | `%eax` in listed ranges | Second collision result reuses the return register. |

`lastX` moves from its incoming stack slot to `%ecx` through the midpoint-x calculation; `lastY` is in `%ebx` through most of the pre-sweep path. The exact original instruction listing is saved as `original-disassembly.txt`.

## Original control flow

- Entry computes `dX` in `%edi`, with negative correction at `+0x1d8`; computes and stores `dY` at `-0x2c`, with correction at `+0x1e0`.
- Midpoint x has two signed arms that both write `midX` at `-0x24`. Midpoint y has two arms that join at the first `is_solid` call (`+0x8e`).
- The current-foot checks are calls at `+0x8e` and `+0xe9`. If neither is solid, the status transition runs and `midY <= lastY` returns; only the downward case branches to midpoint sweep at `+0x250`.
- If a current foot is solid, status filtering and the resolve sequence begin at `+0x16c`. The midpoint sweep checks its own pair of feet, then runs a separately emitted status/resolve sequence at `+0x2c0`. The original therefore contains separate physical current-foot and midpoint resolution blocks, including corresponding epilogues and sound paths.

The maintained source already preserves the separate current-foot and sweep paths, and its compiled function also emits two resolution regions. The known source difference is not a missing branch: the source has `x`, `y`, `dx`, and `dy`, while the original DWARF names/lifetimes are `dX`, `dY`, `midX`, and `midY` with the storage above.

## Probe batch and outcome deduplication

1. **DWARF-named retained body control.** The prior retained body in `docs/attempts/game-main/bodies/handle_player_collision_old.c` was compiled in current TU order with no generated prototypes and the current `play`/neighbor definitions. It produces 910/894 bytes, remains `DIFFER` at offset 8, and still reserves `0x4c` bytes, versus the original `0x3c`. Its assembly spills `dX` to `-0x3c(%ebp)` before the first call and reloads it for midpoint arithmetic. The original uses `%edi` for that first `dX` lifetime and has no such spill. This confirms that restoring the original local names and the retained duplicated resolution source is not sufficient to recover the original register lifetime or frame.
2. **Cached-coordinate comparison probe.** In a research-only copy of the maintained body, the direction tests `((int)ply[player_id]->x < lastX)` and `((int)ply[player_id]->y < lastY)` were changed to compare the already computed `x` and `y`. This follows the original register flow: its first converted coordinates are still in `%eax`/`%edx` at the two comparisons. The candidate function instruction bytes are exactly equal to the current maintained baseline: 961 bytes, `DIFFER` at offset 8, `0x4c` frame. This is a deduplicated effective outcome, so no further spelling variants were run.

Both isolated compilations used locked TDM-GCC 4.4.1, `-O2 -g -mfpmath=387`, current definition order, and no generated prototype block. The current-order probe has 63 exact functions; `new_game` and `run_demo` remain exact. The neighboring collision handlers remain `DIFFER` in both comparisons.

## Handoff

The original CFG and local storage are mapped. The cached-coordinate source edit collapses to the current emission. The retained DWARF-named body confirms the most visible local-lifetime gap: original `dX` is register-resident through its pre-call lifetime; candidate spills it to the bottom of the frame and reserves 16 additional bytes. Prior notes already rule out attributing that spill to crossing the `is_solid` call, since it is stored before the first call. Further source forms around these comparisons would not add information; the next useful step would need a distinct, evidence-backed explanation for why GCC keeps `dX` in `%edi` in the historical source shape.

Artifacts: `original-disassembly.txt`, `candidate-disassembly.txt`, `collision-old-dwarf-names.c`, `dwarf-named-baseline/`, `dwarf-named-baseline.comparison.json`, `run_dwarf_named_probe.py`, `collision-old-cached-coordinate-compare.c`, `cached-coordinate-compare/`, `cached-coordinate-compare.comparison.json`, and `run_cached_compare_probe.py`.
