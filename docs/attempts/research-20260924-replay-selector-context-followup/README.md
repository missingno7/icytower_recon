# Replay selector historical-order follow-up

Research-only locked TDM-2 / GCC 4.4.1 `-O2` complete-TU overlay. No maintained source, generated state, or recovery ledger was changed.

## Probe

The existing owner-aligned selector body with two branch-scoped `char p[1024]` buffers and a delete-branch-scoped `char fname[512]` was recompiled using historical definition order and no generated prototypes. This tests whether historical TU context restores the exact CU neighbor lost when the 512-byte `fname` is moved out of function scope. Its source is retained at `docs/attempts/research-20260924-replay-selector-buffer-scopes/luna-replay-selector-pboth-localfname-20260924.c`.

## Result

Compilation succeeded. The overlay retains 6/15 `FUNCTION_MATCH` functions, with no exact-function gains or losses relative to its local-buffer baseline; relative to the owner-aligned 8/15 control it lacks exact `save_replay` and `get_replay_property`. `replay_selector` remains `DIFFER`, 2662 bytes versus 2845, first mismatch at offset 8, with frame allocation `0x47c` versus `0x46c`, and 94/97 unequal or unresolved relocation comparisons. The body has the same source-level CFG/callee additions previously observed (`rectfill`, `set_sort_method`, and the compiler's `__builtin_memcpy`).

`effective_outcomes.py` gives this probe a separate effective hash from the same local-buffer body under current definition order, despite identical size, frame, mismatch, branch/call, and exact-function metrics. Thus definition order changes emitted target bytes but does not improve the strict verdict or neighbor set. This eliminates historical definition order as the fix for that loss. The owner-aligned global-`fname` body still has a retained 8/15 result, but its selector frame is `0x67c` and it remains `DIFFER`.

## Receipt

- Probe receipt: `docs/attempts/tu-context/game-replay/replay-selector-historical-pboth-localfname-20260924.json`
- Full comparison and locked compiler artifacts: `build/tu-context/game-replay/replay-selector-historical-pboth-localfname-20260924/`
- Historical-order local-buffer control: `luna-replay-selector-pboth-localfname-20260924` in `docs/attempts/tu-context/game-replay/`
- Existing owner-aligned pool/argument analysis: `docs/attempts/research-20260923-replay-pretable-owner/README.md`

This is a failed source-context experiment, not a body or layout match claim.
