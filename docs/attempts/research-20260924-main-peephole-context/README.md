# Main-TU guard / peephole2 diagnostic (2026-09-24)

Research only. Maintained source, ledgers, and shared tools were untouched. Both
inputs are retained full-TU historical-order overlays:
`force_profile_luna_base_20260924` and
`force_profile_luna_gfxguard_retry1_20260924` under
`build/tu-context/game-main/`. The first guard attempt failed to produce an
object; use `retry1`.

The guard adds a 12-byte change to `force_create_profile` (1458 to 1470 bytes).
That function is emitted immediately before the five previously exact bodies
below. The baseline has 63/82 exact functions, the guard 58/82.

| Emitted function | Baseline scratch choices | Guard scratch choices | First object difference |
| --- | --- | --- | --- |
| `force_create_profile` | none visible | DX | edited predecessor |
| `log2file` | DX | CX | +13, register opcode |
| `testWindowResolution` | CX, BX, AX, DX | BX, AX, DX, CX | +11, register opcode |
| `new_game` | CX, BX, SI, AX | BX, SI, AX, DX | +127; size 1139 to 1138 |
| `uninit_game` | DX, CX | CX, BX | +21, register opcode |
| `check_beta_tester` | BX | SI | +191, register opcode |

I recompiled each exact overlay via `tools.tu_context_probe.compile_overlay`
with `-fdump-ipa-cgraph -fdump-rtl-csa -fdump-rtl-peephole2`. The rebuilt
`.text` bytes are exactly identical to each corresponding retained no-dump
object: 63088 baseline bytes and 63100 guard bytes. This proves these flags
byte-neutral for these two compilations. Dump outputs are in the two
`research_force_profile_*_dumps_20260924` directories beside the retained
overlays. To reproduce the pass comparison, split each CSA and peephole2
dump at a Function section header, then compare same-named sections after
normalizing only overlay paths, front-end pointer addresses, and transient
label/temporary suffixes. Keep hard-register names intact.

All five downstream bodies have identical normalized CSA RTL, then differ
at scratch loads in peephole2. `log2file` compares memory
`itrcheck` directly at CSA in both variants; peephole2 materializes it in DX
versus CX. Thus IRA is not the first observed cause of any of the five
losses. The extra DX scratch in the edited predecessor followed by shifted choices fits GCC 4.4.1's
process-persistent `peep2_find_free_register` search cursor. The research
`recog.c` copy defines that cursor but is not proven to be the exact locked
`cc1.exe` source; the binary is stripped. Dump diffs omit failed searches and
unmaterialized calls, so the exact cursor value at each function entry is
inferred, not observed.

The discriminating next tool would be a compatible instrumented GCC 4.4.1
`cc1` build recording each `peep2_find_free_register` entry/exit cursor and
chosen/rejected hard registers for these two overlays, with byte-equivalence
to the locked compiler verified before interpreting the trace. No matching
compiler source/debug map is available locally, so this investigation stops
at the pass boundary evidence rather than claiming a proven hidden cursor.
