# `handle_player_collision_old` current historical-order probe — 2026-09-24

Scope: isolated `game-main` overlays only. No maintained source, focused card, generated current documents, queue, or recovery ledger changed. Compiler was locked TDM-2, `-O2 -g -mfpmath=387`, historical definition order, and `--no-prototypes`.

## Fresh control and probes

The fresh current-source historical-order control compiled 64/82 exact functions before and after, with no gains or losses. `_old` remains `DIFFER`, 961/894 bytes, first mismatch at function offset +8 (`sub $0x4c,%esp` versus `$0x3c`). It has 29 branches and 6 calls (four `is_solid`, two `play_sound`), matching the historical call multiplicities and callee set. Historical frame reservation is 60 bytes; candidate reservation is 76 bytes.

One new source-shape hypothesis split the current `x/y` midpoint reuse into separate `midX/midY` locals while retaining cached coordinate comparisons. It produced the same effective function bytes as the fresh control: 961 bytes, 29 branches, 6 calls, same +8 mismatch. This reuse split is exhausted for the current body.

The retained DWARF-named body, with original `dX,dY,midX,midY,solid1,solid2`, produced 910/894 bytes in this current TU context. Changing declaration order from source order `dX,dY,midX,midY,solid1,solid2` to historical DIE order `midX,midY,dX,dY,solid1,solid2` had no effective output effect. Both have 27 branches and 6 calls and retain all 64 exact functions with no gains or losses. `effective_outcomes.py` groups the two declaration-order probes at identity `eadadba8bd26cd15` (910 bytes, 792 differing bytes, 32/34 unequal relocation operands, 0x4c frame). The split-midpoint overlay groups with the 961-byte control.

The 910-byte retained variant remains `DIFFER`: +8 is still the frame-allocation mismatch (`0x4c` vs `0x3c`), and no strict exact-function gain exists for `_old`. The 34 relocation operands contain two equal and 32 unequal entries; relocation resolution does not prove a layout-only match. Direct call target/callee multiplicities are already correct. Original local locations support `dX` in EDI over `[56,107)`, `[333,338)`, `[472,490)`, `dY` at `-0x2c(%ebp)`, `midX` at `-0x24(%ebp)`, and `midY` in ESI over long ranges. In the candidate DWARF, `dX` has no location entry; `dY`, `midX`, `midY`, `solid1`, and `solid2` have location lists. The pass follow-up below corrects the earlier inference that the `dX` home existed before IRA: it is absent through `.159r.combine` and first visible in `.172r.ira`. The older allocno report still showed no hard-register conflict, but it does not establish when the frame home was introduced.

## Disposition

Current midpoint reuse and local declaration order provide no remaining source-level explanation. The retained DWARF-named shape remains a distinct 910-byte effective outcome, but does not repair the 16-byte frame excess. Further naming/order variants are exhausted; next useful evidence would be historical GCC pass context or a source-backed cause for the IRA home. No layout-only claim is supported.

## Smallest artifacts

- Current body overlay: `docs/attempts/research-20260924-collision-old-split-context/old-split-midpoints.c`
- Fresh current control receipt: `docs/attempts/tu-context/game-main/collision-old-current-historical-control-luna-20260924.json`
- Split midpoint receipt: `docs/attempts/tu-context/game-main/collision-old-luna-high-current-split-midpoints-20260924.json`
- Current retained-body receipts: `docs/attempts/tu-context/game-main/collision-old-luna-high-current-dwarf-names-20260924.json` and `docs/attempts/tu-context/game-main/collision-old-luna-high-current-die-order-20260924.json`
- Named-body DWARF: `build/tu-context/game-main/collision-old-luna-high-current-dwarf-names-20260924/dwarf.txt`
- Deduped outcome summary: `python tools/effective_outcomes.py game-main handle_player_collision_old --pattern 'collision-old-*20260924*' --response --baseline collision-old-current-historical-control-luna-20260924`
## Emission-neutral pass dump follow-up

Both source shapes were compiled with locked TDM-2 `-O2 -g -mfpmath=387` plus `-fdump-tree-all -fdump-rtl-all`. Each diagnostic compile was checked against a no-dump compile from the identical overlay path: object SHA-256, all section hashes, every function effective projection/status, and the complete object relocation list matched exactly. The current control retained 64 exact functions; the named-body variant also retained 64. The earlier cross-path relocation-offset difference was debug-info path noise and was eliminated by this same-path control.

The current and retained bodies first differ at source/tree lowering because they use different local shapes: the maintained body materializes `x/y` locals and reuses them as midpoint values, while the retained body uses `dX/dY` and separate `midX/midY`. In both candidates, `.128r.expand`, `.154r.reginfo`, and `.159r.combine` contain no `-60(%ebp)` home. The first appearance is `.172r.ira`: the control stores the delta in insn 349 and the retained variant in insn 325 to `-60(%ebp)` (IRA frame-relative slot `-36`). The final strict comparison still shows 0x4c versus 0x3c frame reservation. Thus the candidate dX home is established by IRA; the total 16-byte frame excess is measured from the final prologue, and no historical pass dump exists to locate the original-versus-candidate split more precisely.

Both bodies reach the same dX home by IRA despite their distinct 961-byte and 910-byte effective emissions. This pass comparison identifies no new source-backed next hypothesis; stop local probing here.

Pass summary: `pass-neutrality.json`. Dump roots: `build/tu-context/game-main/collision-old-pass-luna-high-20260924/control/` and `.../dwarf_names/`.
