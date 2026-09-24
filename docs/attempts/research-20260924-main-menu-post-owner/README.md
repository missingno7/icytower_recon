# `main_menu_callback` after owner correction

## Question and setup

Starting repository revision: `ca7c5e4e4df85489829f3909e7695b14d1f50c53`. The canonical source and the generated card were read before the probe. The accepted `old_msc`/`blit_mode` owner correction is present in the current source state; this research changed no maintained source, generated current state, or ledger.

A fresh whole-`game-main` TU control was compiled from `src/main.c`, current definition order, with `--no-prototypes`. It retained **64/82 FUNCTION_MATCH** functions and no changed effective code in unchanged function bodies. It is not an object or CU match. Focused control: `main_menu_callback` is DIFFER, 2,883 bytes versus 3,741 historical bytes; first mismatch is offset `+8`, `sub $0x23c,%esp` versus historical `sub $0x26c,%esp`.

The focused direct-edge report had historical calls to `LoadCursorA` twice, `get_rank` four times, and `get_rank_id` once; all three edges were missing from the current callback. Historical `function_lines.py` evidence for lines 5176–5179 gives a discriminating cursor branch: test `mouseInAd`, call `LoadCursorA(NULL, IDC_HAND)` on the true edge, call `LoadCursorA(NULL, IDC_ARROW)` on the false edge, and store either result to `_win_hcursor`. This also agrees with the original callback DWARF at VA `0x4100f8`–`0x410f95` and the independently decoded direct-call count of two.

## Isolated probe and result

The candidate overlays only that true/false cursor-call family at the retained cursor placeholder and supplies the historical Allegro cursor header through the probe declaration overlay. The probe used the same locked compiler, current TU order, and `--no-prototypes` as the control.

- Compile succeeded; no implicit declarations were introduced.
- Exact function count stayed **64/82**: no gains or losses. The callback remains DIFFER.
- Callback size is **3,051 bytes** versus 3,741 historical. Its first mismatch is still offset `+8` (`0x3c` versus `0x6c`), and strict byte differences rise from 2,644 to 2,678.
- The missing direct-call edge set shrinks from `LoadCursorA`, `get_rank`, `get_rank_id` to `get_rank`, `get_rank_id`. Direct-call multiplicities are historical 62, current control 49, cursor variant 55.
- No unchanged function has changed effective bytes. Raw same-CU call fields move in `_mangled_main`, `do_replay_menu`, `load_new_ad_image`, `play`, and `run_demo` as layout responses. The exact-neighbor set is preserved.
- The whole text contribution, initialized data, object, and CU remain unequal. This branch family is source-supported and confirmed as a focused output change, but it does not approach strict callback equality; continue with the separately evidenced rank/presentation and remaining source/data ownership gaps rather than varying cursor spellings.

## Retained evidence

- `main_menu_callback-cursor-branch.c` is the complete isolated function body.
- `cursor-declaration.json` records the required include and its historical basis.
- `cu-inventory.json.gz` contains both run inventories: all 82 function records, every initialized data symbol, every BSS and COMMON symbol, section sizes/hashes, initialized-data comparison summary, and every raw object relocation (4,447 control; 4,461 variant).
- Fresh receipts: `docs/attempts/tu-context/game-main/baseline-current-20260924.json` and `docs/attempts/tu-context/game-main/cursor-branch-20260924.json`.
- Strict object/function reports and COFF objects: `build/tu-context/game-main/baseline-current-20260924/` and `build/tu-context/game-main/cursor-branch-20260924/`.
- Original source line/CFG evidence: `python tools/function_lines.py game-main main_menu_callback --source-view 5176 5179`; retained pre-correction report: `docs/attempts/research-main-menu-rank-interface-full-20260923/README.md`.

The inventory is diagnostic. It does not upgrade a FUNCTION_MATCH, OBJECT_MATCH, or CU_MATCH claim.

## Serialized strict acceptance after later key correction

The retained cursor branch and its evidenced Allegro declaration were
rechecked after blit_debug_keys_20260924. The initial promotion attempt
passed 156 function tests but stopped at the source-provenance gate:
the changed incomplete callback body needed an explicit provenance update.
The native task was aborted, restoring its pre-cursor source. A new
main_menu_cursor_provenance_20260924 plan recorded the callback as an
incomplete_evidence_candidate with the cursor-branch and old_msc evidence.
Its whole-TU check returned ACCEPTABLE, 64 exact before and after, zero
gains/losses and 81 byte-preserved islands. Promotion then passed the
156 function tests, diagnostic link and global audit. The current source
still marks main_menu_callback DIFFER (first mismatch +8); no function
bytes were credited. The accepted transaction is
docs/attempts/tu-context/transactions/main_menu_cursor_provenance_20260924.json.
