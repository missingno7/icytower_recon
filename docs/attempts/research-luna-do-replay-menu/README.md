# Luna isolated research: `do_replay_menu` (2026-09-23)

## Strict status

No strict win. All six current-order `tu_context_probe` trials report `do_replay_menu: DIFFER`; every probe retained 63/82 exact main-TU functions with no gains or losses. The initial production-equivalent control is `luna-do-replay-menu-baseline-20260923`: 2,643/2,661 bytes, first mismatch at +8 because the candidate frame is `0x145c` versus the original `0x185c`.

## Material mechanisms and facts

1. The focused DWARF card proves two distinct lexical `lastGameFile[2048]` locals, in separate paths. The candidate had one function-scope array. Giving the replay-view branch and save-status-3 block separate arrays, and moving save-only arrays plus `status`/`action`/`thisChecksum` into their evidenced scopes, changes the compiled frame from `0x145c` to the original `0x185c`. The candidate then has the historical prologue and first raw byte difference moves from +8 to +194 (`luna-do-replay-menu-scoped-20260923`, 2,639 bytes). This is a declaration/lifetime correction directly supported by DIE scopes and locations, not a size target.
2. Original code after the “play again” selection stores `play_again=1`, sets the loop result register to `'l'`, then rechecks the loop exit. The retained body omitted `ret='l'`, so it could re-enter the menu. Adding the assignment is directly supported by original instruction `mov $0x6c,%esi` at original offset +0x107. On the scoped candidate this advances the first mismatch to +364 and yields a new effective output, `luna-do-replay-menu-play-again-exit-20260923`, 2,643 bytes. At the newly exposed mismatch, original sets the fill byte before the count (`mov $0x20,%al`, then `mov $0x1ff,%ecx`); candidate reverses those independent setup instructions. Both sides use `rep stos` for the 511-space initialization.
3. `memset` and `__builtin_memset` source spellings collapse to the same effective function object for the scoped candidate. An explicit scalar `for` fill loop yields a new object (2,691 bytes) but emits an increment/compare loop rather than the historical `rep stos`, so that loop family is not promising. Moving the terminating NUL store ahead of the fill changes output but preserves the +364 first mismatch and contradicts the original operation order; it is archived only as a negative trial.
4. The focused rule set already has `decoded-instruction-order-source-experiment` for a window where the same MOV instructions occur in a different order; it cautions that a permutation does not identify its source cause. Here the +364 setup is such a pair. The card also records `main_menu_callback` as the historical and candidate emission predecessor, but `predecessor_exact=false`. A declaration-only overlay retained the same effective `do_replay_menu` output as the corrected candidate. Replacing that predecessor with the separately retained, evidence-backed `main_menu_callback-rank-candidate.c` changed the effective `do_replay_menu` output while keeping its source body fixed and strict status DIFFER. In the resulting code the `isGuest` test value moves from `%edx` to `%ecx`; the +364 AL/ECX fill-setup order remains. This is concrete GCC whole-TU context sensitivity, not proof that the retained predecessor is historically correct or that context explains the fill order. It fits the existing `persistent-peephole-scratch` rule as a lead. `emission_order.py game-main src/main.c do_replay_menu` finds no safe source-order move.
5. Original and corrected candidate disassemblies each contain 43 branch instructions, including 27 conditional branches, and their direct game/library call sets agree apart from compiler-generated/runtime edges. The state-handler branches remain present through the save path; some target offsets and late block ordering differ, so this count is not a CFG proof. Branch and call artifacts are archived locally for follow-up alignment.

## Effective-output summary

`python tools/effective_outcomes.py game-main do_replay_menu --pattern 'luna-do-replay-menu-*.json'` reports 6 probes and 5 effective outcomes:

- `07fee387349d51e9`: original baseline, 2,643 bytes, first +8.
- `3076dc5a5a9890ce`: scoped-locals and scoped-builtin-fill collapse, 2,639 bytes, first +194.
- `7009c3fffe29b31c`: scalar fill loops, 2,691 bytes, first +7.
- `9c5e2914f8b97f6e`: scoped locals + `ret='l'`, 2,643 bytes, first +364.
- `d5489ebd283521f7`: scoped locals + `ret='l'` + terminators-first, 2,643 bytes, first +364.
- `2cfea875896db232`: same corrected target body with retained rank candidate overlaid on predecessor `main_menu_callback`, 2,643 bytes, first +364.

Each receipt records full source/object hashes and whole-TU exact-neighbor counts.

## Remaining blocker and next useful step

Local type/declaration evidence is adequate: the relevant values are signed `int`, arrays are signed `char` with DWARF-proved extents, and the scoped arrays now place the stack frame correctly. The semantic play-again exit is repaired in the isolated candidate. Remaining output is unresolved instruction ordering/register allocation and later code differences; the first exposed mismatch after those repairs is the independent fill-byte/count setup order. Continue by aligning the corrected candidate against original instructions after +364 and checking whether historical predecessor/context state or an independently evidenced source sequence explains that order. Do not promote this candidate as-is.

## Small artifacts

- Candidate bodies: `scoped-locals.c`, `play-again-exit.c`, `scoped-fill-loop.c`, `scoped-builtin-fill.c`, `play-again-terminators-first.c` in this directory.
- Full original/candidate disassemblies and source: `original-disasm.txt`, `candidate-disasm.txt`, `scoped-disasm.txt`, `fill-loop-disasm.txt`, `play-again-exit-disasm.txt`, `terminators-first-disasm.txt`, `menu-context-disasm.txt`; raw decoded branch tables are `orig-branches.txt` and `cand-branches.txt`.
- Focused receipts: `docs/attempts/tu-context/game-main/luna-do-replay-menu-{baseline,scoped,fill-loop,builtin-fill,play-again-exit,terminators-first,menu-context,declarations-context}-20260923.json`.
- Current card: `docs/current/functions/main/do_replay_menu.json`.

