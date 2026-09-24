# do_replay_menu isGuest normalization batch (2026-09-24)

## Question and prediction

The current focused card reports a first mismatch at function offset `+397` (VA `0x411125`), next to the `isGuest` branch feeding the historical shared name-copy edge. Before compiling, the prediction was: if boolean spelling changes the register/frame/control output, this local normalization could explain the early mismatch; if all forms collapse, close this source family and move to register liveness/source lifetime evidence.

## Experiment

Compiled the full `game-main` TU using locked `tdm-2` / GCC 4.4.1, historical definition order, no prototypes, with three complete body overlays: maintained `!stricmp(...)`, equivalent `stricmp(...) == 0`, and equivalent explicit `stricmp(...) ? 0 : 1`. Maintained `src/main.c` SHA-256 was `bee055ec1ae6c0dc3cea12de393560b0974302b0cf559cca6dd3cfb55f924533`; base TU overlay identity was `bee055ec1ae6c0dc3cea12de393560b0974302b0cf559cca6dd3cfb55f924533`.

## Result

All three compiled and collapsed to effective identity `af771be203e8505150db8b81b158d6f4a255702fab407694077abd0a52f7986e`. Each leaves `do_replay_menu` `DIFFER`, 2657/2661 bytes, first mismatch `+397`. The first candidate instruction is at `+396`: `mov -0x1820(%ebp),%edi`; the historical counterpart reads the same stack slot into `%edx`. Branch count (43), named call count (63), non-call relocation count (76), and mismatch-byte count (882) are identical across variants. The local boolean spellings do not affect this register choice or the target residue.

The full TU retains 64/82 strict exact functions before and after, with zero gains/losses and 79/82 historical predecessor identities. The function's effective call edges still show one missing historical edge (`ext_4b2a3c`) and one extra candidate `memset`; this is a concrete separate source/call-ownership lead, not interpreted here. No function, object, or CU match is claimed.

## Decision / next discriminator

This experiment does not change the immediate recovery decision: stop varying `isGuest` boolean spelling. The next investigation should inspect the historical/candidate register live ranges and local lifetimes around `+396..+410`, especially why `%edi` is selected instead of `%edx`, and identify the unresolved `ext_4b2a3c` edge from original call/data evidence before proposing another body edit. Prior declaration-order and nested-checksum-scope probes already exist; do not repeat those.

## Artifacts

- `control.c`, `eq_zero.c`, `explicit_01.c`: exact full body overlays.
- `predictions.md`, `batch-manifest.json`, `results.json`: precompile prediction, reproducible batch recipe, compact outcomes.
- Receipts: [control](../tu-context/game-main/replay-menu-isguest-control-20260924.json), [eq_zero](../tu-context/game-main/replay-menu-isguest-eq_zero-20260924.json), [explicit_01](../tu-context/game-main/replay-menu-isguest-explicit_01-20260924.json).
- Full compiler artifacts remain under `build/tu-context/game-main/replay-menu-isguest-*-20260924/`.
