# play: collision switch predecessor probe

Scope: one isolated `game-main/play` TU overlay around the floor-generation predecessor and `collision_type` switch. Maintained files and generated current state were not edited.

## Baseline and retained neighbors

Used the existing historical-order 63/82 exact-set context from `luna-play-summary-historical-order-split-20260924` (`new_game` and `run_demo` both `FUNCTION_MATCH`). Its summary-split body was only the fixed context needed to retain that exact set; this experiment did not edit or investigate the summary/new_rand region. The current `play-merged.c` and current play card were read; the collision/floor source region is the same in both bodies. The candidate order list and focused receipt are archived beside this README.

The isolated predecessor variant preserved exactly 63 `FUNCTION_MATCH` functions, with no gains or losses, including `new_game` and `run_demo`. Receipt status map is authoritative for the complete exact set.

## Original CFG evidence and tested hypothesis

The original has three `collision_type` data references around the switch:

- At historical function offset `0x6e5` (`0x4120e5`), `cmp [collision_type],4`; `jbe 0xb9e` enters the shared dispatch. Invalid values reach the shared `allegro_message` at `0x6f2`.
- On the alternate predecessor, offset `0xb88` tests `scroll_acc`; when it does not add a floor, offset `0xb91` repeats the range compare and branches to the same error call. Valid values fall through to offset `0xb9e`, which loads `collision_type` and jumps through the table.

The baseline candidate had only two references: one range check and the dispatch load. The source-backed hypothesis was that GCC needs the two predecessor checks represented separately around the floor decision. The overlay spells out the floor and no-floor paths, uses one shared error label, and leaves the five-way switch as the dispatch. This is a path-structure test, distinct from the earlier single guard around the switch.

Candidate disassembly produced the three expected global reads: one dispatch value and one guarded read on each predecessor. The two new guards route to the shared error block or the shared switch body. This matches the original reference count and broad predecessor topology; it does not make `play` exact.

## Outcome

Effective output `111968da899e5e50`: `play` remains strict `DIFFER`, 17,421 candidate bytes versus 17,420 historical bytes, first mismatch at offset `+8` (frame allocation). Diagnostic comparison reports 16,229 differing bytes and 869/888 unequal relocation windows. The probe has no gains/losses elsewhere, preserves all 63 exact functions, and retains the original direct-call edge set. It is one distinct effective output from the 17,429-byte baseline (`76e71104a738dd74`, 515 branches versus 518 in this probe; both report 289 calls).

The current card also retains an unresolved `.rdata` owner at play offset 19/addend 6272. The source/body and code still differ broadly, so the new reference topology is only a localized lead, not a body or layout match.

## Artifacts

- Candidate body: `docs/attempts/research-20260924-play-collision-predecessor/play-collision-predecessor.c`
- Explicit order: `docs/attempts/research-20260924-play-collision-predecessor/historical-order.json`
- Receipt: `docs/attempts/tu-context/game-main/luna-collision-type-predecessor-branches-20260924.json`
- Comparison/object: `build/tu-context/game-main/luna-collision-type-predecessor-branches-20260924/`
