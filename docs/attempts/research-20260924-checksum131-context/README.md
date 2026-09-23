# `calc_replay_checksum_131` downstream-context probe — 2026-09-24

## Scope and current state

Research-only isolated whole-TU overlays. No maintained source, current generated state, or `src/recovery.json` was edited. Current focused cards remain authoritative:

- `calc_replay_checksum_131`: 177-byte `DIFFER` / `SOURCE_DIFFER`, six differing bytes. Baseline first mismatch offset 144; candidate/historical instruction ordering diverges in the second loop, with a peeled-first-iteration vs backedge load-order conflict.
- `calc_replay_checksum`: 676 historical vs 675 candidate bytes, `UNKNOWN_SUPERVISOR`, 631 differing bytes; baseline first mismatch offset 19. It is emitted immediately after `_131`, which is not exact.

Historical DWARF lists only signed `int i` and signed `int sum` in `_131`; there are no locals/calls/lexical blocks that offer another evidenced storage lever. Current `Trecord` fields are `key_flags` (byte) and `cycle_count` (int). Historical line mapping puts line 110 at the second-loop update site, and line 117 at the loop header/continuation; inspect the focused card for the full line window and branch evidence.

## Prior work reviewed

- Read `docs/current/functions/replay/calc_replay_checksum_131.json` and `calc_replay_checksum.json`, `docs/current/function-evidence/replay/` references from those cards, `docs/attempts/game-replay/calc_replay_checksum_131.jsonl`, and `calc_replay_checksum.jsonl`.
- Read the previous Luna checksum experiments in `docs/attempts/research-20260923-checksum-luna/README.md`, which addressed the *downstream* function's initial accumulator expression and grouped terms. The 11 downstream body probes deduplicate to six effective outcomes; best prefix/grouping still ends on different register selection, with no gains/losses to the six exact neighbors.
- Read recent replay owner research in `docs/attempts/research-20260923-create-replay/README.md`. Its `create_replay` declaration/data ownership issue is separate. No `replay_selector` or replay data-owner artifacts were edited or overlaid here.
- The `_131` ledger has already tried ordinary term swap, reversed term order, preincrement, sum assignment expansion, and additive-term splitting. The recorded block rules out repeating the three bounded FAST spellings as a repair claim.

## Whole-TU test

Used `tools/tu_context_probe.py game-replay src/replay.c ... --body calc_replay_checksum_131=... --no-prototypes --focus calc_replay_checksum_131 --no-dumps`, locked TDM-GCC 4.4.1 at `-O2`, with all other replay functions from current maintained context.

- Control label `luna-checksum131-baseline-20260924` overlays the current `_131` body.
- Hypothesis label `luna-checksum131-reverse-terms-20260924` reverses the two source-supported independent terms in the second-loop sum: `cycle_count * 3 + key_flags * 5`. This is the existing failed trial's distinct codegen form, rerun specifically as a downstream-context experiment; it is not presented as new repair evidence.

Both compile in full TU context and retain 6 strict function matches out of 15; whole text, object, and CU remain unequal. All six strict functions are unchanged across the two receipts. The control `_131` is 177 bytes and differs at offsets 144–150. The reverse-terms candidate remains 177 bytes and yields a distinct effective `_131` sequence, with its first mismatch moving to offset 134 and five differing bytes. No `_131` relocation or direct-transfer differences occur.

For downstream `calc_replay_checksum`, both receipts produce the same 675-byte candidate, same 676-byte historical comparison, same first mismatch at offset 19 and same 631 differing bytes. Candidate decoded instruction records, relocation records, and direct-transfer records are identical between control and reverse-terms probes. Effective-output grouping confirms two `_131` outcomes but one downstream outcome:

```text
python tools.effective_outcomes.py game-replay calc_replay_checksum_131 --pattern 'luna-checksum131-*.json' --compact
python tools.effective_outcomes.py game-replay calc_replay_checksum --pattern 'luna-checksum131-*.json' --compact
```

The effective IDs were `6520f5bf319b5e89` (control) and `fd337f0997aaa570` (reverse terms) for `_131`; both collapsed to `6cf09815902f772b` for `calc_replay_checksum`. This establishes that this real source-level predecessor instruction-order perturbation does not change the downstream candidate code or its local relocation records under the current TU context. It does not prove all possible TU/compiler-context interactions are absent.

## Handoff

The predecessor's historical instruction-order mismatch is independently bounded and has no demonstrated context effect on the downstream checksum. The current downstream blocker therefore remains its own broad arithmetic/register-selection mismatch, not a side effect of this tested `_131` source spelling. No exact candidate or promotion receipt exists.

## Artifacts

- `body-baseline.c`, `body-reverse-terms.c`
- `build/tu-context/game-replay/luna-checksum131-baseline-20260924/comparison.json`
- `build/tu-context/game-replay/luna-checksum131-reverse-terms-20260924/comparison.json`
