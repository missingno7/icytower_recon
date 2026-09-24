# Replay selector shared type and frame probe (2026-09-24)

Research-only replay CU experiment using locked TDM-2 / GCC 4.4.1 `-O2`, current definition order, and `--no-prototypes`. Maintained `src/`, generated current state, and recovery ledger were not changed.

## Historical type evidence

`docs/current/interfaces/draw_replay_selector.json` reports a `TYPE_LAYOUT_CONFLICT` for parameter 3. Historical DWARF gives `Treplay_post` size 24 and named members `full_path` (0), `directory` (4), `parent` (5), `version` (8), `score` (12), `floor` (16), and `combo` (20). It has no `reserved` member. Current `src/replay.c` inserts `char reserved[2]` at offset 6; that occupies the same bytes GCC naturally pads before `version`. The generated `include/recovered/Treplay_post.h` encodes the DWARF member list and asserts all offsets and total size.

The retained candidate replaces the local tagged declaration with `#include "recovered/Treplay_post.h"`: `replay-shared-Treplay_post-header.c`. A same-invocation source control was compiled from the maintained CU. `effective_outcomes.py` deduplicates both outputs to one draw function identity. Thus the canonical seven-member view fixes the source type discrepancy without changing current draw machine code or strict neighbor count in this probe.

## Batched current-context type trials

All four header-based retained source variants compile and preserve 7/15 exact CU functions with no exact gains or losses. Draw remains `DIFFER`; frame reserve is unchanged at `0x48c` (historical `0x49c`).

| Variant | Draw bytes | Differing bytes | Effective result |
|---|---:|---:|---|
| shared header; float locals | 3080/3726 | 2920 | same as explicit-padding control |
| `view_offset` double only | 3080/3726 | 2920 | same as float control |
| `view_percentage` double only | 3084/3726 | 2908 | distinct |
| both doubles | 3084/3726 | 2929 | distinct |

All remain 36 branches / 41 calls with 91/91 unequal or unresolved relocation comparisons. The new header plus float and `view_offset`-double probes deduplicate to `2c38e0a769428927`; the percentage-double and both-double forms have separate identities. Changing the local floating types changes some emitted bytes, but none changes the frame, CFG counts, function verdict, or exact-neighbor set. Earlier double/lifetime trials are indexed in `../research-20260924-load-replay-min-context/README.md`; these current-context probes confirm the result against the newly promoted 7/15 source state.

## DWARF frame and selected-row facts

Historical DWARF declares `view_percentage` and `view_offset` as `double`. The original prologue reserves `0x49c` bytes; current selected-row source reserves `0x48c`, a 16-byte residual. Historical `name[1024]` and warning `rbuf[129]` occur in distinct lexical blocks but both map to `DW_OP_fbreg -1056`, showing lifetime reuse of the same stack region. The current split-scope source follows that layout and gained 880 of the old 896-byte frame gap. `curr_filename` is a historical `char *` at EBP-1096. Original row code renders the selected row, calls `get_filename(post->full_path)`, stores that result, then stores `post->version` and `post->directory` into `selected_version` and `show_directory`; current retained source follows that sequence. The remaining 16 bytes are not explained by the tested type or lifetime declarations.

The current draw result is still 646 bytes shorter than the 3726-byte historical span, differs in 2920 byte positions, and has 91/91 relocation comparisons unequal/unresolved. It therefore has a substantial source/CFG gap as well as the 16-byte frame difference; no layout-only or function-match claim follows. The focused current card remains supervisor-routed because the shared `Treplay_post` type view differs.

## Receipts and source artifacts

- Interface/type evidence: `../../current/interfaces/draw_replay_selector.json`, `../../current/type-views/view_replay_Treplay_post.json`, `../../current/type-view-evidence/view_replay_Treplay_post.json`, `../../current/types/Treplay_post.json`.
- Header candidate: `replay-shared-Treplay_post-header.c`.
- Batched candidates: `replay-shared-type-current.c`, `replay-shared-type-double-offset.c`, `replay-shared-type-double-percentage.c`, `replay-shared-type-both-doubles.c`.
- Current header receipt: `../tu-context/game-replay/treplay-post-shared-header-current-20260924.json`.
- Explicit-member control receipt: `../tu-context/game-replay/treplay-post-explicit-control-current-20260924.json`.
- Double receipts: `../tu-context/game-replay/replay-shared-type-double-offset-current-20260924.json`, `../tu-context/game-replay/replay-shared-type-double-percentage-current-20260924.json`, `../tu-context/game-replay/replay-shared-type-both-doubles-current-20260924.json`.
- Grouping: `python tools/effective_outcomes.py game-replay draw_replay_selector --pattern 'treplay-post-*-current-20260924.json' --compact --response` and `python tools/effective_outcomes.py game-replay draw_replay_selector --pattern 'replay-shared-*-current-20260924.json' --compact --response`.
- Historical selected-row and accepted load context: `../research-20260924-draw-selector-residual/README.md`, `../research-20260924-draw-selector-residual/original-selected-row.txt`, and `../research-20260924-load-replay-min-context/README.md`.
