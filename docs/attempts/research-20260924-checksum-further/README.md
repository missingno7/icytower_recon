# `calc_replay_checksum` later-loop allocation discriminator

## Frozen question and prediction (before compiling)

Question: can changing only the source evaluation order of the two terms in the final replay-data loop alter GCC 4.4.1 IRA's initial accumulator register selection at function offset +21? The current-context strict first byte mismatch is +19 (the shift immediate); +21 identifies the register-destination instruction, not the first oracle mismatch.

Historical code keeps the first accumulator in ECX (`lea 0x11(%edx,%eax),%ecx`); current candidate allocation chooses EDX. Prior evidence placed this decision at candidate pass `172r.ira`, before later source-order changes in earlier scalar expressions affected it. This probe tests a distinct, later loop under the *current complete replay.c translation unit*.

Prediction: if later-loop operand order changes whole-function register pressure sufficiently to affect the first accumulator assignment, the variant may choose ECX and remove the register-destination mismatch at +21. The earlier +19 shift mismatch can remain either way. If not, it will keep EDX. In either case, all current exact neighboring functions must remain exact; no result is recovery credit unless the strict function oracle reports equality.

## Isolated inputs

- Baseline is a byte-for-byte copy of current `src/replay.c`.
- Variant changes only `r->data[i].key_flags * 3 * (i % 193 + 1) + r->data[i].cycle_count * 7 * (i % 167 + 1)` to the reversed term order.
- Both are complete TUs compiled in historical definition order with locked TDM-2, no new prototypes, and native strict comparison.
- Artifacts/receipts will be appended after the predictions are frozen.

## Results (locked GCC 4.4.1, historical full-TU order)

Both probes compiled the complete retained current `replay.c` TU with no prototypes added and strict comparison. The baseline reproduced the expected current-context state: 7/15 exact functions; `calc_replay_checksum` is 675/676 bytes, first mismatch `+19` (the shift immediate; the register-destination mismatch is at `+21`), 631 differing byte positions, frame `0x2c`, six branches, and no relocations. Exact neighbors were `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, `load_replay`, and `get_replay_property`.

The one-term-order variant is a distinct effective output. It remains `DIFFER`, now 680/676 bytes with first mismatch still `+19` and 636 differing byte positions. The register-destination mismatch at `+21` also remains. The first accumulator sequence is unchanged: `mov 0x60(%ebx),%eax; mov %eax,%edx; shl $5,%edx; lea (%edx,%eax,2),%edx`. Thus the reversed later loop did not move the initial allocation from EDX to historical ECX. All seven exact peers remain exact; no gains/losses occurred. The variant reports raw offset changes for `load_replay` and `save_replay`, but the strict function matches remain preserved. Whole text remains unequal.

| Probe | Source SHA-256 | Object SHA-256 | Checksum outcome |
|---|---|---|---|
| `checksum-further-control-20260924` | `a3ab23ce1f43d91c7f9e46d15e1f565576af5cc001be4cca1e74f104ac6f32b5` | `18a92252720b44f13a70227bd2e36994fa3d83bc30e515943a09ce1af12ff924` | 675 bytes, `+19`, 631 differences |
| `checksum-further-reverse-final-data-20260924` | `5b7f98fd31e8699f3deea74471a11beeb6d9681008216354007c3e70960cffc` | `98afe89a60947fb74aca986467161bb23715cdbad231ff1cd56d9a2e566fc385` | 680 bytes, `+19`, 636 differences |

The source files differ only in the final loop's two additive terms. Effective instruction/relocation comparison groups them into two identities (`6cf09815902f772b` baseline, `4a554e4bb653fe17` variant). The control and variant receipts are in `docs/attempts/tu-context/game-replay/`; complete strict reports and objects are in `build/tu-context/game-replay/checksum-further-{control-20260924,reverse-final-data-20260924}/`.

## Decision

This experiment rules out the tested later-loop operand order as a cause of the first accumulator's EDX/ECX choice. It does not change the next recovery decision: stop local operand-order perturbations for this function. A future continuation needs source/DWARF/pass/context evidence that predicts a different first-accumulator allocation; another source spelling without such evidence would not discriminate the blocker. This diagnostic earns no recovery credit.


## Offset note

The initial precompile wording conflated the `+21` register-destination instruction with the strict first byte mismatch. The current-context baseline card and fresh strict receipt both place the first mismatch at `+19` (the shift immediate). The experiment's causal prediction concerned whether the destination at `+21` changes; that destination remains EDX in the variant. The report above has been corrected to keep these two observations distinct.
