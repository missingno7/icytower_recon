# Collision original follow-up (2026-09-24)

Scope: isolated `game-main` full-TU probes using locked TDM-2, `--order historical`, and `--no-prototypes`. Maintained `src/`, generated cards, and `src/recovery.json` were not changed.

## Concrete source finding

The maintained body uses `play_sound(combo_sound[0],1,1)`, but historical code loads `DWORD PTR [0x4dd300]` at `0x407f9c` immediately before the call. Historical DWARF records `sounds` as `SAMPLE *[9]` at `0x4dd2e0`; `sounds[8]` is exactly `0x4dd300`. `combo_sound` is a different array at `0x4dd280`. This supports `sounds[8]` as the historical expression and makes the current sound-handle expression a concrete source discrepancy. The exact original parameters remain `int lastX, int lastY` and the only local DIEs are `solid1`, `solid2` (both declared at historical line 3293); candidate interface is `AGREE`. `play` passes `(midX,lastY)`, while the callee does not use either parameter. The historical/candidate direct callee sets both remain `{is_solid, play_sound}`; there is no inlining into or from this function.

## Probes and outcomes

- Control receipt: `docs/attempts/tu-context/game-main/research-collision-original-historical-control-20260924.json`; object/comparison/DWARF: `build/tu-context/game-main/research-collision-original-historical-control-20260924/`.
- Sound-expression overlay: `docs/attempts/research-20260924-collision-original/sounds-eight.c`; receipt: `docs/attempts/tu-context/game-main/research-collision-original-sounds-eight-20260924.json`; object/comparison/DWARF: `build/tu-context/game-main/research-collision-original-sounds-eight-20260924/`.
- Both compile 63/82 exact main functions, retain `new_game` (1139 B) and `run_demo` (159 B) as `FUNCTION_MATCH`, preserve historical predecessor position 79/82, and produce no gains or losses. Target remains `DIFFER`, 449 vs 456 bytes, first mismatch offset 205.
- `effective_outcomes.py` groups the control and existing zero-guard variants at `aeae676cbe028084` (154 differing fixed byte positions); the `sounds[8]` source yields a new output `128ed0e2d4e76fcc` (153 positions). The earliest mismatch and the live register reversal remain: history loads `ply[player_id]` into `%eax`, then `status` into `%edx`; candidate loads the table entry into `%edx`, then `status` into `%eax`. Thus the sound expression is a proven source correction/new compiler outcome, but does not explain or resolve the offset-205 allocator difference.

## Stop point

Prototypes and parameter types agree; local declaration order/types agree with DWARF; actual caller arguments are ordinary two-int cdecl arguments and are unused; full historical-order TU gives the same focus result; body has no additional locals in DWARF; direct call graph is unchanged. The remaining offset-205 allocation cause has no newly supported declaration/ABI explanation. Further guard cosmetics are already deduplicated and would have low information gain. Do not promote the probe or change maintained source without a separate source-recovery transaction.
