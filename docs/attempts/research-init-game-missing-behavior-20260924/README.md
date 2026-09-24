# `init_game` omitted behavior block recovery — 2026-09-24

Research-only reconstruction from the historical `main.c` line table and original instructions. No maintained source, generated current state, or recovery ledger changed. The run remains `DIFFER`; it is a source candidate for the supervisor's serialized transaction, not a promotion claim.

## Source and instruction evidence

The current accepted body omitted eight explicit NULL stores after the successful SFX sample assignments. Historical source view (`python tools/function_lines.py game-main init_game --source-view 1965 1974`) maps original lines 1965–1971 to seven 10-byte `movl $0, <symbol>` instructions:

- `jump_sound[0]`, `[1]`, `[2]` at original offsets 5165, 5175, 5185;
- `sounds[0]`, `[1]`, `[3]`, `[5]` at offsets 5195, 5205, 5215, 5225;
- after `unload_datafile(sfx)`, original line 1974 stores zero to `sfx` at offsets 5260–5270.

These are independently named symbol targets in the disassembly and correspond to pointer-typed arrays / `DATAFILE *`. The retained candidate puts the seven sound-slot resets after sample extraction, then clears `sfx` immediately after unload, matching the original statement order and control-flow region.

Other source/CFG discrepancies were repaired in the same isolated candidate:

- Loader failure: original line 1679 calls `log2file` with `" *** failed"` before text mode and the fatal message (`--source-view 1677 1682`). The current body omitted that call.
- Failed guest-profile load: original line 1890 logs `" profile not found '%s'` with `"guest"` before `create_profile` (`--source-view 1882 1893`). The current body omitted that call.
- Display switch mode: the historical line table has separate calls at 1723 and 1726, passing `SWITCH_BACKAMNESIA` and `SWITCH_BACKGROUND`; the current ternary expression emitted one call. The candidate restores the two branch-specific call sites.
- Graphics-mode fallback: the historical CFG has one fullscreen `set_gfx_mode` call site at line 1639, reached both from initial fullscreen selection and from the failed-windowed branch after `options.full_screen=-1`. The current body duplicated the fullscreen call and its fatal error block. The candidate keeps the windowed attempt in `if (!options.full_screen)` and routes both fullscreen cases through the shared `if (options.full_screen)` block.

The retained previous negatives were reviewed first: parser-local lifetime and register-allocation scope probes leave the +14 mismatch; earlier complete-body/compiler-context variants converge; the old undefined `checkFile` probe is invalid and was not reused.

## Fresh current-order full-TU result

Canonical body-overlay probe `init-game-historical-reset-blocks-body-overlay-20260924` used current source order, no generated prototypes, and the locked compiler. It compiled successfully:

- `init_game`: `DIFFER`, 5780/5788 bytes, first mismatch +14. The restored source-backed structures gain 92 bytes from the 5688-byte accepted body, leaving an 8-byte deficit. The residual first mismatch is the historical parameter-register allocation, not the omitted SFX block.
- Exact functions: 63/82 before and after; no gains, losses, or new implicit declarations.
- `check_dir`: remains `FUNCTION_MATCH`, 103/103 bytes, correct resolved target. Its raw call displacement changes with the expanded preceding body; effective target identity remains exact.
- `new_game` and `run_demo`: remain `FUNCTION_MATCH`, 1139 and 159 bytes.
- Effective `init_game` identity: `2ac0d9b4accb7066`; response summary reports 5310 differing bytes and 419/419 unequal relocations, so this is not an exact body.

Strict receipt: `docs/attempts/tu-context/game-main/init-game-historical-reset-blocks-body-overlay-20260924.json`. Detailed comparison: `build/tu-context/game-main/init-game-historical-reset-blocks-body-overlay-20260924/comparison.json`.

The exact-peer fingerprint is `f64f63d89cb0603f6e8f211aad4c0e59461745e96f0aaf67a4005fd8cc0cb72c`, computed as SHA-256 over sorted `FUNCTION_MATCH` peers with candidate sizes, relocation-masked candidate instruction bytes, and relocation offset/symbol/addend/resolution tuples. It covers all 63 peers; specifically, `check_dir`, `new_game`, and `run_demo` are exact.

## Files for serialized follow-up

- Single-function retained candidate: `init_game.c`.
- Ready raw transaction spec: `init-game-historical-reset-blocks.tu-context.json` (current order, no prototypes, body bound to the candidate above).
- Full-TU candidate: `main-reset.c`.
- `main.c` preserves the earlier partial probe's `research_base` bytes; its size and SHA-256 match the retained receipt. The earlier partial outcome remains 5708/5788 and is not overwritten.

No production body edit, generated card edit, recovery-ledger edit, or promotion occurred.
