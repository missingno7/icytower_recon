# `draw_replay_selector` scrollbar follow-up

Research-only TDM-2 / GCC 4.4.1 `-O2` continuation using the combined owner-aligned replay TU. No maintained source, current generated state, recovery ledger, cards, protected body, or sibling repo was edited.

## Original evidence

- `function_lines.py game-replay draw_replay_selector --lines` puts the scrollbar calculation at original offsets 423–594 (`replay.c:483`, then inlined `draw.inl:88`) before the lower details frame at 609–680 and before row presentation. The fill itself is unconditional in this CFG range.
- Historical machine instructions set x bounds to `x+0x129` and `x+0x12f` (x+297 and x+303). `fg` is the value in the local at `ebp-0x438`.
- At offsets 99–140 the code loads global `num_itr_files`, stores the `int` at `ebp-0x424`, uses `fidivrl max_posts`, and clamps. The reverse divide yields `p = max_posts / num_itr_files`. DWARF and storage evidence identify `num_itr_files` as a global signed `int` in `.bss`; there is no local snapshot DIE. DWARF lists top-scope `int i` without a location; the instruction at offset 1029 later reuses `ebp-0x424` as the loop index. This supports stack-slot reuse, but does not identify a source local that must own the initial count value.
- Historical x87 computes `T = 266*(1-p)*offset/(num_itr_files-max_posts)`, then bottom `y+32+266*p+T` and top `y+32+T`. The FISTP conversions apply to the complete coordinate sums.

## Isolated probes and strict result

`scrollbar-historical-order-20260923-source.c` corrects the ratio/precision and formula, removes the unsupported zero guard, and places the fill before the details frame in original line/CFG order. It compiles with a 0x49c frame, matching historical, and the x87 fraction spill/store locations at +198/+207/+244 match original. The result remains **DIFFER**, 3730 bytes vs 3726; first difference is +95 where candidate stores the second `makecol` result to `ebp-0x444` but original stores it to `ebp-0x440`. Historical then loads/stores `num_itr_files` through `ebp-0x424`; candidate directly emits `fildl _num_itr_files`.

A discriminating source-level snapshot probe declares `int file_count = num_itr_files` and uses it for the ratio and scrollbar denominator. It causes an explicit load/store/FILD sequence, but GCC assigns it to `ebp-0x42c`, not the historical `-0x424`, and it does not change the +95 first mismatch, size, or strict status. The exact source and comparison are retained in:

- `scrollbar-historical-order-20260923-source.c`, `...-summary.json`, `...-functions.json`
- `scrollbar-count-snapshot-20260923-source.c`, `...-summary.json`, `...-functions.json`
- `build/tu-context/game-replay/scrollbar-historical-order-20260923/`
- `build/tu-context/game-replay/scrollbar-count-snapshot-20260923/`

Both variants preserve the eight exact functions: `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, `create_replay`, `save_replay`, and `get_replay_property`. `draw_replay_selector` remains DIFFER; the other six functions retain their previous DIFFER status. The formula probe changes no call or data owner: direct call counts and indirect GFX targets (`+0x44: 4`, `+0xbc: 3`, `+0x3c: 2`, `+0x48: 4`) and the eight datafile member offsets remain as in the immediately preceding background/details probe.

## Boundary

The original CFG, literal call, bounds, ratio, x87 equation, source order, candidate frame size, and fraction spill schedule are accounted for. The remaining early mismatch is local instruction scheduling/allocation: the color result is assigned to a different local slot, and the original's temporary count snapshot reuses the later loop-index slot. The snapshot probe confirms a normal local declaration is insufficient to reproduce the historical `-0x424` reuse. No DWARF DIE identifies the temporary itself or provides a source-level lifetime/owner constraint for that slot, so further forcing would be speculative. No promotion or maintained edit is appropriate.
