# my_strcmp follow-up: local search boundary

Date: 2026-09-24. Research-only read of the current focused card and retained my_strcmp predicate, CFG, accepted-type-context, and pass-dump evidence. No compile was run because the evidence does not support a new discriminating source/type/lifetime/pass hypothesis. No maintained source, current generated state, or recovery ledger was edited.

## Current strict state

The generated focused card reports DIFFER / SOURCE_DIFFER, SOURCE_CONTROL_FLOW_SHAPE, original size 128 bytes, current candidate size 123 bytes, and first mismatch +21. The retained accepted-type-context batch preserved all seven exact peers and gained/lost none. It found no exact my_strcmp candidate.

## Why no follow-up compile is justified

- The original and candidate interfaces use const void *; local a and b are Treplay_post *; av and bv are signed int. The accepted Treplay_post type context preserved the same effective outputs as the earlier probes.
- The original DWARF has no lexical blocks. The maintained candidate has the same local identities and types; there is no evidenced nested lifetime to restore.
- The exact predecessor is get_replay_property; retained analysis marks my_strcmp cursor-independent and finds no peephole scratch dependency.
- The existing nine CFG/predicate probes deduplicate to seven effective results. Baseline, outer-equality/switch, and explicit-CFG overlays under accepted type context reproduce existing identities. More branch-spelling variants would repeat tested causal classes.
- Emission-neutral GCC dumps show CFG divergence already at 013t.cfg; tree optimization and RTL expand retain each candidate’s chosen edges. 187r.bbro records differing candidate block order. The historical executable provides final instruction and line evidence but no original intermediate dump to discriminate which source construction selected the historical order.

The remaining blocker is specific: find historical source evidence for the CFG construction that makes GCC 4.4.1 emit the path block before the property block with the historical conditional edges. No such evidence is present in the current card, local types, line/DWARF scope data, or retained TU/pass experiments. Stop this local spelling/type/lifetime branch; reopen only if new historical source evidence or a cross-function mechanism supplies a distinct causal hypothesis.

## Evidence identities

- src/replay.c SHA-256: A3AB23CE1F43D91C7F9E46D15E1F565576AF5CC001BE4CCA1E74F104AC6F32B5
- focused card SHA-256: 7B5B7AD537B79DE1D51BA39810D8A3A46B8E937DB0E63D6E694A1614E93D3CDE
- accepted type-context strict batch summary SHA-256: CBD39DB381D1104FCF2B227C7B7C9A6D4C767DD19D350A7655AACD7FE3397A1B
- focused card: docs/current/functions/replay/my_strcmp.json
- branch/layout record: docs/attempts/research-20260924-my-strcmp-tail/README.md
- accepted type-context and pass trace: docs/attempts/research-20260924-replay-strcmp-context/README.md

This is a scoped negative result, not recovery credit. No source candidate or acceptance receipt was produced.
