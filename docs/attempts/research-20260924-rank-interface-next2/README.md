# `set_next_rank_message` interface prerequisite for `view_profile`

Research only, from current HEAD `22423901`. No maintained source, generated current state, or recovery ledger was edited.

## Decision

This interface prerequisite does not change the next `view_profile` recovery decision. A whole-TU control that removed only the caller's explicit `(Tprofile_rank *)` cast compiled with the same `view_profile` instruction stream, strict status, first mismatch, and exact profile peer count as the current source. The callee's nominal type mismatch is real and the interface task remains `TYPE_LAYOUT_BLOCKED`, but that mismatch is not the cause of `view_profile`'s current instruction mismatch.

## Prediction and discriminating experiment

Before compiling, predicted that removing the cast would leave code unchanged: both operands are 32-bit pointers under the locked i386 ABI; the callee declaration, definition, body and historical order are unchanged. If the instruction stream differed, it would show that GCC's type view at this call has a codegen effect and justify tracing its first divergence. A compile failure, strict peer loss, or instruction delta would likewise change the next decision.

The isolated source copy changes only:

```c
set_next_rank_message(nextRankMessage, (Tprofile_rank *)profile);
```

to:

```c
set_next_rank_message(nextRankMessage, profile);
```

It retains the whole authentic profile translation unit, current definition order, `-O2`, locked TDM-2, and no added prototype block. GCC accepts the incompatible-aggregate pointer conversion with its existing diagnostics policy.

## Outcome

- Baseline and control both compile.
- `view_profile`: `DIFFER`, 2168 candidate bytes / 2249 historical bytes, first historical mismatch `+115`, 1625 differing byte positions and 72 relocations in each comparison.
- Mechanical comparison of the complete per-instruction candidate arrays gives equality; their SHA-256 is recorded in `experiment-summary.json`.
- Profile strict function count remains 11 before/after; zero gains, zero losses. Whole `.text` remains unequal.
- The current caller's only direct edge to `set_next_rank_message` is at the call represented by source line 656. The removed cast changes neither emitted instructions nor the caller's strict peer set.
- The focused `view_profile` card places that direct edge at object offset +712, while the first historical mismatch is +115; the current mismatch occurs well before the call site.

The current card identifies `set_next_rank_message` as `FUNCTION_MATCH`, 431/431 bytes, while the interface card records the actual type conflict: original DWARF parameter 2 is full `Tprofile *` (1360 bytes); current definition/prototypes use `Tprofile_rank *` (140 bytes), with 37 aggregate member differences. `view_profile` itself is already declared and defined as `int view_profile(Tprofile *)`. Thus the caller owns the historical type, and the callee's partial rank view is isolated behind an ABI-compatible pointer cast.

## Why no admissible type repair emerged

Prior isolated variants changing the callee declaration/definition to `Tprofile *` and casting field accesses to the partial rank view preserved the 431-byte body and 11 exact profile functions, but changed the protected `FUNCTION_MATCH` source island. They therefore do not satisfy the interface task's safe edit scope. A prototype-only type change fails compilation because the definition still has the incompatible `Tprofile_rank *` type. Making the definition use historical `Tprofile *` requires rewriting or aliasing its protected rank-only member accesses. No DWARF evidence supports treating the 140-byte subset as the historical 1360-byte aggregate.

## Artifacts

- `baseline.c` and `view_profile_call_without_rank_cast.c`: full source overlays.
- `experiment-summary.json`: prediction, source hashes, strict result and effective instruction identity.
- `baseline-receipt.json`, `call-control-receipt.json`: whole-TU probe receipts.
- Prior protected-body/type-view experiments: `../research-20260924-profile-rank-type-view/findings.md` and its candidate sources.
- Current source and oracle records: `src/profile.c`, `docs/current/interfaces/set_next_rank_message.json`, `docs/current/functions/profile/set_next_rank_message.json`, `docs/current/functions/profile/view_profile.json`.

## Next discriminator

No source-spelling or cast experiment is justified. Reopen the interface task only if independent historical source/type evidence can establish a type identity that both exposes the rank accesses and corresponds to the original full `Tprofile` DIE, or if the protected body becomes legitimately editable after the strict body status changes. For `view_profile`, continue from the already established `+115` inline draw CFG/layout residue and the two unresolved `.rdata` relocation owners; this interface result adds no recovery evidence.
