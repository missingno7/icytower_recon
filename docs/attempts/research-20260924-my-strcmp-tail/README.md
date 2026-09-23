# `my_strcmp` historical branch-layout investigation

Date: 2026-09-24. Research-only full replay-TU probes on a separate copy of
`docs/attempts/research-20260923-replay-pretable-owner/property-case-order-source.c`.
That source copy retains the named header, 83-entry switch table, and eight
exact functions. Each overlay replaces only `my_strcmp`; the reordered
`get_replay_property` body in the source base was left untouched. No maintained
source, current generated state, or recovery ledger was edited.

## Historical behavior and evidence

The original `my_strcmp` is 128 bytes at `0x41e6c0`. Its disassembly establishes
this behavior:

1. If the two `directory` bytes differ, branch to the shared tail at +112. That
tail decrements the original `a->directory` byte: value 1 returns -1, every
other value returns +1.
2. If the bytes are equal and nonzero, compare `full_path` with `stricmp`.
3. If the bytes are equal and zero, sort modes 2–4 compare
   `get_replay_property` values: signed `av > bv` returns -1; otherwise return
   +1. Other modes compare `full_path` with `stricmp`.

The important original edges are `jne +0x70` at +20 to the shared directory
tail, `je +0x30` at +24 to property sorting, and `ja +0x1a` at +37 back to the
path comparison when the sort mode is outside 2–4. Property comparison uses
`jg` at +98, with the greater-than result at +116. The directory tail is
`dec %al; jne +0x64` at +112/+114, then -1 on fallthrough.

DWARF records parameters `c`/`d` as `const void *`; `a` and `b` as
`Treplay_post *`; and `av`/`bv` as signed `int`. The locals are declared at
historical lines 649–651, and there are no lexical blocks. The line table is
particularly useful for code layout: the string-compare instructions at +26
and +100 map to source line 671, while the property mode/calls/comparison at
+48 through +77 map back to lines 662–668. The mismatch tail at +112 maps to
line 654. Thus the emitted string path precedes the property block even though
its source line is later; code block placement is part of the remaining
compiler behavior.

## Prior attempts read

Read `docs/current/functions/replay/my_strcmp.json`, all 13 entries in
`docs/attempts/game-replay/my_strcmp.jsonl`, and all three predicate-probe
records in `docs/attempts/predicate-probes/game-replay/my_strcmp.jsonl` plus
`my_strcmp.json`. The existing attempts already cover the front-nested
directory return, equality-to-one spelling, switch versus unsigned interval,
and range/guard inversions. Those remain `DIFFER` at 123/128 (first +21) or
128/128 (first +24); simple predicate substitutions are not repeated here.

## New whole-TU outcomes

The locked TDM-2 GCC 4.4.1 `-O2` whole-TU overlays all compiled. Each produced
8/15 exact functions with no losses; relative to current reference's six,
`create_replay` and `save_replay` become exact through the copied owner base.
Each target remains `DIFFER`, with three unequal relocations.

| Probe | Structure tested | Effective output | Target |
|---|---|---|---|
| `luna-my-strcmp-owner-baseline-20260924` | copied owner-base control | `b414923b3c83083f` | 123/128, first +21 |
| `luna-my-strcmp-outer-equal-interval-20260924` | equal-directory block, unsigned interval, shared tail | `87ce5531f9364b8c` | 122/128, first +21 |
| `luna-my-strcmp-outer-equal-switch-20260924` | equal-directory block, switch, shared tail | `577b1637b6435bf7` | 128/128, first +24 |
| `luna-my-strcmp-prop-le-20260924` | outer-equal/switch, reverse signed property predicate | `acb18905ad3b6bdb` | 127/128, first +21 |
| `luna-my-strcmp-dir-ne-20260924` | outer-equal/switch, reverse tail predicate | `363349c060a40064` | 125/128, first +20 |
| `luna-my-strcmp-explicit-cfg-20260924` | explicit labels for path/property/directory destinations | `2fba60d27256a555` | 127/128, first +20 |
| `luna-my-strcmp-zero-block-path-last-20260924` | explicit zero block, path fallback after switch | `363349c060a40064` | 125/128, first +20 |
| `luna-my-strcmp-zero-block-path-last-le-20260924` | same, reverse signed property predicate | `3fddac2dece1be9b` | 126/128, first +20 |
| `luna-my-strcmp-reversed-returns-20260924` | outer-equal/switch, both return predicates reversed | `3fddac2dece1be9b` | 126/128, first +20 |

Effective-output grouping: `python tools/effective_outcomes.py game-replay my_strcmp --pattern 'luna-my-strcmp-*-20260924.json' --compact` (9 probes, 7 outcomes). The outer-equal/switch form reproduces the 128-byte historical size and the +20 `jne` to the shared tail. It still emits `jne` at +24 to the later path block, while history has `je` to the later property block. Its signed property result uses `jle` to the +1 path, versus historical `jg` to the -1 path; its tail uses `je` to the -1 block, versus historical `jne` to the +1 block. Reversing source predicates changes those edges, but moves other block targets and sizes rather than yielding the original layout.

## Stop point and artifacts

The source-backed outer-equality/shared-tail structure advances the comparison:
it recovers the historical function size and first directory-mismatch edge.
The line table and original bytes establish a source-level CFG, but tested C
forms do not reproduce GCC's block placement and conditional polarity. The
remaining mismatch is code-layout/branch selection, not an unresolved semantic
comparison. No strict candidate was found.

The separate source copy and all exact body overlays are in this directory.
Full strict CU reports are under `build/tu-context/game-replay/` with the
labels above. `src/replay.c` SHA-256 remains
`73d99aea3da12bb730812e43443c1a0dc07b8457c3469c4d0b285ef0a1d20c93`; recovery
ledger SHA-256 remains
`2f0710c753742dda1de1bb624cce6fa378ba14c6a205adb9e3552c67bbd8f360`.
