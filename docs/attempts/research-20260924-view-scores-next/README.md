# view_scores CFG follow-up (2026-09-24)

## Frozen prediction

The retained combined candidate repairs the line-286 `keypressed()` call and the two exit-key groups. Its two source lines `while (!cycle_count)` test zero only. Historical instructions test `cycle_count` then use signed `jle` at function offsets +876..+884 and +2191..+2198. I predicted `while (cycle_count <= 0)` at both sites should recover those conditional branches, with the unmodified site retaining its zero-only test. The frame should remain 0x4c; all 10 exact peers should remain exact; this branch correction alone would not close the 50-byte body gap.

## Batch and outcomes

All probes compile the authentic full `game-hisc` TU using `tdm-2 -O2`, current definition order, no prototypes, and a complete isolated `view_scores` body overlay. The original candidate is `docs/attempts/research-luna-view-scores-20260924/view-scores-key-call-and-constants.c`.

| Source variant | Effective identity | `view_scores` | Exact peers | Frame | Outcome |
|---|---|---:|---:|---:|---|
| First wait `<= 0` | `b6b4ac9c0b4eb3b3` | 2502/2552, DIFFER | 10/10 | 0x4c | distinct |
| Second wait `<= 0` | `d30cb081204fe579` | 2502/2552, DIFFER | 10/10 | 0x4c | distinct |
| Both waits `<= 0` | `6740d893ed5edaa4` | 2502/2552, DIFFER | 10/10 | 0x4c | distinct |

The object disassemblies confirm each changed source site switches its zero-only branch to signed `jle`; the untouched site retains its zero-only branch. Changing both yields the independently predicted pair. All receipts report no exact-peer gains/losses and no unchanged-body effective-code changes. The combined input therefore fixes the historical condition at both sites, but retains the 16-byte frame deficit, 50-byte extent deficit, and 2316 unequal code bytes. This experiment does not claim recovery credit.

Effective grouping command:

```
python tools/effective_outcomes.py game-hisc view_scores --pattern 'view-scores-*-nonpositive.json' --response --baseline view-scores-first-wait-nonpositive
```

Full receipts are `docs/attempts/tu-context/game-hisc/view-scores-first-wait-nonpositive.json`, `.../view-scores-second-wait-nonpositive.json`, and `.../view-scores-both-waits-nonpositive.json`. Locked objects and RTL/dumps are under matching `build/tu-context/game-hisc/<label>/` directories. The combined candidate to carry forward is `view-scores-both-waits-nonpositive.c` (source SHA-256 `3d7b43875e08b3c7d99a258dcab0d0213fecd6df5c7cad0829f79bb59788f6c0`). The two single-site source hashes are `c0c2da6db2c3ff476c974a0a791e0a98e946969b477c215ed8ebca22a4a477da` and `e4e16a80085b15ba48fabfd8eeb4eaac6d253af37937a050bde1f91eeed082b8` respectively.

## Recovery decision

Yes, this changes the next source-recovery decision: the retained candidate should preserve both historically evidenced `cycle_count <= 0` waits. It does not change the next investigation of the remaining frame/body mismatch. Close the zero-vs-nonpositive predicate question; do not spend more probes on this source family. The frame allocation remains unexplained by these predicate changes, so any follow-up should compare historical and candidate instruction/lifetime evidence around a different concrete mismatch. Keep this branch diagnostic; do not edit maintained source or recovery state from these probes.

The next probe changes only the input-drain predicate from `key[KEY_K]` to `key[KEY_SPACE]` in the retained both-waits candidate. Historical line-table/disassembly evidence at line 183 shows a load from `key[KEY_SPACE]`; the candidate RTL records `key+11` for its `KEY_K` read. Prediction: this operand should move to the historical SPACE address/reference; the load/test/loop shape should remain structurally the same. Frame allocation should remain 0x4c, and all ten exact peers should remain exact. Function extent may shift only from branch/register selection. This tests the apparent key mismatch and does not predict closure of the remaining frame/body gap.

## Second bounded discriminator: input-drain key

The current source-line/operand audit corrected an earlier note: historical line 183 loads `key[KEY_SPACE]` (original address `0x5069d3`), whereas the retained candidate had `key[KEY_K]`. The candidate GCC RTL identifies the latter as `key+11`; changing only this first input-drain operand to `KEY_SPACE` produces `_key+0x4b`, the historical address. This directly resolves the apparent disagreement with the older note that said the entry-drain key already agreed.

Frozen prediction: only the key operand should change, with equivalent test/loop shape, 0x4c frame, and all ten exact peers preserved. The full-TU probe `view-scores-space-drain-key` compiled successfully and preserved 10/10 exact peers with no peer code changes. It is a fourth effective outcome (`bcb78569c1f5e0bd`), still `DIFFER`, 2502/2552 bytes, frame 0x4c, 2316 unequal bytes. The strict function status and frame/body gaps did not change. This is source/operand evidence, not recovery credit.

The corrected candidate to retain is `view-scores-space-drain-key.c`; receipt: `docs/attempts/tu-context/game-hisc/view-scores-space-drain-key.json`; object and disassembly: `build/tu-context/game-hisc/view-scores-space-drain-key/`. Source SHA-256: `a83407acef2fa402a5ff663d0a6be9ce47236dda6a21caf04077af835044f572`. The effective response batch is reproducible with:

```
python tools/effective_outcomes.py game-hisc view_scores --pattern 'view-scores-*.json' --response --baseline view-scores-both-waits-nonpositive
```

## Stop boundary

No additional specific historical call or loop predicate mismatch is exposed by the retained source-call set or inspected source-line/disassembly regions. The two wait predicates and entry-drain key are now supported in the isolated candidate. The remaining mismatch is still broad (16-byte frame deficit, 50-byte extent deficit); named-local types/declaration order already agree, original DWARF has several unlocated locals and many reused loclist ranges, and candidate-only GCC RTL cannot identify the original compiler's live ranges. There is no discriminating source-backed declaration/lifetime experiment to justify from the remaining evidence. Stop this branch until new source, DWARF, or localized instruction evidence narrows it; do not search by frame size.
