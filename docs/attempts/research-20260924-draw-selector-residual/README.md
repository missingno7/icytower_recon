# `draw_replay_selector` residual investigation

Date: 2026-09-24. Research-only full-TU probes with locked TDM-2 / GCC 4.4.1 `-O2`. Production sources, generated current state, and recovery ledger were not edited. Probe labels are unique; sources and receipts are retained here and under `../tu-context/game-replay/`.

## Baseline

The best prior maintained-base result overlays the DWARF-backed `load_replay` body and selected-row assignments with split `name[1024]` / warning `rbuf[129]` storage. It preserves six maintained exact peers and makes `load_replay` a seventh strict function match. `draw_replay_selector` remains DIFFER: 3007/3726 bytes, first difference at +8 (the prologue reserve), frame `0x48c` versus original `0x49c`, 37 branches and 39 calls. Its receipt is `../tu-context/game-replay/load-replay-min-draw-dwarf-buffers-selected-20260924.json`; comparison detail is `../../../build/tu-context/game-replay/load-replay-min-draw-dwarf-buffers-selected-20260924/comparison.json`.

## Original selected-row path evidence

`original-selected-row.txt` is the original EXE disassembly from `0x41c1d0` through `0x41c50f`. The row loop calls `textprintf_ex` for the selected row at `0x41c4aa`, then calls `get_filename(post->full_path)` at `0x41c4ba`, stores its result in the DWARF local `curr_filename` at EBP-`0x448` (`0x41c4bf`), reads `post->version` at `0x41c4cb`, stores it at EBP-`0x450` (`0x41c4ce`), and stores the row's directory byte at EBP-`0x454` (`0x41c4d4`). These selected-row stores are after the row-render call in the original.

The prior successful draw context placed `show_directory` and `selected_version` stores before rendering and omitted the selected-row `curr_filename` call/store. Two probes test the evidence-backed missing call and its position:

| Variant | Draw bytes | Difference bytes | Frame | Calls / branches | Strict TU result |
|---|---:|---:|---:|---:|---|
| Add `curr_filename = get_filename(post->full_path)` in the existing early selected block | 3035/3726 | 2872 | `0x48c` | 40 / 37 | 7/15 exact; six prior exact peers retained and `load_replay` gains FUNCTION_MATCH |
| Move all three selected-row stores and the filename call after row rendering | 3080/3726 | 2920 | `0x48c` | 41 / 36 | 7/15 exact; same six peers retained and `load_replay` gains FUNCTION_MATCH |

The two variants have distinct effective output identities (`60393416dbebc8ce` and `2c38e0a769428927`). Neither recovers the missing 16 bytes of frame allocation or improves strict draw equality. Both are negative for the tested source-level cause; the second is further from the original function size. Receipts are `receipt-selected-filename.json` and `receipt-stores-after-row.json`; source variants are `draw-selected-filename.c` and `draw-selected-stores-after-row.c`.

## Context hypothesis status and blocker

The supervisor independently removed explicit `Treplay_post.reserved[2]` in its isolated research base. That changed `replay_selector` effective code but left `draw_replay_selector` output unchanged and preserved the seven strict functions. The aggregate/explicit-padding declaration is therefore not the cause of this draw frame or CFG difference.

Known DWARF locals account for the `name` and `rbuf` shared slot at fbreg -1056 and selected values at EBP-1108/-1104; the split-buffer probe recovers 880 of the original 896-byte frame gap. DWARF says `curr_filename` is a pointer at EBP-1096. Restoring its observed selected-row call/store changes code shape but leaves frame reserve fixed. Both double locals and tested lexical lifetime variants also left the best frame at `0x48c` (prior README). The 16-byte residual is therefore not explained by these evidenced local declarations. The full draw function still has a substantial code/CFG gap, and offset-based relocation windows are not safe ownership evidence across that shift; no layout-only conclusion follows.

Current blocker: recover the remaining original source/control-flow or a compiler-context cause for a 16-byte spill/outgoing-argument difference and the 719-byte function-size gap without introducing unsupported locals or source behavior. The focused card remains `DIFFER / STACK_FRAME_LAYOUT`; this research does not authorize promotion.

## Accepted replay TU transaction

The strict `TU_CONTEXT` transaction `replay_load_draw_historical_20260924` subsequently applied the typed `PACKFILE *pf` local in `load_replay` with the DWARF-scoped draw buffers and selected-row assignments after rendering. The first `check` reported `ACCEPTABLE`, six to seven exact functions, `load_replay` gained, no losses. `promote` reran locked acceptance, ordinary link, source-scope checks and the 156 function acceptance tests, then published the verified report and ledger. The transaction plan and final receipt are under `docs/current/tu-context-tasks/` and `docs/attempts/tu-context/transactions/`.

This promotes the strict `load_replay` result and a source-backed incomplete draw candidate. `draw_replay_selector` remains `DIFFER`; the 16-byte frame residual and wider code/CFG gap remain open. The type-padding probe and alternative replay-header owner branches were not included in this transaction.
