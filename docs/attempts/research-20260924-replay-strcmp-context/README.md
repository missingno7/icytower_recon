# Replay `my_strcmp` strict investigation in accepted type context

Date: 2026-09-24. Research-only. The strict batch rebuilt isolated overlays from the accepted `Treplay_post` generated-header TU at `build/tu-context/game-replay/treplay-post-generated-header-20260924/overlay/src/replay.c`. It used the locked TDM-2 `-O2` command and accepted current definition order. It did not edit `src/replay.c`, current cards, or `src/recovery.json`.

## Strict batch

`strict-batch-summary.json` and the three `build/tu-context/game-replay/replay-strcmp-context-*` comparisons are the receipts. All three overlays compiled and preserved the seven `FUNCTION_MATCH` peers recorded by the accepted generated-header context.

| Candidate | Strict status | Size | First mismatch | Effective output |
|---|---:|---:|---:|---|
| Maintained body baseline | DIFFER | 123/128 | +21 | `b414923b3c83083f` |
| Outer equality plus switch | DIFFER | 128/128 | +24 | `577b1637b6435bf7` |
| Explicit path/property/directory labels | DIFFER | 127/128 | +20 | `2fba60d27256a555` |

Each output identity agrees with the earlier body probe under the prior whole-TU research base. The accepted generated type context did not change these bodies' output. The equal-size switch candidate reaches historical +20 `jne` to the shared directory tail, then differs at +24: candidate `jne` targets the path block while historical `je` targets the property block. No candidate is an exact match.

## Pass trace and stopping point

`pass-dump-summary.json` records baseline versus outer-equal pass facts. The added flags only emitted dumps: `.text`, `.rdata`, `.data`, and `.bss` are byte-identical to each variant's no-dump strict build.

- `013t.cfg` already reflects the source CFG difference: baseline starts with `directory !=`, outer-equal starts with `directory ==`.
- `123t.optimized` folds conditions and merges shared return blocks while preserving each form's condition edges.
- `128r.expand` carries those chosen conditional edges into RTL. No separate type, predecessor, or peephole scratch effect appears; accepted `Treplay_post` has the historical seven members/layout, `my_strcmp` is marked cursor-independent, its peephole scratch-find list is empty, and its immediate predecessor `get_replay_property` is an exact body match.
- `187r.bbro` is where GCC records the final physical block order. Baseline order is `2 5 6 9 3 11 12 7 10`; outer-equal order is `2 3 5 6 10 8 9 11 12`. The resulting object uses a different fallthrough/branch target arrangement at +24 than history. The original EXE gives the target edge and DWARF line mapping, but does not provide an original intermediate pass dump.

Prior nine branch/predicate probes dedup to seven output identities, with repeated outcomes across distinct spellings. This batch reconfirmed three identities under the accepted type context, so stop local spelling. No further source-backed TU/type/pass discriminator follows from the current evidence: changing optimization flags or injecting compiler hints would not be historically evidenced. Strict state remains DIFFER (123/128, first +21); the blocker is the historical source/CFG shape that guides GCC's block-reordering pass to emit the path block before the property block with the original branch edges. No candidate or acceptance receipt exists.
