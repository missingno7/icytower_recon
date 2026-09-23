# Profile selector interface research

Current cards: `docs/current/interfaces/draw_profile_selector.json` and `select_profile.json` are both `TYPE_EVIDENCE_INCOMPLETE` / `TYPE_LAYOUT_BLOCKED`. Current focused function cards remain DIFFER (`draw_profile_selector`: `STACK_FRAME_LAYOUT`; `select_profile`: `REGISTER_OR_INSTRUCTION_SELECTION`). The shared dependency edges are in `docs/current/task-dependencies.json`.

## What the blocker means

The layout checker is not missing the historical types. The locked DWARF graph and generated headers give complete layouts: `Tprofile` is 1360 bytes (`handle[32]` at byte offset 6); `Tavailable_profile` is 32 bytes (`handle[32]` at offset 0). The profile CU's `-aux-info` declarations spell the selector's handle arguments as `char *`, so `layout_checks` looks for a candidate aggregate named `char`, finds none, and emits `UNAVAILABLE: Candidate named type layout is missing or ambiguous`. This is a misleading status for this case: the actual historical aggregate evidence exists, while the candidate declarations erase the aggregate types.

This occurs at `src/profile.c:130,149,712` for `draw_profile_selector` (both params 2 and 3) and `src/profile.c:131,150,765` for `select_profile` (param 2). There are also ordinary declaration conflicts: `draw_profile_selector` uses candidate `void *` where historical DWARF says `BITMAP *`; the other aggregate spellings and pointer/return positions of `select_profile` canonicalize correctly (`Tprofile_create` -> `Tprofile`, `Tprofile_control` -> `Tcontrol`).

DWARF's historical declarations are explicit: `draw_profile_selector(BITMAP *, Tprofile *, Tavailable_profile *, int, int, int, int, int, int)` and `select_profile(Tprofile *, Tavailable_profile *, int, Tcontrol *) -> Tprofile *`. On the locked 32-bit target all these object-pointer arguments occupy the same 4-byte cdecl slots, so current candidate pointer spellings do not by themselves establish an ABI stack mismatch. They do erase type/debug evidence and leave body pointer arithmetic written against a byte view. The existing code can be updated to the evidenced member view (`Tprofile.handle`, `Tavailable_profile.handle`) because the member names, offsets, and dimensions are DWARF facts; the address arithmetic must be changed with the declarations and caller expressions as a unit.

## Isolated probe

`fixtures/profile-handle-pointer-v1.c` compiled with locked TDM GCC 4.4.1 TDM-2, `-m32 -O2`. The generated assembly for byte-view and typed-member address expressions is identical for both cases:

- `(char *)profile + 6` vs `profile->handle`
- `(char *)profiles + i * 32` vs `profiles[i].handle`

This is a discriminating local compiler fact, not complete body or object proof. Results and SHA-256 identities are in `probe-summary.json`; exact assembly and command receipt are in the sibling `.s` and `.log` files.

## Prior experiments and status

The focused `draw_profile_selector` body ledger (`docs/attempts/game-profile/draw_profile_selector.jsonl`) has only three retained candidates and they differ in frame allocation; none tests corrected aggregate interfaces. No separate `select_profile.jsonl` body ledger exists. Retained body snapshots are in `docs/attempts/game-profile/bodies/`. Thus the current interface blocker is not explained by prior interface experiments. The actual shared prerequisite is available and should be repaired only in an isolated, coupled signature/body/caller candidate, then checked with the existing strict interface acceptance path after layout issues are addressed.

## Next discriminating experiment

Create an isolated profile.c overlay that changes the selector declarations/definitions to the historical pointer types, changes profile-name accesses to `.handle` / `->handle`, changes `select_profile`'s two selector calls to pass the `Tprofile *` itself, and changes profile-list accesses to `.handle`. Compile the complete CU and compare every function, data/BSS symbol, and relocation. Keep it research-only. The microprobe shows the byte-address expressions themselves can collapse to the same code, but it does not predict changed call-site or aggregate-debug emissions.


## Whole-TU coupling probe

The complete typed overlay (`overlay/profile.c`, TDM-2 `-O2 -g -mfpmath=387`) passed through `experiment.compare` with the original EXE used only as oracle. It retains 10/17 exact functions (baseline had 11/17), with `profile_data_page_advanced` losing its exact result; both selectors remain DIFFER. This was not just a debug/type-section change.

An isolated cause test added only `#include "recovered/Tavailable_profile.h"` at the file top, leaving every existing function body and signature unchanged. The compiler deterministically reproduced an unrelated `profile_data_page_advanced` mismatch at body offset 229, changing its 332-byte exact function into DIFFER. The effective code change is an adjacent instruction order swap for two independent initializations: the baseline stores zero to `rows` before clearing the `i` register; the header-visible build clears `i` before storing zero to `rows`. The `.text` identity changed and the strict CU result dropped from 11 to 10 exact functions. A repeat compile of the same header-only source produced the exact same complete object SHA-256, so this is deterministic.

A second control placed that same type include immediately after `profile_data_page_advanced`. That function then retained byte-identical output (same 332-byte function SHA-256 as baseline) and all 11 baseline exact functions remained exact. This isolates the effect to declaration placement/context before that function is emitted. It establishes a declaration-order dependent GCC 4.4.1 whole-TU codegen effect; it does not establish that `profile_data_page_advanced`'s source is wrong. Do not repair that witness function to compensate.

Receipts: strict full-CU reports under `build/profile-current-baseline-v1`, `profile-interface-header-only-v1` plus repeat `v2`, `profile-interface-late-header-v1`, and `profile-selector-typed-interface-v3`. Full disassembly of the witness is retained as `advanced-baseline.asm`, `advanced-early-type.asm`, and `advanced-late-type.asm`. Function-slice hashes/diffs can be regenerated from those COFF objects and reports. Exact identity loss is a context effect; it is not counted as a recovered function.
