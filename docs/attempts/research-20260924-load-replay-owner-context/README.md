# `load_replay` research on the replay-owner base

Date: 2026-09-24. Research only; the source base is a separate copy of
`research-20260923-replay-pretable-owner/property-case-order-source.c`. Probes
replace only `load_replay`. The historical-order `get_replay_property` edit in
that base remains untouched. No maintained source, generated current state, or
recovery ledger was edited.

## Historical source evidence

The current focused card is `docs/current/functions/replay/load_replay.json`:
historical function size 1136 bytes, target first mismatch at +171, candidate
size 1148, and 22 of 39 text relocations unequal/unresolved. Historical line
mapping and DWARF show these declarations:

| Local | Historical evidence |
|---|---|
| `pf` | `PACKFILE *`, declaration line 266 |
| `r_temp`, `r` | declaration line 267; `r_temp` is the 0x8cc-byte `Treplay` at frame offset -2252 |
| `i` | signed `int`, declaration line 268 |
| `sum` | signed `int`, declaration line 269 |
| `cs` | signed `int`, declaration line 346 |

There are no lexical-block DIEs for this function. The copied candidate had
`cs` declared at the function top with the other locals, so its declaration
placement did not reflect the historical line. Historical line 346 maps to
function offset +0x42c, the load of `r->checksum`; line 347 is the following
zero store, and lines 348–352 cover checksum calculation, comparison, failure
logging, and cleanup.

Historical disassembly confirms the candidate's broad body and loop structure:
the `ccc[5]` and `jc[5]` reads are two distinct loops, each advances a byte
offset by four and compares it with 20; the 100-element table loop reads five
fields per index; the replay-data loop reads a four-byte cycle count and one
key byte per item. The source order, loop bounds, and read order in the copied
body agree with those rows and the instruction stream. Do not fuse the first
two loops: that would contradict the historical CFG.

## Declaration-placement probe

The baseline and two source-backed variants were compiled as complete replay
translation units with the locked TDM-2 GCC 4.4.1 `-O2` command, using current
definition order and the copied owner source. No new prototype block was added.
Each retained the source base's 8/15 `FUNCTION_MATCH` results (relative to the
current reference, 6 before / 8 after), with no exact-function losses.

| Probe | `cs` declaration/use form | Effective output | Target result |
|---|---|---|---|
| `luna-load-replay-owner-baseline-20260924` | top-level `int cs;`, later assignment | `305bd4b34ee3d876` | 1148/1136, first +171 |
| `luna-load-replay-cs-late-20260924` | `int cs;` immediately before assignment | `305bd4b34ee3d876` | same |
| `luna-load-replay-cs-initializer-20260924` | `int cs = r->checksum;` at historical line 346 | `305bd4b34ee3d876` | same |

All three have the same emitted target instruction-byte SHA-256:
`6d23832afe71fdbf0ea58f81df39be2646a4d6a0f36839c069ea982cef93fd9c`.
All compile cleanly, stay 1148 bytes, report 22 unequal relocations, and retain
the same first mismatch: candidate branch `0f 84 be 03 00 00` at +171 targets
+1133, while the historical `0f 84 b2 03 00 00` targets +1121. The 12-byte
target-length excess is already present downstream of that branch.

The earlier `research-luna-replay-load` work also tested changing only `pf`
from `void *` to the historical `PACKFILE *`; its emitted target byte hash was
unchanged. It tested historical function order and moving `create_replay` or
`draw_replay_selector`; those also left `load_replay` bytes unchanged. Thus the
local type, the late `cs` declaration, and the tested source-order perturbations
do not explain the register choice.

## Blocker and artifacts

The target still differs in the array-read region. History retains `pf` in
`%ebx` and uses `%edi` as an array cursor; the owner-base candidate swaps those
roles around the ccc/jc loops, with additional moves and padding. The loops and
source ordering are historically supported, but the tested source corrections
do not change GCC's allocation. This is a register/context code-generation
blocker, not evidence for changing the read semantics or CFG.

Full reports are under `build/tu-context/game-replay/` with the three probe
labels above. Retained exact body overlays are `load-replay-baseline.c`,
`load-replay-cs-late.c`, and `load-replay-cs-initializer.c`; the untouched 83-
table, named-header source copy is `property-case-order-source.c`.
