# `rebuild_profile_list` interface follow-up

## Evidence

The focused interface card is blocked because the profile CU declares `extern int rebuild_profile_list(char **profs);` at `src/profile.c:108`. Locked DWARF and the generated type header establish the function signature as `int rebuild_profile_list(Tavailable_profile **profs);`; `Tavailable_profile` is 32 bytes, with `handle[32]` at offset 0. The implementation in `src/main.c` and its focused function card already use the typed signature and remain an exact 198-byte function match. The problem is the cross-CU declaration seen by the profile caller.

The existing isolated typed selector overlay includes `Tavailable_profile.h` only after `profile_data_page_advanced`, because making the type visible earlier changed that exact neighbor. A declaration moved to that existing late point can express the correct type without disturbing the witness.

## Probe

`overlay/rebuild_profile_list_typed_late_decl_v1.c` removes the `char **` declaration and reintroduces `extern int rebuild_profile_list(Tavailable_profile **profs);` immediately after the late type include. The caller expression remains `rebuild_profile_list(&profiles)` with `profiles` typed as `Tavailable_profile *`.

The locked full-CU compile emits the typed prototype in `interfaces.aux` and no longer warns about an incompatible `rebuild_profile_list` argument. The strict report covers all 17 profile functions, initialized data, common/BSS, and relocations. It retains the same 11 exact functions as the typed late-header baseline. `select_profile` remains 2698/3070 DIFF, with the same effective function output and first mismatch +12; `draw_profile_selector` likewise remains unchanged at 1250/1268. No code emission changes in the caller CU, and no object or CU match is established.

## Outcome and scope

The evidence supports a precise declaration repair for the caller CU. It clears the aggregate type erasure at the call declaration without changing emitted output. The existing interface card checker should therefore stop reporting the `char`/missing-layout issue when this declaration is represented in the maintained source. This research probe did not edit maintained source, cards, ledger, generated state, or another agent's directory.

The production `python tools/interface_task.py begin rebuild_profile_list` gate
currently rejects this card as `SUPERVISOR` with the reason "Repair or establish
the named aggregate layouts before editing this interface". The isolated
result does not bypass that gate; a separate strict declaration-promotion path
is still required.

## Receipts

- `result.json`: compact outcome and exact neighbor set.
- `overlay/rebuild_profile_list_typed_late_decl_v1.c`: isolated full-TU source.
- `build/rebuild_profile_list_typed_late_decl_v1/comparison.json`: strict report for the complete profile CU.
- `build/rebuild_profile_list_typed_late_decl_v1/interfaces.aux`: compiler-confirmed typed declaration.
- `build/rebuild_profile_list_typed_late_decl_v1/build-provenance.json`, logs, object, dependency, DWARF, and other compile artifacts.
