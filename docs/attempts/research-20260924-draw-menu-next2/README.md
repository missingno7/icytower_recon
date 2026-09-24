# `draw_menu` current-context rebase

Date: 2026-09-24. Research-only whole-`game-menu` probes, locked TDM-GCC 4.4.1, `-O2`, i386/x87. No maintained source, generated current state, or recovery ledger was edited.

## Current input and control

The current source is `src/menu.c` SHA-256 `4cdb39a001e2413b206a702941af52c40616e490960bac25da8513e9558cf044`; `src/recovery.json` SHA-256 `1fdd09a43371e21578c7ed5eb6d9c7f16f3cc00ebe4f796f76ba83a106c01a56`. Historical-order/no-prototype whole-TU control receipt: `build/tu-context/game-menu/luna-draw-menu-next2-current-control/comparison.json`.

Control result: 7/10 functions exact; 10/10 historical predecessors preserved. `draw_menu` remains DIFFER, 956/1118 bytes, first mismatch +8, frame allocation 0x15c instead of 0x16c; response summary reports 5/6 unequal relocations. No peer gains/losses.

## Source/DWARF-supported discrepancy and rebased probe

The focused card identifies local `DATAFILE *assets` at candidate line 124 as `CANDIDATE_ONLY_DEBUG_DECLARATION`; original DWARF has no such local. That local is the concrete 16-byte frame excess. Prior source-backed correction removes it and directly indexes the three `mp->data` entries. Its retained body is `docs/attempts/research-20260924-draw-menu-followup/recorded_control.c` (SHA-256 `b4a472ae03d27e6b0b955e0e4d109f23be9a072cbe500e75f505f1d48f439ec6`).

I rebased that known correction against the current whole-TU source/context:
`build/tu-context/game-menu/luna-draw-menu-next2-dwarf-control/comparison.json`.
It emits 896/1118 bytes, the historical 0x16c frame, and first differs at +16; it preserves 7/10 exact functions and all 10 historical predecessors. There are no peer gains or losses. The response comparison is in `results.txt`. Thus the candidate-only declaration explains the frame delta, but its removal does not recover the function: the unresolved `mp` allocation is still historical `%edi` versus candidate `%edx` (first instruction-order/register mismatch +16). Strict status stays DIFFER; this earns no recovery credit.

The two retained candidate forms compiled to two effective outcomes (956-byte current control versus 896-byte corrected body). This confirms the frame correction still transfers into the current TU context. It does not distinguish a new historical source cause. The downstream `handle_menu` and `update_game_menu` raw-code-change flags are address-sensitive; normalized effective comparison reports no unchanged-body changes, and the strict peer set is unchanged.

## Scoped negative and next discriminator

`research-20260924-draw-menu-followup/README.md` already tested the alternate DATAFILE indexing expressions, direct recovered field types, and `h`/`stepIn` statement ordering; all three variants collapsed to one effective output. The historical line table and current candidate already support `h` before `stepIn`; DWARF-backed scopes for `pos`, `str`, `h`, loop `x`, `key_str`, and bitmap `b` agree. No fresh source/line/DIE-supported local hypothesis remains here. Stop body spelling search. A useful next experiment must identify why GCC 4.4.1 allocates `mp` to `%edx` in this complete body while the historical object keeps it in `%edi`, using pass/RTL or historical predecessor/context evidence. Do not infer source history from byte size or try register-pressure rewrites without evidence.

## Receipts

- Current control: `build/tu-context/game-menu/luna-draw-menu-next2-current-control/comparison.json`
- Rebased corrected-body control: `build/tu-context/game-menu/luna-draw-menu-next2-dwarf-control/comparison.json`
- Effective compiler response: `results.txt`
- Earlier source/DWARF and collapse evidence: `docs/attempts/research-20260924-draw-menu-followup/README.md`
