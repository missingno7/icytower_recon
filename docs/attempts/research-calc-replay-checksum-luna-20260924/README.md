# calc_replay_checksum isolated investigation (2026-09-24)

This handoff records a read-only review of the current focused card, current verified replay CU report, current source/type context, original census/DWARF facts, and retained replay checksum probes. No maintained source, ledger, generated current document, or object was edited; no new compiler probe was run. Existing probe evidence remains at the cited paths.

## Current strict state

- `docs/current/functions/replay/calc_replay_checksum.json`: `DIFFER` / `SOURCE_DIFFER`, `UNKNOWN_SUPERVISOR`; historical 676 bytes, current 675, first strict difference at function offset 19 (`0x41bac4` historical start), 631 differing bytes. The card has no relocation mismatch, direct-transfer mismatch, unresolved call, literal, global, owner prerequisite, callee-interface issue, or local declaration task. `body_edit_allowed` in the card is true, but it is not a CHEAP task and the owner/strict-proof claim remains unresolved.
- Original DWARF confirms `int calc_replay_checksum(Treplay *r)`, `int i`, and `unsigned int sum`; source lines 188–215. `Treplay` is 2220 bytes. The card maps `size` at +8, `no_combo_top_floor` at +92, `biggest_lost_combo` at +96. Current source uses the generated `Treplay`/`Trecord` layouts and no checksum-local interface repair is pending.
- Current `docs/current/reports/game-replay.json` reports 15 historical functions, no extra functions, 7 `FUNCTION_MATCH`, 7 other `DIFFER`, 1 `CODEGEN_SIMILAR`; whole text, object, and CU are not equal. The checksum target itself owns no relocation. Adjacent `calc_replay_checksum_131` is `DIFFER`, same 177-byte size and same start offset; following `destroy_replay` is exact.

## Retained source-form trials

`python tools/effective_outcomes.py game-replay calc_replay_checksum --pattern 'checksum-luna-*.json' --compact --response` groups the 11 retained source-form trials under `docs/attempts/tu-context/game-replay/` into 6 effective instruction/relocation-normalized outcomes. Every outcome is strict `DIFFER`; none gained an exact function. The nearest outcome is 671/676 bytes with 374 differing bytes. Other outcome families are 675 bytes with 601–631 differing bytes. Tested forms include base spelling, additive coefficient expansion, grouped and reordered terms, splitting terms, and changing the final scale / sum update form. The receipt set also records no exact-neighbor gains.

The 2026-09-24 predecessor-context check is independently informative: `luna-checksum131-baseline` and `luna-checksum131-reverse-terms` produce two distinct effective outputs for `calc_replay_checksum_131` (177 bytes, 6 vs 5 differing bytes), but one identical effective `calc_replay_checksum` output (675 bytes, first difference 19, 631 differences). Thus that specific predecessor source rewrite does not move the checksum target. This does not exclude every compiler-context effect.

## CU accounting from the current report

Functions (original size / candidate size):

- `get_sort_method` 10/10 `FUNCTION_MATCH`
- `set_sort_method` 13/13 `FUNCTION_MATCH`
- `hash` 71/71 `FUNCTION_MATCH`
- `calc_replay_checksum_131` 177/177 `DIFFER`
- `calc_replay_checksum` 676/675 `DIFFER`
- `destroy_replay` 54/54 `FUNCTION_MATCH`
- `update_file_list` 184/184 `FUNCTION_MATCH`
- `draw_replay_selector` 3726/3772 `DIFFER`
- `create_replay` 254/254 `CODEGEN_SIMILAR`
- `load_replay` 1136/1136 `FUNCTION_MATCH`
- `replay_selector` 2845/2493 `DIFFER`
- `save_replay` 1227/1227 `DIFFER`
- `get_replay_property` 1147/1147 `FUNCTION_MATCH`
- `my_strcmp` 128/123 `DIFFER`
- `add_itr_file` 360/357 `DIFFER`

Current object accounting: candidate sections `.text` has 376 relocations (types 20: 203, 6: 173), `.debug_info` 212 (11: 134, 6: 78), `.rdata` 95 (type 6), `.debug_frame` 30 (15 each type 11/6), `.debug_aranges` 2, `.debug_line` 1, `.debug_pubnames` 1: 717 total. The report retains all entries. It marks 63 text relocations unresolved at CU level; none is in the checksum body. Common/BSS symbols are `_sort_method` (value 16), `_num_itr_files` (16), `_itr_file_list` (24576). Initialized-data comparisons are `.data` logical 7 bytes and `.rdata` 1152 bytes, both unequal; `.rdata` has 12 unresolved self-relocations. No whole-object or CU equality follows from text or focused-function results.

## Handoff decision

The current card plus 11 retained source-form probes do not identify a new semantic spelling that could plausibly bridge a 631-byte strict mismatch. No local ownership/interface prerequisite is evidenced. One predecessor body variation is excluded as a cause of checksum output, but it is not a complete test of compiler-context dependence. Any continuation should move to a specifically evidenced TU/compiler context question (and retain a fresh, unique isolated TU/pass probe) or remain supervisor-routed; this review does not justify editing the body or claiming layout-only equality.
