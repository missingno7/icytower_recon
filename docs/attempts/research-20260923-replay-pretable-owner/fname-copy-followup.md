# Replay selector delete-buffer ownership probe

Research-only locked TDM-2/GCC 4.4.1 `-O2` probe. No maintained source, current-state artifacts, card, or recovery ledger was changed.

## Historical evidence and change

Original `replay_selector` DWARF maps `char fname[512]` to frame offset `-1056` in lexical block DIE 223836, whose range includes the delete branch. The original line table at offsets 1834–1852 copies `"Really delete replay?"` into that buffer; offsets 1852–1925 then pass `fname` as `my_alert` argument 1 and the warning string as argument 2. The corrected isolated source now mirrors that order: under the original delete preconditions it calls `strcpy(fname, ...)`, then calls `my_alert(fname, warning, 1, 0)`.

The historical source line table for `get_replay_property` establishes case order `score` (line 253), `floor` (254), `combo` (255). The maintained/current order was score, combo, floor. A second isolated edit moves the floor case before combo, preserving the property mapping and behavior.

## Strict results

The combined candidate retains the owner-aligned folder chooser/title/header edits from `folder-title-period-source.c`, plus the DWARF-supported delete-buffer copy and historical property-case order.

- Generated 83-entry switch-table relocations occupy `.rdata+0x1b8` through `+0x304` (end exclusive), matching the historical start (`+0x1b8`); the prior candidate occupied `+0x1b4` through `+0x300`.
- `_replay_header` remains a `.rdata` symbol at `+0x470`.
- Pool owners now align: `itr` `+0x154`, folder title (with period) `+0x158`, empty-string suffix reference `+0x17a`, delete question `+0x17b`, and warning `+0x194`.
- `get_replay_property` is strict `FUNCTION_MATCH`; its two prior unequal literal relocations at offsets 916/1036 resolve after source-order restoration. The messages are `%s:combo=%d` and `%s:floor=%d`; original code associates +916 with combo at `+0x3ea` and +1036 with floor at `+0x3de`. Candidate pool now has floor at `+0x3de`, combo at `+0x3ea`.
- `create_replay` remains `FUNCTION_MATCH`. `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, and `update_file_list` remain exact.
- `replay_selector` is still `DIFFER` and does not meet promotion criteria. `draw_replay_selector` and `load_replay` also remain `DIFFER`; the full CU has 8 `FUNCTION_MATCH` and 7 `DIFFER` results.

## Artifacts

- `fname-delete-copy-source.c`, `fname-delete-copy-summary.json`, and `fname-delete-copy-functions.json`: intermediate copy-only probe. It fixes string/table ownership but leaves the helper's two floor/combo references swapped.
- `property-case-order-source.c`, `property-case-order-summary.json`, and `property-case-order-functions.json`: combined source-supported candidate and strict report.
- Compiler object and dumps: `build/tu-context/game-replay/replay-selector-fname-copy-property-case-order-probe-20260923/`.

This establishes the original-backed causal mechanism for both the four-byte table position and the helper's two remaining references in the prior owner-aligned candidate. It is research evidence only; no protected production body was changed or promoted. The combined source changes the case order inside the existing `FUNCTION_MATCH` body `get_replay_property`; the current repository rule forbids editing that protected production body even though this isolated compile keeps its emitted function exact. `replay_selector`, `draw_replay_selector`, and `load_replay` also remain different, so the combined source is not a serial acceptance candidate under the present gates.
