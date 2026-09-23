# `calc_replay_checksum` focused historical-source probes (2026-09-23)

Research only. No maintained source, generated current state, recovery ledger,
accepted body, or neighboring repository was edited. Compiler probes used the
locked TDM-GCC 4.4.1 TDM-2 compiler at the normal `-O2` setting. Every probe
overlaid only this function body and compiled the complete replay CU.

## Baseline and evidence

The current card is `docs/current/functions/replay/calc_replay_checksum.json`;
the complete focused evidence is
`docs/current/function-evidence/replay/calc_replay_checksum.json`. It records
the 676-byte historical function, current `-O2` candidate, branch counts, and
DWARF locals. The historical function has six branches and its only named
locals are `int i` and `unsigned int sum`; `i`'s location list spans four
machine-code ranges, and `sum` changes locations across its live ranges. The
original and candidate both emit at historical/candidate function position 4,
immediately after `calc_replay_checksum_131`; that predecessor is not exact.
The focused card classifies this task `UNKNOWN_SUPERVISOR`.

Strict baseline TU probe: `checksum-luna-base-20260923`. It compiles cleanly,
retains all six exact replay functions, and leaves whole `.text` unequal. The
checksum is 675 bytes against 676 historical bytes; its first mismatch is at
offset 19. Report: `build/tu-context/game-replay/checksum-luna-base-20260923/comparison.json`.

The original EXE disassembly at `0x41bacd` through `0x41bb4f` establishes the
initial accumulator calculation. It computes `17 * biggest_lost_combo + 17`,
then adds `127 * no_combo_top_floor`; the maintained body currently multiplies
that whole expression by two. Removing this final scale is source-supported
by the instructions and advances the first mismatch from offset 19 to offset
16, but the candidate remains 675 bytes and differs at 613 byte positions.
This does not establish a full body repair.

## Batched source-shape probes

All following labels have strict whole-TU receipts in
`docs/attempts/tu-context/game-replay/` and full comparisons in
`build/tu-context/game-replay/`:

| Body form | Label suffix | Size | First mismatch | Exact replay functions |
|---|---|---:|---:|---:|
| Existing body control | `base` | 675 | 19 | 6 |
| Remove final `* 2` | `remove-final-scale` | 675 | 16 | 6 |
| Three additive statements | `additive-terms` | 671 | 16 | 6 |
| Reverse first-term order | `reordered-terms` | 675 | 13 | 6 |
| Group `(a*17+17)+b*127` | `grouped-a-first` | 675 | 21 | 6 |
| Split/parenthesized assignment forms | `split-a-first`, `split-b-first`, `grouped-b-first`, `sum-b-plus-sum`, `sum-reverse-add`, `sum-in-parent` | 671 | 13 | 6 |

The strict grouping utility deduplicates these 11 receipts to six effective
function outcomes:

```text
python tools/effective_outcomes.py game-replay calc_replay_checksum --pattern 'checksum-luna-*.json' --compact
```

The grouped `a` form reproduces the original prefix through offset 20, including
the original `a*17+17` calculation, but GCC then selects `%ecx` for the second
field instead of the original `%edx`. The remaining forms either collapse to
one of the six function outputs or worsen the first mismatch. None reaches
`FUNCTION_MATCH`; none gains or loses any of the six exact CU neighbors. Some
split forms change raw code offsets in `load_replay` and `save_replay`, while
the strict count remains six. Whole CU text, object, and CU equality remain
false.

## Stop point

The evidenced factor-of-two source error is useful, but removing it does not
recover the original register schedule. Explicit grouping yields one distinct
output and a longer exact prefix, then stalls on an instruction-selection
mismatch. The tested parenthesization and assignment variants have been
deduplicated; more cosmetic rewrites of this expression are unlikely to help.
The unresolved function also has broad downstream differences (no test is
close to whole-body equality), and its immediate historical predecessor is
itself unresolved. Route further work to supervisor investigation of the
checksum's historical statement grouping / GCC context rather than promoting
any probe. All retained body overlays and negative strict receipts are in this
directory; generated probe outputs are under `build/tu-context/game-replay/`.
