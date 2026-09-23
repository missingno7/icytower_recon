# `replay_selector` caller CFG and call-site follow-up

Research-only full-TU overlays with locked TDM-2 / GCC 4.4.1 `-O2`. Every probe uses the owner-aligned `property-case-order-source.c` as its retained full-TU base and `src/replay.c` as canonical CU identity. No maintained source, recovery status, card, or generated state was changed. The prior `draw_replay_selector` analysis remains separate; these experiments change only the caller body.

## Source-backed original call structure

`function_lines.py game-replay replay_selector --calls-by-line` and original PE disassembly show these caller-site facts:

- Original `update_file_list` has one source/call site (line 732). The owner-aligned candidate calls it at three sites: after directory entry, after folder selection, and in the shared `need_to_update` path. The original directory and folder paths instead set state and reach the shared refresh path.
- Original has three `destroy_replay` sites. The candidate initially had two. The missing site is immediately before the folder picker: line table lines 786/789 and disassembly offsets +2292..+2321 show `play_menu_select`, a conditional `destroy_replay(rep)`, then GUI color setup and mouse/file-picker calls. The original later clears `rep` while resetting selection/offset. This block is independent of the draw-selector calls.
- Original stores `1`, `2`, `3`, and `4` directly to global `sort_method` in the four sort-key arms. Calling `set_sort_method(value)` is a candidate source-level call addition; the helper's complete body is only `sort_method = sm`.
- Original direct external-call multiplicities are 59 call instructions total, including two indirect calls. At owner control, the candidate has 55 total: 2 destroys, 3 updates, 2 draws, and 1 load as same-CU calls. Original same-CU counts are 3 destroys, 1 update, 2 draws, and 1 load.
- Other evidenced call-site differences: original has 2 `is_any`, 2 `keypressed`, 4 `play_menu_select`, 1 `play_menu_move`, and 4 `makecol`; owner control has 1, 1, 2, 2, and 2 respectively.

## Isolated outcomes

The direct-sort-store variant compiles to the same effective function output as control (`f607ff93e72c58a8` identity); strict output grouping confirms the exact same 2662-byte target. GCC inlines `set_sort_method`, so removing the source-level helper calls alone does not change target bytes.

`defer-list-update.c` removes the two nested `update_file_list` calls and leaves the shared refresh. Its same-CU calls become 2 destroys, 1 update, 2 draws, and 1 load. It is a distinct effective output: 2606/2845 bytes, DIFFER at +8, frame `0x27c`, 73 branches, 52 calls, 93/96 unequal relocations, and 8 exact functions out of 15.

`folder-event-order.c` restores the source-backed folder picker prelude, conditional destroy, color initialization, `rep = NULL`, and shared refresh. It gives the target 2743/2845 bytes, DIFFER at +8, frame `0x27c`, 74 branches, 57 calls, 99/102 unequal relocations, and the same 8 exact functions. Same-CU call multiplicities now match original (3 destroys, 1 update, 2 draws, 1 load). External `makecol` reaches 4; `play_menu_select` reaches 3.

The controller-wait-gate variant adds the second original `is_any` query and the idle reset evidenced at offsets +399..+436. The delete-select-sound variant restores the `play_menu_select` site before the delete alert at original +1829. A cumulative `caller-call-count-candidate.c` includes both with the folder-event corrections. Its output is 2791/2845 bytes, DIFFER at +8, frame `0x27c`, 75 branches, and 60 calls versus 59 original. The exact 8/15 neighbor set is unchanged. Its external `is_any`, `keypressed`, `play_menu_select`, and `makecol` multiplicities match original; the remaining external-call count discrepancy is `play_menu_move` (candidate 2, original 1).

`shared-move-sound.c` moves both candidate movement paths to a common label, testing the single historical call site at line 823. GCC emits the same effective function output as `folder-event-order.c` (2743 bytes, 57 calls); this source refactoring does not create a new compiler outcome.

All receipts preserve the same eight exact replay peers: `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, `create_replay`, `save_replay`, and `get_replay_property`. Every target stays DIFFER; the prior direct-sort-store, movement-label, controller, delete-sound, folder, and refresh probes make no exact-function gains/losses. The owner-aligned predecessor count remains 15/15.

## Boundary and artifacts

The static caller sites now have an evidence-backed explanation for the nested list refreshes, folder-picker destruction/reset, and most direct-call multiplicities. The shared movement label collapses to the prior GCC result; its one-extra `play_menu_move` call remains unexplained at the source level. The cumulative candidate still differs at its frame prologue (+8), has 75 versus 67 historical branch instructions, and has thousands of differing bytes/relocations; the call corrections do not establish CFG equality or a function/layout match. Prior branch-scoped buffer probes already cover the `fname`/`p` lifetimes and are not repeated here.

Retained bodies: `direct-sort-stores.c`, `defer-list-update.c`, `folder-event-order.c`, `controller-wait-gate.c`, `delete-select-sound.c`, `shared-move-sound.c`, `caller-call-count-candidate.c`.

Receipts/builds use labels `replay-selector-cfg-{control,direct-sort,defer-list,folder-event,controller-wait,delete-sound,shared-move,caller-count}-20260924` under `docs/attempts/tu-context/game-replay/` and `build/tu-context/game-replay/`.
