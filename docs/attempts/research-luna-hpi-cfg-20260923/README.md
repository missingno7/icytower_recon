# `handle_player_input` exact-size mismatch replay (2026-09-23)

## Diagnosis

The focused card reports `DIFFER`, exactly 728 candidate bytes vs 728 historical, 50 differing bytes, with the first mismatch at function offset `+475`. It is not a relocation-owner failure. The two relocation-table entries at candidate `+480` (`_demo`) and `+492` (`_rec_pos`) are explicitly `UNALIGNED_BYTE_WINDOW`: they do not align to original instruction operands at those offsets, so the fixed-byte values cannot establish an owner mismatch. The two direct `play_jump_sound` transfers resolve to the same historical target. Original and candidate each report 185 instructions, 30 conditional/unconditional branches, and the same 11 direct calls.

The first real divergence is source evaluation/lifetime ordering within the replay-record update. Historical code at `+473` tests the stored key-flags high bit; the set-bit branch writes the two marker records and jumps out of the recording update. The input flags are extracted only after that test on the non-marker path (historical line 2420 after line 2418). The current source extracts `control->flags & 0x93` before testing the high bit. The candidate therefore starts the region at `+475` with the flags load, while the historical code begins by reading the record's `key_flags`. Moving the flags computation into the high-bit test's `else` is historically evidenced by the CFG and the `flags` DIE: that local is nested in a lexical block whose original live ranges begin after the branch, not at function scope.

Thus the immediate code difference is the placement/lifetime of a pure flags computation relative to the record marker branch. It changes instruction order and GCC register scheduling without changing total size or the number of branches/calls. The saved card and original line/branch evidence support this finding; equal sizes do not make it a layout-only match.

## Current-order no-prototype probes

All used isolated complete-function overlays with `--order current --no-prototypes`. The production-equivalent control preserved **63/82** exact functions.

| Variant | Target output | Exact functions | Dedup/result |
|---|---:|---:|---|
| Current body control | 728 B, first mismatch +475 | 63/82 | Baseline output identity `9cfad1b8…` |
| Move flags computation into the non-marker `else` | 760 B, first mismatch +3 | 61/82 | New output identity `a4e3f196…`; loses `show_instructions` and `stopGameMusic` exact matches |
| Also scope flags to the non-dead recording branch, preserving the early assignment | 728 B, first mismatch +475 | 63/82 | Same output as control; scope-only change eliminated |
| Scope flags and compute it inside the non-marker `else` | 760 B, first mismatch +3 | 61/82 | Same output as the preceding moved-assignment variant |

The CFG-backed placement variant is not a safe candidate: it grows the target by 32 bytes, changes the prologue/register set, and loses two exact neighbors. Its scoped spelling is byte-for-byte/effective-output equivalent, so further syntax variations of that same branch form are not informative. The source-backed scope-only probe does preserve every exact neighbor but collapses to the production control. No strict candidate was found; stop here rather than retrying cosmetic spellings.

## Artifacts

- Focused card: `docs/current/functions/main/handle_player_input.json`
- Full original evidence (instruction alignment, DWARF ranges, branch windows, calls and relocations): `docs/current/function-evidence/main/handle_player_input.json`
- Earlier historical-order and source-flow experiments: `docs/attempts/game-main/handle_player_input-finding.md`
- Isolated sources: `probes/current-control.c`, `probes/flags-scoped-to-live-recording-branch.c`, `probes/flags-computed-only-in-keyflag-else.c`, `probes/flags-declared-and-computed-in-else.c`
- Current-order receipts: `docs/attempts/tu-context/game-main/luna-hpi-current-control-20260923.json`, `luna-hpi-flags-scoped-recording-branch-20260923.json`, `luna-hpi-flags-moved-else-20260923.json`, `luna-hpi-flags-scoped-else-20260923.json`
- Full TU comparisons and objects: `build/tu-context/game-main/luna-hpi-*/`

No maintained source, current card, ledger, or recovery file was edited.
