# `update_game_menu` final parameter research

Scope: isolated research only. No maintained `src/`, current generated state, or recovery ledger was changed.

## Evidence

- The original `update_game_menu` DWARF signature records the final parameter as `void **` (parameter DIE 159521). The current candidate declares `int *`.
- Original `handle_menu` DWARF records its local `data` as `void *`. The call site passes `&data`, so the caller-side object is a pointer slot and the callee writes a pointer value into it.
- The generated historical `Tmenu` layout declares `Tmenu.data` as `void *` at offset 144. This agrees with the current `handle_menu` source, which consumes the output as an opaque pointer.
- Therefore the historically supported operation is `*data = m[pos].data`; the maintained `(int)m[pos].data` narrowing cast is not supported by the recovered type evidence.

## Isolated probes

Two full `game-menu` CU overlays were compiled with the locked TDM-2 GCC 4.4.1 command in current definition order, with both `bmp` and the final parameter changed to their historical pointer types:

| Probe | Final parameter/store | CU exact functions | `update_game_menu` |
|---|---|---:|---|
| `luna-menu-data-voidpp-only-20260923` | `void **`; retained `(int)m[pos].data` cast | 7/10; no gains or losses | DIFFER, 582 bytes |
| `luna-menu-data-voidpp-corrected-store-20260923` | `void **`; `*data = m[pos].data` | 7/10; no gains or losses | DIFFER, 582 bytes |

The two candidate function instruction streams are byte-identical to each other (173 decoded instructions). The coupled type-and-store correction compiles cleanly and does not disturb any exact function. Neither overlay matches the historical body; the first mismatch remains in the earlier control-flow region, not the final store.

## Conclusion and blocker

The final-parameter type and pointer-store semantics are established by independent callee DWARF, caller DWARF, and `Tmenu.data` layout evidence. Pointer-size ABI equivalence was not used as proof. The correction is code-generation-neutral within these probes, but the current interface card has no generated edits and routes the combined interface conflict (`void *` to `BITMAP *`, plus `int *` to `void **`) to supervisor interpretation. I did not run `interface_task.py` because it edits maintained source and its generated task state; a production-interface promotion is outside this research lane. If promoted later through a supported interface task, the body’s direct pointer assignment should be admitted only as a separately scoped, historically evidenced body repair after interface acceptance.

## Artifacts

- Candidate overlays: `docs/attempts/research-luna-menu-interface/menu-data-voidpp-only.c`, `menu-data-voidpp-corrected-store.c`
- Probe runner: `docs/attempts/research-luna-menu-interface/run_probe.py`
- Probe receipts: `docs/attempts/tu-context/game-menu/luna-menu-data-voidpp-only-20260923.json`, `luna-menu-data-voidpp-corrected-store-20260923.json`
- Compiled comparisons: `build/tu-context/game-menu/luna-menu-data-voidpp-only-20260923/comparison.json`, `luna-menu-data-voidpp-corrected-store-20260923/comparison.json`
- Historical evidence: `docs/current/interfaces/update_game_menu.json`, `docs/current/functions/menu/handle_menu.json`, `include/recovered/Tmenu.h`
