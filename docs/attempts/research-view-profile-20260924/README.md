# `view_profile` investigation (2026-09-24)

Research only. No maintained source, generated status, or production ledger was edited. Every compiler result below came from an isolated full-TU overlay built with locked TDM-2 at `-O2`, current definition order, and no added prototype block. The strict comparison checked all profile functions.

## Baseline and current prerequisite

The current function card is `DIFFER` / `SOURCE_DIFFER`, 2160 candidate bytes vs 2249 original, first mismatch at function offset `+62`. Current source has `while (is_any(get_controls())) poll_control(...)`.

The supervisor queue blocks body work on two interface tasks: `view_profile` (`TYPE_EVIDENCE_INCOMPLETE`) and `set_next_rank_message` (`TYPE_LAYOUT_CONFLICT`). Original DWARF records `int view_profile(Tprofile *)`; current declarations/definition use `void view_profile(void *)`. The profile header describes canonical `Tprofile` as 1360 bytes, but the task's declaration audit still reports it unavailable/ambiguous in affected CUs. `set_next_rank_message` currently uses a 140-byte `Tprofile_rank` view where the original parameter is full 1360-byte `Tprofile`; that partial alias lacks canonical correspondence for the referenced `score` field. Neither prerequisite was changed.

## Supported missing condition

The original entry disassembly performs `is_any(get_controls())` and then reads byte address `0x5069d3`; both branches loop to the `poll_control` body. Allegro's original `key` array is at `0x506988`, `KEY_SPACE` is 75, and `0x506988 + 75 == 0x5069d3`. The declaration is `volatile char key[]`. Candidate relocation `_key + 75` resolves independently to the same original address. This supports the original condition `is_any(get_controls()) || key[KEY_SPACE]` and explains the original `mov al,[0x5069d3]` byte load.

The isolated probe for that condition changed the candidate from 2160 to 2168 bytes, moved the first mismatch from `+62` to `+115`, and preserved all 11 exact profile neighbors (0 gains, 0 losses). The strict target remains `DIFFER`; the first remaining mismatch is the conditional branch at `+115` (`original 0f84d9070000` vs candidate `0f848e070000`), whose destinations are at original `+0x850` and candidate `+0x805`. This is a later function-layout/CFG difference, not a remaining mismatch in the key relocation.

A separate `&& !closeButtonClicked` probe and a `|| closeButtonClicked` probe were negative controls. The first diverged at `+21`; the second still diverged at `+62` because it reads a different global/type. All probes retained 11 exact neighbors. Their distinct effective outputs are recorded in the batch receipts.

## Artifacts and strict outcomes

- `batch-manifest.json`: baseline vs incorrectly ordered close-button guard; `key-batch-manifest.json`: baseline vs supported key-space guard; `or-batch-manifest.json`: baseline vs close-button OR negative control.
- `key-space-or.c`: retained body overlay for the source-supported condition.
- Receipts: `docs/attempts/tu-context/game-profile/vp-20260924-key-control.json` and `.../vp-20260924-keyspace.json`.
- Strict full-TU report: `build/tu-context/game-profile/vp-20260924-keyspace/comparison.json`.
- Exact recorded status: key-space overlay `DIFFER`, 2168/2249, first `+115`, 11/17 exact functions unchanged, no neighbor regressions, whole `.text` unequal.

## Successor trace for `+115`

The `+115` instruction is the `draw_sprite(bg, screen, 0, 0)` inline `color_depth == 8` branch, not a different source-level condition. Original line-table evidence maps the inlined body to Allegro `draw.inl:238` at `0x419b57` (call site `profile.c:549`). The branch at `0x419b5d` goes to function offset `+0x850`; the ordinary path dispatches through vtable slot `0x44` and rejoins at `+0x9a` (`0x419b86`).

The key-space overlay's DWARF maps the equivalent inline body to `draw.inl:238` at object offset `0x1167` (call site `profile.c:630`). Its branch at `0x116d` goes to function offset `+0x805`; the ordinary path uses the same vtable slot `0x44` and rejoins at `+0x9a` (`0x1196`). The original slow successor at `+0x850` and candidate slow successor at `+0x805` both stage zero x/y, source `screen`/source bitmap, dispatch through vtable slot `0x48`, then jump to the same relative join `+0x9a`. Original and candidate therefore express the same two CFG successors and inline Allegro operation. The encoded conditional differs because that slow block has a different physical offset in the two whole-function layouts; this trace does not identify a missing source operation and does not justify a probe.

The data/call evidence is consistent: original normal dispatch calls `*0x44(%edx)` and slow dispatch calls `*0x48(%edx)`; candidate has the same slots. The original normal-path source is the `screen` bitmap (`0x4dda8c`); candidate uses the corresponding `_screen` relocation. This branch is an inlined library layout difference, not evidence for another predicate change. No candidate was compiled for this trace; the key-space result and 11 exact peers remain as recorded above. The two `.rdata` relocations at `+1222` and `+1625` and the interface prerequisites remain unresolved.
