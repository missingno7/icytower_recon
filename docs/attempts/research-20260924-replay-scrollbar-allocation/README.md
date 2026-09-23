# Replay scrollbar stack allocation follow-up

Research-only locked TDM-2 / GCC 4.4.1 `-O2` full-TU overlays. The retained full-TU base is `docs/attempts/research-20260923-draw-replay-selector-frontier/scrollbar-historical-order-20260923-source.c`; canonical CU identity is `src/replay.c`. The batch wrapper does not expose `--research-base`, so the control and two candidate overlays were compiled directly with `tools/tu_context_probe.py`. No maintained source, cards, recovery ledger, or generated state was edited.

## Source and DWARF evidence

- Original `fh` (DIE 222403) has fixed EBP-relative location `-1076` (`-0x434`). `fg` (DIE 222454) is at `-1080` (`-0x438`).
- Original `i` (DIE 222418) is a top-scope signed `int` with no DWARF location. `mg` (DIE 222469) is also top-scope, but has a location list (`0xa8ff`), not a fixed slot. `view_percentage` (DIE 222484) lives in `st(1)`; `view_offset` has no location. Neither DIE assigns the count temporary to a source local or identifies the second color result as `mg` at the first point it is stored.
- Original code stores the second `makecol` result at `ebp-0x440`; after it loads `num_itr_files`, it stores the count at `ebp-0x424` and executes `fild` from there. The same `-0x424` slot is reused later. This is consistent with a temporary's short lifetime, but the DWARF does not prove the source declaration or name for that temporary.

## Isolated declaration probes

The control recompiled at 3730/3726 bytes, DIFFER, first mismatch +95, and 8 exact functions out of 15. `draw_replay_selector` keeps its 0x49c frame, 52 branches, and 52 calls.

`reuse_i.c` assigns `num_itr_files` to the already evidenced top-scope `i`, then uses `i` in the ratio and denominator. GCC emits a count load/store/FILD sequence, but allocates it at `ebp-0x42c`, not historical `-0x424`. It retains the 0x49c frame, is 3730/3726 bytes, DIFFER at +95, and has 8 exact functions out of 15. Its normalized effective function identity differs from control; emitted-byte differences increase from 3321 to 3365. It does not move the second color result from `-0x444` to `-0x440`.

`scoped_file_count.c` shortens the count local's lexical lifetime around the ratio and scrollbar formula. Its normalized effective function identity collapses with `reuse_i`; it produces the same mismatch, sizes, frame, branch/call counts and exact-function set. The allocation still uses `-0x42c`. The test therefore gives no distinct compiler outcome for the shortened scope.

All three runs preserve the same eight exact replay peers: `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, `create_replay`, `save_replay`, and `get_replay_property`. All have the same historical predecessor count (15/15). The six non-exact functions keep their prior DIFFER status.

## Boundary

The DWARF supplies no source-level owner constraint for the temporary at `-0x424`. The evidence-backed `i` assignment and a shorter lexical count lifetime both miss that slot, while the color result remains at `-0x444`. Further forcing of either address would be speculative. Stop this declaration/lifetime line here unless new original source or debug evidence distinguishes the owners.

Receipts and compiled artifacts are retained as `luna-scrollbar-control-tu-20260924`, `luna-scrollbar-reuse-i-tu-20260924`, and `luna-scrollbar-scoped-count-tu-20260924` under `docs/attempts/tu-context/game-replay/` and `build/tu-context/game-replay/`.
