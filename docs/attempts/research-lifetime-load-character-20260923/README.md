# `load_character` parameter-home probes

Isolated whole-TU research only. Maintained `src/`, generated current state,
accepted bodies, and `src/recovery.json` were not changed. Both probes used
locked TDM GCC 4.4.1, `game-main`, current order, and `--no-prototypes`.

## Evidence carried forward

The historical DWARF loclist reported in
`docs/attempts/game-main/load_character-finding.md` gives `filename` in ESI at
function offsets 31–58, then in its incoming stack home at EBP+8 through the
end. `name` is in EBX at most later offsets. The vector2 pointer-lifetime study
showed that changing whether a pointer variable remains live across an early
sample can change when its underlying parameter is materialized. That suggests
testing explicit source lifetimes here, but it does not license arbitrary
volatile or aliasing changes.

The carried-forward finding says 13 differing ModRM register fields. The fresh
production-equivalent report for the current retained body instead has 15 byte
difference offsets (`+13, +16, +24, +41, +53, +59, +67, +138, +178, +185,
+202, +206, +248, +254, +258`). It remains 330 bytes and 92 instructions;
all function relocations and the direct `log2file` target resolve equally.
This count discrepancy is preserved for follow-up rather than silently
reconciled: the finding predates the current retained body form.

## Bounded trials

| Label | Lifetime hypothesis | Strict result |
| --- | --- | --- |
| `research-lifetime-load-character-late-log-home-20260923` | Assign a `log_filename` alias immediately before the late `log2file` call, so its local lifetime begins after the BMP load. | 330 B, 92 instructions, first mismatch +13. |
| `research-lifetime-load-character-format-alias-20260923` | Use an alias only for the early `sprintf` argument while retaining direct `filename` use for the later log call. | 330 B, 92 instructions, first mismatch +13. |

`python tools/effective_outcomes.py game-main load_character --pattern
'research-lifetime-load-character-*' --compact` groups both reports as one
effective function output (`f896246c764546d6`). The entry allocator still
loads `filename` into EBX and the result of `get_filename` into ESI. Neither
alias arrangement makes GCC re-materialize `filename` from its EBP+8 home or
select the historical EBX/ESI roles. These source-level lifetime forms are
therefore eliminated for the current retained body; no strict match was found.

Each comparison retains the full diagnostic inventory: all 82 function
records, 13 object sections, 428 COFF symbols, 4,424 relocations, 93 common
allocations, and initialized `.data`/`.rdata` ownership. Each probe preserves
the 63 exact-function count and reports no effective code change in an
unchanged-body neighbor. Raw call-displacement changes in unrelated later
functions are recorded separately by the probe as a same-CU layout effect.

## Artifacts

- Isolated source overlays: `late-log-home.c`, `format-alias.c` in this folder.
- Probe receipts: `docs/attempts/tu-context/game-main/research-lifetime-load-character-*.json`.
- Full object comparisons and pass dumps: `build/tu-context/game-main/research-lifetime-load-character-*/`.
- Prior location-list and source-form analysis: `docs/attempts/game-main/load_character-finding.md`.
- Prior whole-TU context finding: `docs/attempts/research-luna-load-character/README.md`.

The remaining concrete context hypothesis is still the predecessor `init_game`
and GCC 4.4.1 peephole2 search cursor documented in the prior context finding.
These two local-lifetime probes do not strengthen or disprove that hypothesis.
