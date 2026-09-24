# Replay selector single movement-call discrimination

## Question and prediction (recorded before compiling)

The retained cumulative `caller-call-count-candidate.c` preserves the folder-picker event/order correction and restores the source-backed controller-wait and delete-select sound sites. The previous locked output had one extra `play_menu_move` call instruction (candidate 2, target 1). One shared-label `goto` source form had already collapsed to the folder-event output.

`movement-flag-after-switch.c` retains both UP/DOWN state-update branches, sets a per-iteration flag only on successful movement, and issues one lexical `play_menu_move()` after the key switch. Prediction: if the compiler preserves that common call site, emitted move-call multiplicity should drop to one; a collapsed output, two emitted calls, or no target-residue change closes this local call-placement hypothesis.

## Reproduction and result

Two fresh whole-TU overlays compiled against current `src/replay.c`, with current/native emission order, no generated prototypes, and locked TDM-2/GCC 4.4.1 `-O2`:

- Baseline receipt: `docs/attempts/tu-context/game-replay/replay-selector-next2-control-20260924.json`.
- Flag candidate receipt: `docs/attempts/tu-context/game-replay/replay-selector-next2-movement-flag-after-switch-20260924.json`.

The exact CU peers are identical in both receipts: `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, `load_replay`, and `get_replay_property` (7/15, no gain/loss). Both use the same 15-function historical emission order and keep `replay_selector` at position 10. Source identity for `src/replay.c` is SHA-256 `a3ab23ce1f43d91c7f9e46d15e1f565576af5cc001be4cca1e74f104ac6f32b5`.

`effective_outcomes.py` identifies two effective outputs:

| Variant | Effective identity | Bytes | First mismatch | Frame | Branches* | Calls | Exact peers |
|---|---|---:|---:|---:|---:|---:|---:|
| Cumulative baseline | `a68b09981dc86ce7` | 2791/2845 | +8 | 0x27c | 75 | 60 | 7/15 |
| Movement flag | `e12391350f863e6e` | 2795/2845 | +8 | 0x27c | 75 | 60 | 7/15 |
| Historical target | — | 2845 | — | 0x46c | 67 | 59 | — |

`*` The report's branch total counts all `j*` transfers, including unconditional jumps.

Target and candidate disassembly confirm the key prediction failed: original has one `play_menu_move` call at function offset `+0x70d`; the flag candidate has two `_play_menu_move` call relocations, as does the baseline. GCC has one source/cgraph call edge for the flag form but emits it into two call instructions along its optimized control flow. The candidate is a distinct effective output, with 38 fewer differing bytes and one fewer unequal relocation, but the first mismatch remains +8 and no exact peer changes. The emitted call total remains 60 versus 59 historical.

## Decision

This experiment does **not** change the next recovery decision. It establishes that one lexical post-switch call is not sufficient to reproduce the historical single emitted movement call under this context. The local call-placement/spelling branch is closed; the extra emitted call is a CFG/code-generation residue, not a source-call-count issue. Do not promote or count recovery. A future movement investigation needs a specific original-versus-candidate CFG discriminator before another edit; otherwise work another mismatch front.

## Artifacts

- Candidate source: `docs/attempts/research-20260924-replay-selector-next2/movement-flag-after-switch.c` (SHA-256 `fefaa4161a4a530c3913f966e2cb3f03ceaa284c0d8a978fe7a2a33ef1a66903`).
- Baseline body: `docs/attempts/research-20260924-replay-selector-cfg/caller-call-count-candidate.c` (SHA-256 `f5421c77965c1ef75a7aa5331c54cead933435d935db3be899a75eae429d8d1a`).
- Strict comparisons and compiler outputs: `build/tu-context/game-replay/replay-selector-next2-control-20260924/` and `build/tu-context/game-replay/replay-selector-next2-movement-flag-after-switch-20260924/`.
- Effective-output grouping: `python tools/effective_outcomes.py game-replay replay_selector --pattern 'replay-selector-next2-*.json' --response --baseline replay-selector-next2-control-20260924`.

No maintained source, recovery ledger, or generated current state was changed.
