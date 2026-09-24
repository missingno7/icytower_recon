# Isolated `view_profile` interface probe

## Hypothesis and edits

Historical profile CU DWARF records `int view_profile(Tprofile *)`. The maintained source instead declares/defines `void view_profile(void *)`, and `menu.c` declares `extern void view_profile(void *)`. `Tprofile` is already generated from locked DWARF as a 1,360-byte aggregate. This probe changed only those three signatures and added `#include "recovered/Tprofile.h"` to `menu.c`; the function body and all other declarations remained unchanged.

## Locked full-CU result

Ran `tools/tu_context_probe.py` separately for full `game-profile` and `game-menu` CUs with the retained overlay. Both strict comparisons compile successfully. Profile preserves all 11/17 exact function matches; menu preserves all 7/10. No exact peers are gained or lost. Candidate `interfaces.aux` files state `extern int view_profile (Tprofile *)` in both CUs. The implementation candidate remains DIFFER (2,160 vs historical 2,249 bytes); `handle_menu` remains DIFFER (1,066 vs historical 1,120 bytes). No function-match claim follows from the interface correction.

The `.text`, `.data`, `.bss`, and `.rdata` section hashes are unchanged from current reports. All relocations in code/data sections are identical (profile: 467; menu: 217), and common allocations plus initialized-data comparisons are unchanged. The total relocation counts remain 798 and 395. Debug sections and debug relocation offsets change because the typed signature alters DWARF; therefore these are not object/CU matches and the full relocation tables are not byte-identical.

## Gate status

This is an evidenced isolated candidate, not a promoted interface repair. `docs/current/interfaces/view_profile.json` still routes to `TYPE_LAYOUT_BLOCKED`: the card sees candidate `void` pointers and blocks declaration planning before it can apply the generated `Tprofile` type. Current production `interface_task.py` also insists all named aggregate layout issues be repaired before planning any interface edits, so there is no strict promotion receipt for this candidate yet. `handle_menu` has an `AGREE` card for its own signature; only its external `view_profile` declaration needs the coupled update.

## Artifacts

- Candidate overlays: `profile.c`, `menu.c` in this directory.
- Compact metric receipt: `result.json`.
- Strict full-CU reports and compiler aux/DWARF: `../../../../build/tu-context/game-profile/view-profile-typed-signature-20260924/` and `../../../../build/tu-context/game-menu/view-profile-typed-signature-20260924/`.
- Locked commands used `--research-base`, `--order current`, `--no-prototypes`, `--no-dumps`; no production sources, headers, cards, or ledgers were changed.
