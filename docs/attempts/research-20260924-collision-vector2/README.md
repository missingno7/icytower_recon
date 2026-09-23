# `handle_player_collision_vector_2` parameter/IRA follow-up — 2026-09-24

Scope: research overlays only. No maintained source, generated current state, or recovery ledger changed. Locked compiler is TDM-2 GCC 4.4.1, `-O2 -g -mfpmath=387`; overlay compilation used current definition order and `--no-prototypes`.

## Historical `lastY` evidence

Function range is `0x4088c8..0x408d06` (1086 bytes); the CU base is `0x406960`. The parameter DIE is `lastY: int`, with location-list entries translated to function-relative offsets:

| Range | DWARF expression | Meaning |
|---|---|---|
| `[0,269)` | `DW_OP_fbreg +4` | incoming stack parameter |
| `[269,512)` | `DW_OP_reg7` | EDI |
| `[512,514)` | `DW_OP_fbreg +12` | stack |
| `[514,845)` | `DW_OP_reg7` | EDI |
| `[845,847)` | `DW_OP_fbreg +12` | stack |
| `[847,1086)` | `DW_OP_reg7` | EDI |

The bytes independently show `mov 0xc(%ebp),%edi` at `+15`, and historical line-intersection call setups pass `%edi` as the `lastY` argument. The DWARF register attribution begins at `+269`, later than that copy, so its location list is not a complete record of the physical register live range from entry.

The sibling `_vector` evidence describes a different allocation: `lastY` is held in ESI while EDI carries `ply1`. `_vector_2` instead carries `lastY` in EDI; do not transfer the sibling's register assignment as a family rule.

## Locked GCC IRA evidence

A full-CU diagnostic compilation added `-fdump-rtl-ira -fira-verbose=3` through `tu_context_probe.compile_overlay`; the target's decoded instruction-byte list is identical to the no-dump baseline (1057 bytes). Dump: `build/tu-context/game-main/collision-vector2-ira-20260924/main.c.172r.ira`; comparison: `build/tu-context/game-main/collision-vector2-ira-20260924/comparison.json`.

In that baseline candidate, GCC has pseudo `r84 [lastY]`; IRA assigns its allocno `a24(r84)` to `mem`, with live ranges `[131..463]` before compression and `[52..159]` after compression. The RTL loads `[ebp+12]` into short-lived call-argument pseudos at the call sites. `p` is pseudo `r74`, assigned EBX; `current_y` is `r71`, assigned ESI. General-register pressure reports `14` at the main region. This supports a register-pressure/lifetime diagnosis: the candidate has a long-lived `lastY` value that IRA spills while `p` and geometry/result pseudos occupy registers.

An already-retained isolated probe that removes `p` and spells the global accesses directly provides a discriminating result: generated prologue now copies `lastY` into EBX (`mov 0xc(%ebp),%ebx`), rather than leaving it stack-resident, but the function grows from 1057 to 1117 bytes and remains DIFFER. Receipt/source: `docs/attempts/tu-context/game-main/collision-vector2-direct-player-pointer-20260924.json`, `docs/attempts/research-20260924-collision-vector2/vector2-direct-player-pointer.c`. This does not recover the original EDI allocation and has no exact-neighbor losses.

## Predecessor/context check

The prior historical-order full-TU baseline and the current-order baseline produce the same effective 1057-byte target outcome; the historical-order probe also retained its 62 exact functions and had no losses. Current-order baseline has 63 exact functions and protects `new_game` and `run_demo`. The historical/current predecessor context therefore offers no new lever for this allocation in the checked contexts; no extra predecessor probe was warranted.

## Disposition

No source form is justified by the parameter DIE alone that would legally force IRA's spilled parameter into the original EDI slot. The one source-shape probe that changes the spill decision instead selects EBX and adds 60 bytes. Stop before cosmetic register-spelling or artificial alias trials. Strict status remains DIFFER (1057/1086 baseline; first strict mismatch at `+16`); no promotion claim.

Artifacts: baseline/direct-pointer/snap receipts in `docs/attempts/tu-context/game-main/`; isolated bodies in `docs/attempts/research-20260924-collision-vector2/`; the locked IRA dump and comparison in `build/tu-context/game-main/collision-vector2-ira-20260924/`.
