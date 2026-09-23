# `calc_replay_checksum` operand-order follow-up (2026-09-24)

## Scope and state

Research-only complete-TU overlays built from the owner-aligned replay source `docs/attempts/research-20260923-replay-pretable-owner/property-case-order-source.c`, whose control has eight exact functions. The locked TDM-2 GCC 4.4.1 `-O2 -mfpmath=387` command and strict `experiment.compare` report path were used. No maintained source, generated current state, recovery ledger, or accepted body was edited.

The probe base uses the already-established source-supported first accumulator form `(biggest_lost_combo * 17 + 17) + no_combo_top_floor * 127` from `grouped-a-first.c`; this follow-up does not repeat its prior scale/order experiments. The new batch reverses one source operand pair at a time in later addends, guided by the original instruction stream, then tests one combined reverse-all form.

## Historical evidence

The original PE function is 676 bytes at `0x41bac4`. DWARF identifies `Treplay *r`, signed `int i` (declared line 127), unsigned `int sum` (line 128), and an inlined `hash(sum)` body at line 166. No other locals are present. The candidate declaration and locals agree. The recovered `Treplay` and `Trecord` headers preserve their historical sizes, field offsets, and field types; relevant arrays include `tc_c_data`, `tc_q_data`, and `tc_t_data` as `float[100]`, `data` at offset 2216, and `Trecord.key_flags`/`cycle_count` at offsets 0/4.

The checksum has no external data or literal owners, no relocations, and no direct call instructions; `hash` is inlined in the historical bytes and candidate. Its source callers are `get_replay_property` and `save_replay`. Thus this mismatch is local arithmetic/code generation, with no unresolved data or callee ownership to explain it.

Original scalar field processing establishes these machine-order pairs: `floor_shrink` then `floor_size`; `start_speed` then `speed_increase`; `gravity` then `random_seed`; `tc_posts` then `rejump`; and in the five-element loop, `ccc[i]` then `jc[i]`. The current source expression order agrees with those pairs, but the GCC candidate schedules the right-hand term first for these commutative additions. The 100-entry float loop, 32-byte date/name loop, 42-byte comment loop, and replay-data loop are represented as expected by the historical CFG and recovered field types. Original branch count is six.

## Batched outcomes

The 8/15 owner-aligned control retained these eight `FUNCTION_MATCH` functions in every overlay: `create_replay`, `destroy_replay`, `get_replay_property`, `get_sort_method`, `hash`, `save_replay`, `set_sort_method`, and `update_file_list`. No probe gained or lost an exact neighbor.

| Variant | Candidate size | Fixed-offset differing positions | First mismatch |
|---|---:|---:|---:|
| Control, prior grouped-a-first accumulator | 675 | 601 | 21 |
| Swap `floor_shrink`/`floor_size` | 675 | 597 | 21 |
| Swap `start_speed`/`speed_increase` | 675 | 615 | 21 |
| Swap `gravity`/`random_seed` | 675 | 601 | 21 |
| Swap `tc_posts`/`rejump` | 671 | 333 | 21 |
| Swap `ccc`/`jc` terms | 675 | 601 | 21 |
| Reverse all five pairs | 675 | 594 | 21 |

The seven target instruction streams have seven distinct SHA-256 identities in `owner-context-results.json`; no duplicate outcomes were discarded. The `tc_posts`/`rejump` swap creates the only large improvement: it removes four candidate bytes and cuts fixed-offset differences by 268. It remains strict `DIFFER` (671 vs 676), and the first mismatch remains at offset 21. Reversing all pairs is worse than that isolated result, so the improvement is local to the individual source expression interaction; it does not justify further broad operand shuffling.

## Artifacts and handoff

- Source variants and summaries: `docs/attempts/research-20260924-checksum-full-context/`.
- Strict per-variant CU comparisons and object/DWARF artifacts: `build/tu-context/game-replay/luna-checksum-fullctx-<variant>-20260924/`.
- Owner-aligned baseline source and its prior provenance: `docs/attempts/research-20260923-replay-pretable-owner/README.md`.
- Current focused evidence remains `docs/current/functions/replay/calc_replay_checksum.json` and `docs/current/function-evidence/replay/calc_replay_checksum.json`.

The source-order batch found a new diagnostic lead but no strict match. The exact `tc_posts`/`rejump` instruction and CFG interpretation is recorded in [`postswap-instruction-analysis.md`](postswap-instruction-analysis.md). The remaining broad arithmetic/register differences, including the offset-21 first mismatch, are unresolved. Do not promote these overlays or edit maintained state from this result alone.
