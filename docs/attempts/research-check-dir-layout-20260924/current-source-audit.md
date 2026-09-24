# Fresh current-source `check_dir` layout receipt (2026-09-24)

Scope: research-only historical-order whole-TU diagnostic. No source, generated current state, or recovery ledger changed.

## Probe

Command: `python tools/tu_context_probe.py game-main src/main.c research-checkdir-current-historical-20260924-noproto --order historical --no-prototypes --focus check_dir --focus new_game --focus run_demo --no-dumps`.

Receipt: `docs/attempts/tu-context/game-main/research-checkdir-current-historical-20260924-noproto.json`; strict comparison: `build/tu-context/game-main/research-checkdir-current-historical-20260924-noproto/comparison.json`.

- Compile succeeded; 63 `FUNCTION_MATCH` before and after, no gains or losses.
- `check_dir` remains `FUNCTION_MATCH` / `BODY_MATCH_LAYOUT_BLOCKED`, 103/103 bytes, at historical position 74.
- `new_game` and `run_demo` remain `FUNCTION_MATCH`.
- `check_dir` body shape, all five relocation targets, and direct call target (`log2file`) resolve equal. Candidate `call` bytes at `check_dir+27` are `e8 d8 da ff ff` (relative displacement -9512); original are `e8 74 da ff ff` (-9612). `layout_operand_equal` is false. This is the only body-local layout dependency; it is not a missing or wrong source operation.

## Exact TU placement dependency

Current historical-order candidate symbol offsets: `log2file=28344`, `check_dir=37824`, gap 9480. Original VAs: `log2file=0x40da58`, `check_dir=0x40ffc4`, gap 9580. The 100-byte gap shortfall equals the only intervening function-size difference: `init_game` candidate 5688 versus original 5788 bytes. Every other emitted function between the endpoints has its historical size, and total inter-function padding is 16 bytes in both layouts. Therefore the call displacement mismatch is fully explained by the current `init_game` body being 100 bytes short; editing `check_dir` would falsify its already-correct body.

This refreshes the older context note, which used an earlier `init_game` candidate at 5666 bytes and produced a -120-byte endpoint gap. Other saved historical-order overlays form one older effective `check_dir` code outcome (code SHA-256 `6be5d4202e15cc34e7e06039adea756c0418ac5cbb1cefe264d9f76741b2a903`, call displacement -9492); this current-source probe is a second outcome (code SHA-256 `0bf8c60a7fa61ea6b39f5ed92c55a7a9caf4a531bd585db4c193dd78767572d6`, displacement -9512). Both preserve 63 exact functions with no loss. They differ because surrounding TU content changed, not because `check_dir` body or relocations changed.

## Blocker

`check_dir` body edits are prohibited by the focused card (`body_edit_allowed: false`), and its interface is already `AGREE`. The remaining `BODY_MATCH_LAYOUT_BLOCKED` state depends on recovering `init_game`'s intervening source/code layout from semantic evidence. No check_dir-only source or declaration hypothesis is justified; no layout-targeted reorder or size filler was tested.

