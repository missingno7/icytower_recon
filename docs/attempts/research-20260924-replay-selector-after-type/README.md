# Replay selector follow-up after `Treplay_post` acceptance

Research-only TDM-2 / GCC 4.4.1 `-O2` current-context probes, run after the seven-member generated `Treplay_post` header was accepted in `src/replay.c`. No maintained source, generated current state, or recovery ledger was edited. All receipts keep seven exact replay peers; no gains or losses occurred.

## Hypotheses

The current selected-row source already follows the DWARF-backed `curr_filename`, `selected_version`, and `show_directory` stores. Earlier current-context trials established that making `view_offset` and/or `view_percentage` `double` changes some bytes but never changes the `0x48c` frame. Those type trials are not repeated here.

This batch tests the remaining source-backed draw shape:

- `selected-alpha`: the historical selected-row block has `set_trans_blender`, `drawing_mode`, inlined `rectfill` (`draw.inl:88`), then `solid_mode`. The source bounds/color and alpha are retained from the earlier CFG reconstruction: `x+7, row, x+0x125, row+fh-9, fg`, alpha 50.
- `sprite-sort`: two unconditional sprite draws and the four-arm `sort_method` indicator switch, with asset indexes and coordinates recovered from original data references and CFG blocks.
- `selected-alpha-and-sprite-sort`: combined source-backed changes, to measure their interaction in the accepted header context.

The current-context baseline is retained as a control. All source bodies and the batch manifest are in this directory. The locked probe receipts and detailed strict comparisons are under `docs/attempts/tu-context/game-replay/` and `build/tu-context/game-replay/`.

## Results

| Variant | Strict status | Candidate / historical bytes | Frame | Effective outcome |
|---|---|---:|---:|---|
| Control | DIFFER | 3080 / 3726 | `0x48c` | `2c38e0a769428927` |
| Selected alpha | DIFFER | 3284 / 3726 | `0x48c` | `8dd39b52393e6e8e` |
| Sprite and sort | DIFFER | 3576 / 3726 | `0x48c` | `cffe79fafa3efb2e` |
| Both changes | DIFFER | 3720 / 3726 | `0x48c` | `6fa9f6833c09aa76` |

All four outputs are distinct after effective-output deduplication. The combined candidate is six bytes shorter than the historical span, but its first mismatch is still the prologue at offset 8, 3,551 bytes differ, and all 62 compared non-call relocations are unequal or unresolved. It is not a `FUNCTION_MATCH` or a proven layout-only match. The frame remains 16 bytes smaller than the historical `0x49c` allocation.

The selected-row experiment adds four calls and 204 bytes. The sprite/sort experiment adds 17 branches and 7 calls. Combining them preserves the seven exact peers but remains `DIFFER`. The new research does not explain the residual frame allocation or resolve relocation ownership.

## Follow-up boundary

The body-level source shape now includes these independently evidenced presentation blocks, but the strict gap remains broad despite the near-equal span size. Stop further cosmetic source variations. Continue by inspecting the selected-row/selector compiler context or the unresolved data/literal ownership and exact call layout; do not treat the six-byte span delta as proof of a match.

## Artifacts

- Candidate bodies and `batch-manifest.json`: this directory.
- Summary receipt: `docs/attempts/tu-context/game-replay/replay-selector-after-type-control-20260924.json` and sibling receipts for the three variants.
- Full batch metrics and effective hashes: saved by `python tools/batch_tu_probe.py` in the tool output and the comparison reports named by the receipts.


## Semantic audit and ordered retained body

A line-by-line diff against the maintained `draw_replay_selector` found only the two additions listed above. The sprite/sort block is between the title and first list clip, matching the original CFG order. Its asset indices and coordinates are independently recorded from original data references and branches in `research-20260923-draw-replay-selector-frontier/README.md`.

The earlier batch's `selected-alpha` and combined body placed the rectangle after the selected text call. That order was wrong: original disassembly places `set_trans_blender` (alpha 50), `drawing_mode` (mode 5), inlined `rectfill` and `solid_mode` before `_textprintf_ex` at `0x41c4aa`. Those earlier alpha-containing receipts are retained as failed ordering probes and are not the retained body. The corrected complete body in `retained-draw-replay-selector.c` places the alpha sequence in that original position. Its rectangle bounds and color are recovered from the original stack stores and DWARF, and `draw.inl:88` confirms vtable offset `0x3c` is `rectfill`.

A fresh locked current-order probe with the accepted generated header compiled this corrected body. It remains `DIFFER` at 3772/3726 bytes with frame `0x48c` versus historical `0x49c`; all seven current `FUNCTION_MATCH` peers remain exact, with no gains or losses. Receipt: `docs/attempts/tu-context/game-replay/replay-selector-after-type-retained-ordered-20260924.json`. The research-only spec is `transaction.json`.
