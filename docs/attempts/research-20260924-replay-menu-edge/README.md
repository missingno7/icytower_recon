# do_replay_menu edge and register investigation (2026-09-24)

## Scope

Read-only analysis of the source at HEAD `ca7c5e4e`. The whole `game-main` TU was compiled with locked TDM-2/GCC 4.4.1 at `-O2`, historical definition order, and no generated prototypes. Probe bodies and receipts are retained here; maintained source, generated current state, and recovery ledger were not edited.

## Call-edge reconciliation

The historical call inventory shows `call 0x4b2a3c <___chkstk>` at `0x410fa3`. The candidate call inventory records `___chkstk` at function offset `+12`, independently resolved to the same target VA `0x4b2a3c`. The reported missing historical `ext_4b2a3c` edge is therefore an alias/name normalization discrepancy. Both outputs call the stack probe.

The source-level edge report also lists `memset` because this body asks to fill `fname`, `pname`, and `comment` with 511 spaces. Historical evidence maps those fills to inline `rep stos`; the candidate machine-call inventory has no `memset` call either. That extra edge is not an emitted call difference.

## Register and lifetime evidence

At `+396`, the historical code loads `isGuest` from `-0x1820(%ebp)` into `%edx` (`8b 95 e0 e7 ff ff`); the candidate loads the same slot into `%edi` (`8b bd e0 e7 ff ff`). Both test that register and branch to `+0x7f8`; the selected register is consumed by that test. DWARF locates `isGuest` in the same stack slot, EBP-6176, on both sides. The differing register is a short-lived branch temporary, while the source local retains the same location.

Two semantics-preserving lifetime probes changed only the duplicate `status` initialization around save-buffer setup: one delayed the assignment until after buffer setup, and the other retained only the block-entry assignment. They both produced the existing object SHA-256 `f31e3b157cd91767c2a2a9a940ed5fd7286e0aa6870357fae75d7ab3b5a0e45e`; effective emission identity `af771be203e85051` deduplicates them. Neither changes the `%edi` selection. The status lifetime distinction does not explain the register choice.

## Whole-TU result

Each probe compiled successfully and retained all 64 exact functions out of 82, with no gains or losses, and 79/82 historical predecessor identities. `do_replay_menu` remains `DIFFER`, 2,657 candidate bytes vs 2,661 historical bytes, first mismatch `+397`, 882 differing bytes. No function, object, or CU match is claimed.

## Reproduction

```powershell
python tools/tu_context_probe.py game-main src/main.c replay-menu-edge-delayed-status-20260924 --order historical --no-prototypes --focus do_replay_menu --body do_replay_menu=docs/attempts/research-20260924-replay-menu-edge/delayed-status-init.c
python tools/tu_context_probe.py game-main src/main.c replay-menu-edge-single-status-20260924 --order historical --no-prototypes --focus do_replay_menu --body do_replay_menu=docs/attempts/research-20260924-replay-menu-edge/single-status-init.c
python tools/effective_outcomes.py game-main do_replay_menu --pattern 'replay-menu-edge-*-20260924.json' --compact --response
```

Inputs are `control.c`, `delayed-status-init.c`, and `single-status-init.c`. Full TU receipts are copied into `receipts/`; compiler comparisons remain under `build/tu-context/game-main/`. Prior fill and call evidence is summarized in `docs/attempts/research-20260924-do-replay-menu-save-init/README.md`, and stack-probe alias provenance is in `evidence/research/notes/library_boundary.md`.
