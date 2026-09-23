# `handle_player_collision_old` lifetime follow-up (2026-09-23)

## Current boundary

The current focused card `docs/current/functions/main/handle_player_collision_old.json` reports `DIFFER`, 961 candidate bytes versus 894 historical, first mismatch at function offset 8 (`sub esp, 0x4c` versus `sub esp, 0x3c`). Its current recovery state allows body edits, but this research made none to maintained source. All probes used isolated function-body overlays in current `main.c` order with `--no-prototypes`.

The historical behavior has two current-foot collision checks, then a downward-only midpoint sweep. Historical disassembly has distinct emitted current-foot and sweep resolution paths. The retained DWARF-shaped body preserves those two paths; current production source shares a resolution tail. That retained source variant is 910/894 (first mismatch +8), so the CFG difference is a supported explanation for part of the candidate's larger body, but does not explain its remaining frame mismatch.

## DWARF live ranges and causal boundary

Original DIEs place `midX`, `midY`, `dX`, `dY` in that declaration order at line 3242; `solid1`/`solid2` follow at 3243. Original locations decoded in `docs/attempts/research-20260923-collision-old/README.md` and `original-disassembly.txt` show:

- `dX` in EDI across function-relative ranges `[56,107)`, `[333,338)`, and `[472,490)`. Its first live range ends before the first `is_solid` call at offset 142, so a call-preservation spill does not explain its historical storage.
- `dY` at `-0x2c(%ebp)`; `midX` at `-0x24(%ebp)`; `midY` in ESI over multiple ranges, including the first-call interval and later sweep setup.
- The old DWARF-shaped candidate computes these named values but stores `dX` at `-0x3c(%ebp)` before any call and reloads it for midpoint arithmetic. Its local DIE has no location for `dX`. Its frame remains `0x4c`, 16 bytes larger than history.

That identifies the concrete gap: the source/control-flow form can preserve the same values and branches, yet GCC 4.4.1 allocates `dX` to a frame spill where the historical code keeps it in EDI. Repeated body naming alone does not recover that register lifetime. No field-layout difference is evidenced by the card.

## Isolated probes and deduplication

A two-variant whole-TU batch tested the original-DWARF local declaration order as a source-supported register/slot allocation hypothesis. Both variants used the retained old-body candidate; the only change was declaration order (`dX,dY,midX,midY` versus `midX,midY,dX,dY`). They deduplicated to the same effective 910-byte output, first mismatch +8, with the full-TU exact set unchanged at 63/82 (no gains/losses). Receipts:

- `docs/attempts/tu-context/game-main/luna-collision-old-dwarf-order-control-20260923.json`
- `docs/attempts/tu-context/game-main/luna-collision-old-dwarf-order-mid-first-20260923.json`

A second two-variant batch used the actual current production body as control and kept `midX`/`midY` distinct from the cached `x`/`y` coordinates in the hypothesis variant. This follows the historical DWARF distinction between midpoint and delta locals while retaining current CFG. GCC optimized the split to the same effective body: both are 961/894 with the same +8 frame mismatch. The exact full-TU set stayed 63/82, with no gains/losses. Receipts:

- `docs/attempts/tu-context/game-main/luna-collision-old-production-control-20260923.json`
- `docs/attempts/tu-context/game-main/luna-collision-old-production-midpoints-20260923.json`
- Manifest and source overlays: `production/manifest.json`, `production/production-control.c`, `production/separate-midpoint-locals.c`

All 63 production exact functions were preserved. Both current-body variants have the same effective outcome identity `a8537bc8fb3bff7d62a9802b2d4ae3a0d8f245c260241db679869cb8c29573cb`; both DWARF-order variants share `39e101af96813029e0ce2d499af5a9fbaacd9b7fe786f51b4e9f0484e9135cc6`. Neither batch changed maintained files or generated state.

## Blocker and handoff

The distinct-midpoint-local source form is eliminated by GCC to the production baseline. Reordering the retained candidate's locals is likewise output-neutral. The retained split-resolution body proves a separate CFG source shape matters, but its `dX` spill and 16-byte frame excess remain. The current evidence supports no further local declaration or cached-coordinate variant; chasing variable spellings would duplicate outputs. Next progress needs a distinct source-level cause for why the historical allocation keeps `dX` in EDI while retaining `lastX` in ECX across the midpoint branches, or additional historical compiler/pass evidence. No strict candidate was found; keep all current production exact neighbors protected.

## Supporting artifacts

- Current card: `docs/current/functions/main/handle_player_collision_old.json`
- Earlier local lifetime/CFG audit: `docs/attempts/research-20260923-collision-old/README.md`
- Retained split-resolution body: `docs/attempts/game-main/bodies/handle_player_collision_old.c`
- Original and candidate asm: `docs/attempts/research-20260923-collision-old/original-disassembly.txt`, `candidate-disassembly.txt`
- Batch folder: `docs/attempts/research-luna-collision-old-lifetime-20260923/`
