# create_profile batched reconstruction research (2026-09-24)

Scope: isolated `docs/attempts/research-20260924-create-profile-batch/` overlays for the current `game-profile` focus `create_profile`. No production source, current card, or recovery ledger was edited. All compiles used locked `tdm-2`, `-O2`, `tu_context_probe.py`/`batch_tu_probe.py`; all saved probes are diagnostic, never acceptance evidence.

## Starting evidence

`docs/current/functions/profile/create_profile.json` is CHEAP/DIFFER: 823 bytes on each side, two differing bytes, first at function offset `0x45` / original VA `0x41a9cd`. The target stores `overwrite` from `[ebp+0xc]` in ESI and tests ESI; candidate uses EDI and tests EDI. No relocation or direct-transfer mismatches were recorded. Same-CU historical and current positions are both 15, with exact `delete_profile` as predecessor. The original DWARF inventory has function-scope locals in the source order `file`, `p`, `i`, `now`, `my_time`, `year`, `month`, `day`; there are no lexical blocks. Existing focused attempt history has 16 FAST records: earlier bodies first differed at offset 508; the latest records converged to offset 69 after changing the independent `flash`/`start_floor` initialization source order.

## Batched outcomes

- `batch.json`: four equivalent `overwrite` guard forms (control, nested `if`, early `goto`, De Morgan). All four compile to the same effective identity `e9b312015907a283…`; all remain DIFFER, 823/823 bytes, first mismatch 69. No neighboring exact functions changed.
- `declaration-batch.json`: four local declaration order/grouping variants. All map to the same identity and the same mismatch. These were diagnostic counterfactuals: their declaration ordering diverges from the DWARF local sequence, so none is a candidate repair.
- `current-order.json` and `historical-order.json`: compared current and historical TU emission order with control and nested-guard bodies. Both orders retain the same target outcome identity and mismatch at 69; the target's historical/current position and exact predecessor remain unchanged. The order hypothesis does not explain the register choice.

Each probe has a unique receipt under `docs/attempts/tu-context/game-profile/` and a detailed comparison under `build/tu-context/game-profile/`. The batch manifests and retained source overlays are in this directory. Effective-output grouping is available by rerunning each manifest with `--reuse-only`.

## Conclusion / handoff

The source guard shape, these local declaration perturbations, and TU emission order do not move GCC's `overwrite` value from EDI to the original ESI choice. No strict candidate or promotion receipt was found. Keep the production function at DIFFER and route this register-allocation mismatch for supervisor investigation; do not treat the normalized/effective equality groups as proof. The strongest next experiment would need a new evidence-backed compiler/pass or source-lifetime hypothesis that can alter allocator input while preserving the historical DWARF inventory and every other emitted byte.

## IRA pass control

I compiled the untouched current CU with one diagnostic `-fdump-rtl-ira` option, using the exact command recorded in `build/fast/game-profile/build.json` and an isolated output path. The resulting object is byte-identical to the baseline object: SHA-256 `a17d081c9d873e261a7de4d81d5cf291f9f1e73d957129a449a5ff886235b51e`. This validates that the dump option did not alter the effective object. The saved IRA dump (`passes/profile.c.172r.ira`) shows the `overwrite` comparison fed from `[ebp+12]` in RTL and its reload at insn 22; the excerpt is in `passes/create_profile-ira-excerpt.txt`. The final register choice occurs at reload/code emission in the candidate. There is no original GCC dump to compare, so this only locates the candidate-side decision and does not identify why original GCC selected ESI.
