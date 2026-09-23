# profile_data_page_general isolated context study (2026-09-24)

This folder contains a batch manifest and two retained body overlays for the unresolved `game-profile` function. It does not modify maintained source, generated current state, or `src/recovery.json`.

## Batch result

The locked GCC 4.4.1 TDM-2 compiler ran both overlays at the current TU order with generated prototypes disabled. Both strict results were `DIFFER`, and both kept all 11 existing `FUNCTION_MATCH` functions in the profile CU with no gains or losses. The baseline is 1082 bytes versus 1091 historical, first mismatch at function offset 266. The retained `!= 1` selector candidate is 1074 bytes, still first mismatching at 266. Their effective identities differ (`f902f9787c50019d…` vs `4aaa41149e496824…`), so the spelling change is not an output collapse; it moves code size farther from history without changing the first branch mismatch.

## Artifacts

- `batch-manifest.json`: reproducible batch inputs and labels.
- `current_baseline.c`: body from the blocked current attempt.
- `selector_ne1_trial14.c`: retained prior selector spelling used as a comparison.
- Receipts: `../tu-context/game-profile/research-20260924-general-{baseline,ne1}.json`.
- Full isolated reports: `build/tu-context/game-profile/research-20260924-general-{baseline,ne1}/comparison.json`.

The next investigation should inspect the original and candidate CFG/layout around the selector branch and compare compiler/TU context. The card shows the function remains at its historical emission position with the same exact predecessor, while the historical exact prefix stops at 5 of 17 functions; this leaves earlier GCC state as an open possibility. Do not infer a source cause from the branch target alone.

## Original CFG and baseline GCC layout

A dump-enabled baseline was compiled with the same locked command plus only `-fdump-ipa-cgraph -fdump-rtl-all`. Its `.text` dump is byte-for-byte identical to the no-dump baseline; the object file hash differs because debug metadata records the separate output location. It preserves all 11 exact profile functions and the same 1082-byte target body. The raw compiler command and dumps are retained in `rtl-all-baseline/`; compare `unit.o` to `build/tu-context/game-profile/research-20260924-general-rtl-noprotos/unit.o` for the verified no-dump baseline.

At the first selector, the original executable has `test %esi,%esi; jle +0x3a4`, then `cmp $1,%esi; je +0x3c0`. The candidate has the same tests at the same instruction positions and same outer-gate target, but the equality branch goes to `+0x3dc`. The original `+0x3c0` block loads the singular suffix pointer and jumps back to the shared `sprintf` argument setup at `+0x113`; candidate `+0x3dc` performs the corresponding load and jump. Later selector arms also converge on shared call setup blocks. Thus the first concrete difference is a different branch destination for the same apparent CFG role; the destination block itself has the same operation and continuation. This is not a proof of semantic/layout-only equivalence.

The candidate `profile.c.187r.bbro` dump shows GCC's trace block reordering on this baseline. After the hot body it appends cold selector arms; the recorded final BB sequence ends `... 43 44 3 39 25 14 6 18 45 21 29 46 32 47 35 10`. The `bbro` log also duplicates join blocks 20, 31, and 34 as 45, 46, and 47 to connect fallthrough traces. The executable's cold tail is laid out at offsets `+0x3a4` through `+0x434`, with the first singular arm at `+0x3dc`. This explains how GCC arranges the candidate's branches, but there is no original RTL to establish why the historical compiler chose the `+0x3c0` order.

Original line mappings around the formatting code are coarse: the initial seconds guard/selector maps to historical line 311; later minutes, hours, and days code maps to lines 312–314. DWARF has no lexical blocks and no additional local beyond the nine recorded in the card. Both sides retain one `malloc` call and eleven `sprintf` calls. The historical immediate predecessor is the same exact `profile_data_page_extra` function in both emission positions. No line-table, local, call, or predecessor evidence identifies a fresh source alternative. The historical exact prefix is only 5/17 functions, so prior compiler state remains an open investigation path, but there is no evidence selecting a specific context probe. Stop body guessing here and route to a supervisor for a context/source reconstruction hypothesis.

Relevant retained paths:

- Original disassembly window: `assets/icytower15.exe`, at `0x4197a5–0x4198a3` and `0x419a4c–0x419aec`.
- Baseline candidate object and original-vs-candidate report: `build/tu-context/game-profile/research-20260924-general-rtl-noprotos/unit.o` and `comparison.json`.
- GCC block order: `rtl-all-baseline/profile.c.187r.bbro`; pre/post block and register snapshots: `profile.c.181r.csa` and `profile.c.182r.peephole2`.
- Dump-enabled strict result receipt: `../tu-context/game-profile/research-20260924-general-rtl-noprotos.json`.
