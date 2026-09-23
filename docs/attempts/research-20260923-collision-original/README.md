# Collision-original zero-path research (2026-09-23)

`handle_player_collision_original` remains strict `DIFFER`: 449 candidate bytes
against 456 historical bytes, first mismatch at function offset 205. The fresh
25-CU baseline before this research retained 209 strict functions and 35,299
matched game-function bytes. These are isolated current-order whole-TU probes;
maintained source and the recovery ledger were not changed.

The previous seven production FAST attempts varied the later collision/edge
branches but all retained the offset-205 mismatch. Three new, semantically
equivalent spellings of the zero-collision status guard (nested, split, and
inverted) produced **one effective function outcome** (`aeae676cbe028084`),
449 bytes, first mismatch 205. They also preserved every exact TU neighbor.
The guard spelling family is locally exhausted.

The historical suffix at `0x407f7e` branches from `solid1 == solid2` to the
edge-zero store at `0x407fcb`, which is also reached from the no-solid path.
An explicit source join using `goto edge_zero` produced a **new** effective
outcome (`c43344cdff7ec40d`). It replaces candidate `setne/movzbl` with a
conditional jump to a shared zero store, matching that aspect of the historical
CFG. It still emits 449 bytes and first differs at offset 205. The candidate
stores edge 1 directly, while history loads 1 into `%eax` and uses a shared
store; the no-solid path also differs. Exact TU neighbors were preserved.
This source is retained as a diagnostic branch, not promoted.

All 291 retained main-TU probes inspected by `effective_outcomes.py` had the
same effective result for this function before the new explicit join, despite
many unrelated TU changes. Its historical and current emission predecessor is
the exact `start_reward`. The stable mismatch starts where the original keeps
the player pointer in `%eax` and status in `%edx`, while GCC's candidate
interchanges those registers. A later suffix change can alter CFG without
changing this first register choice. Further cosmetic guard/edge rewrites are
unlikely to help; the next discriminating investigation needs a concrete
local-lifetime or optimizer-allocation mechanism, supported by DWARF and a
pass-level probe, or new historical source/context evidence.

`probe.py` generates all four complete body overlays and their whole-TU
receipts. `results.json` and the four receipts under
`docs/attempts/tu-context/game-main/research-collision-original-*.json` record
the compiler outcomes; the object and full comparison live under the matching
`build/tu-context/game-main/` labels. No probe is a match claim.
