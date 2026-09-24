# `select_profile` control parameter investigation

## Source and TU context

All probes use the retained combined full-TU candidate with restored switch dispatch, original create prompt/UI paths, scoped `buff[256]`, `new_name[32]`, and `buf[128]`, and `textout_ex`. It is compiled as the full `game-profile` CU with locked TDM-2 GCC 4.4.1 flags `-O2 -g -mfpmath=387`. Each comparison reports all 17 functions, initialized data, common/BSS allocations, and object relocations. Every run retains the same 11 exact neighbors: `hash2`, `generate_profile_checksum`, `get_rank_id`, `get_rank`, `set_next_rank_message`, `profile_data_page_advanced`, `profile_data_page_basic`, `profile_data_page_extra`, `save_profile`, `load_profile`, and `delete_profile`.

Historical DWARF names `ctrl` as `Tcontrol *` and gives it a location list. The oracle prologue is concrete: at function offset +12 it executes `mov esi,[ebp+0x14]`; every control helper call then passes `%esi`. The baseline candidateâ€™s function signature uses a typedef of that same `Tcontrol`, but call sites reload `[ebp+0x14]`. An entry local alias (`Tcontrol *cached_ctrl = ctrl`) was optimized to the same effective function emission as the baseline (identity `9ca3e8d8â€¦`), 2998/3070 bytes, first mismatch +12. This eliminates simple alias spelling as a lever.

The oracle CFG includes two `is_any(ctrl)` calls per loop. The first call guards key simulation when `ctrl_wait` is zero. A second `is_any(ctrl)` call gates decrementing `ctrl_wait`; the baseline candidate had only the first call and decremented the wait unconditionally. This is visible in original disassembly around +0x2e5 through +0x32e, before `keypressed`, and explains why the baseline parameter is repeatedly used through a broader call sequence.

## Source-backed probe

Added the missing second `is_any(ctrl)` guard around the wait decrement. This emitted the original prologue capture into `%esi` at +12 and one extra direct call instruction (69 versus baseline 68). It moved the first strict mismatch to +64, where the oracle stores the newly created bitmap pointer at `[ebp-0x130]` and the candidate stores it at `[ebp-0x128]`. Historical DWARF places `bgbmp` at `ebp-0x130`; the candidateâ€™s stack-slot assignment is already divergent before the main loop. The strict result is still `DIFFER`, 3115/3070 bytes (45 bytes larger), first difference +64. It is not a layout-only proof.

Both nested and short-circuit C forms of the second guard compile to the same effective function identity (`f05c05d7â€¦`), so further syntax variants of that guard are not useful. The byte increase and +64 stack-slot difference point to remaining register/local allocation or wider TU/compiler context, after the control-use path is restored. No production source, generated card, recovery state, or shared ledger was changed.

## Artifacts

- `results.json`: compact strict results, counts, effective identities, and exact-neighbor sets for four variants.
- `control.c`, `cached_ctrl.c`, `any_gated_wait.c`, `any_short_circuit.c`: complete TU variants; paired `*.body.c` files isolate the function source.
- `build/<variant>/comparison.json`, `build-provenance.json`, `unit.o`, compiler logs, and dependency/interface metadata: strict full-CU proof inputs and outputs.


## Bounded frame-slot follow-up

The frame size is already exact in the +12-corrected candidate: both oracle and candidate reserve `0x16c`. Historical DWARF assigns `bgbmp` to `ebp-0x130` (`-304`), while the corrected candidate’s setup stores the bitmap at `ebp-0x128` (`-296`); the first strict byte difference is the displacement byte of that store at +64. The historical sibling-local map is `old_font -320`, `selectedProfile -316`, `done -312`, `offset -308`, `bgbmp -304`, and `ctrl_wait -296`. The three scoped arrays (`buff[256]`, `new_name[32]`, `buf[128]`) all reuse `-288` in non-overlapping lexical scopes. Candidate DWARF preserves the three array scopes and `-288` slot, and the candidate keeps `old_font -320` and `selectedProfile -316`, while its observed other scalar slots differ (`ctrl_wait -312`, `done -308`, `offset -300`; `bgbmp` is stored at `-296`). This points to local/register assignment inside an already matching frame, not a frame-size or buffer-scope mismatch.

The source declaration order already follows the historical DIE order, with `bgbmp` last. Source-backed pointer-type trials restored `BITMAP *bgbmp` alone, then the historical local pointer types for `selectedProfile`, `old_font`, and `bgbmp`. Both compiled to the same effective `select_profile` identity as the untyped corrected baseline (`f05c05d7…`), still 3115/3070 and first mismatch +64; the 11 exact neighbors remained unchanged. These trials eliminate pointer spelling as a lever. No source-backed declaration or lifetime change remains supported by the local DWARF evidence, so this follow-up stops at the frame-allocation blocker.

Artifacts for the follow-up are `bitmap_local_type.c`, `historical_pointer_local_types.c`, their paired body files, and `build/<variant>/comparison.json`; `build/any_gated_wait/dwarf.txt` retains the candidate sibling DIEs.
