# Profile directory interface probe (2026-09-24)

## Question

`create_profile` in `src/profile.c` is routed to the supervisor queue because its direct prerequisite `get_profile_dir_for_profile` has an `INTERFACE_CONFLICT`. The callee's current card is already `FUNCTION_MATCH`. This probe checks whether spelling the parameter as `size_t` instead of `unsigned int`, or using the shared `directories.h` declaration, changes the full `game-profile` translation unit or harms its exact functions.

## Current evidence

- `docs/current/functions/directories/get_profile_dir_for_profile.json`: `FUNCTION_MATCH`, 63 bytes, historical and candidate signature `int get_profile_dir_for_profile(char *, size_t, const char *)`.
- `docs/current/interfaces/get_profile_dir_for_profile.json`: supervisor `INTERFACE_REPAIR`; recorded historical signature uses `size_t`; reason is `unsigned int -> size_t`.
- `src/profile.c` has a duplicate declaration with `unsigned int buflen`; `include/directories.h` uses `size_t buflen`.
- The retained debug type probe in `docs/current/reports/game-profile.json` gives `size_t` as a four-byte `unsigned int` (`DW_ATE_unsigned`). On this target the two spellings have equal ABI width and compatible types.
- `create_profile` remains `DIFFER` at offset 69: original byte `0x75`, candidate `0x7d`, aligned as `test %esi,%esi` versus `test %edi,%edi`. The interface declaration is not evidence for this body mismatch.
- `docs/attempts/game-profile/create_profile.jsonl` has 16 retained records. Fourteen report the same mismatch at offset 508; the last two report offset 69. Entries 2–16 share the same retained body SHA-256 `3b119575b6f4ce1dc1854466c5e22e589bbeb15071bbc7038447ca090e3b130e`, so these records do not represent 15 distinct body candidates.

## Isolated full-TU probes

Both probes use `python tools/tu_context_probe.py game-profile src/profile.c ... --order current --no-prototypes --no-dumps --focus create_profile`, TDM-2 at the target's locked `-O2` settings, and compile the whole CU. No maintained source, header, current card, or production ledger was edited.

1. `profile-interface-baseline-20260924.json` is the unmodified full-TU control.
2. `profile-shared-header-20260924.json` removes the local `extern` and inserts `#include <directories.h>` after `allegro.h`.
3. `profile-size_t-spelling-20260924.json` replaces the local `unsigned int` prototype with a `size_t` prototype. The probe inserts this declaration after `get_controls`; that declaration movement is a debug/source-layout confound, so the shared-header candidate is the more actionable mechanism.

The declaration specifications are archived beside this file. Probe report and object paths are under `docs/attempts/tu-context/game-profile/` and `build/tu-context/game-profile/` using the labels above.

## Results

The baseline and both candidates have the same strict status for every profile function: exactly 11 `FUNCTION_MATCH`, no gains, and no losses. The 11 exact functions are:

- `hash2`
- `generate_profile_checksum`
- `get_rank_id`
- `get_rank`
- `set_next_rank_message`
- `profile_data_page_advanced`
- `profile_data_page_basic`
- `profile_data_page_extra`
- `save_profile`
- `load_profile`
- `delete_profile`

The other six remain `DIFFER`: `create_profile`, `draw_profile_selector`, `draw_buffer`, `profile_data_page_general`, `view_profile`, and `select_profile`.

The isolated COFF controls are stronger than status counts alone: baseline and both candidates have identical `.text` (11,528 bytes), `.data` (416 bytes), `.rdata` (1,860 bytes), and `.bss` contributions. All 425 `.text` relocations and 27 `.data` relocations are identical. Therefore the two source spellings deduplicate to one emitted code/data outcome for this compiler and TU.

Whole object identities differ because debug records differ. The shared-header candidate changes `.debug_info`, `.debug_line`, `.debug_loc`, and `.debug_pubnames`; the spelling candidate also changes debug sections. These are not object/CU matches, and no equality claim is made for them.

## Handoff

The evidence supports an isolated candidate mechanism: replace the duplicate `profile.c` declaration with the shared `directories.h` declaration. It is code/data neutral in this full-CU compile and preserves all 11 strict function matches. It does not improve `create_profile`, establish debug/CU equality, or itself clear the generated interface conflict. The current interface card names `src/directories.c` and does not plan a repair in the caller CU, so any maintained change needs a supervisor-owned cross-CU interface decision and its normal interface acceptance workflow. Keep `create_profile`'s body unchanged while this prerequisite is unresolved.
