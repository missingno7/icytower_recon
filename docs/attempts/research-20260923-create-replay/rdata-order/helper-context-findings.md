# Replay helper context findings

Research-only TDM-2/GCC 4.4.1 `-O2` overlays. No maintained source, current cards, or recovery ledger changed.

## Strict helper regression

The owner-aligned source overlay (`full-owner-context-summary.json`) has the historically named `_replay_header` at `.rdata+0x470`, but its generated replay-selector table begins at `.rdata+0x1b4`; the historical table begins at `+0x1b8`. The table is 83 relocated DWORDs (332 bytes) in both cases. The four-byte early start and end are a real section-layout difference, even though the header and warning strings align.

`get_replay_property` remains 1,147 bytes. The full owner context reports `body_shape_equal=true`: instruction boundaries and mnemonic shape agree. Its strict failure is eight unequal `.rdata` references, at function offsets 135, 871, 916, 951, 990, 1036, 1096, and 1130. The first points at the error string expected at `0x4d7ce5` but resolves to `0x4d7ce1`; later format strings similarly resolve to shifted or differently ordered section content. This is data relocation/layout, not a changed instruction schedule.

The source-preserved helper variant kept the original hard-coded `memcmp(..., "ITR140", ...)` comparison. It fails at offset 102 as well as eight format-string relocations. The comparison relocation resolves to the candidate's separate literal at `0x4d7cbb`; the original relocates to the single named owner at `0x4d7dd0`. Equal bytes in two places do not establish the original owner. Therefore preserving helper source text alone does not preserve its strict identity once the owner-aligned const header moves the string pool.

## Context control

`create-replay-owner-no-prototypes-20260923` was built with TU context body overlays, historical definition order, and no generated prototype block. It retains the original `get_replay_property` body and hard-coded literal and reports `FUNCTION_MATCH` (1,147/1,147 bytes; all 41 relocations equal). However this control uses maintained mutable `static char replay_header[]`, which puts the header in `.data`, not the sought const `.rdata` owner. It does not solve the owner layout.

A stricter control removed all three generated prototype blocks from `preserve-exact-helper-source.c`, retaining the const header and preserved helper body. It still has `_replay_header` at `.rdata+0x470` and the 332-byte table at `+0x1b4`, but `get_replay_property` remains DIFFER with nine relocation mismatches, including the separate ITR140 literal target at +102. The no-prototype context thus does not reconcile the const-owner and protected-helper constraints. This is retained as a useful data-layout/codegen tradeoff, not an acceptance candidate.

Artifacts:

- `full-owner-context-summary.json`: owner-aligned baseline and neighbor statuses.
- `preserve-exact-helper-summary.json`: helper source kept unchanged; named owner and switch context.
- `create-replay-preserve-helper-no-prototypes-20260923-summary.json`: no-prototype const-owner control.
- `preserve-helper-no-prototypes-source.c`: exact compiled source for that control.
- `context-bodies/`: extracted retained function definitions for the first no-prototype context control.

## Lower switch range, source and CFG facts

The original indirect dispatch subtracts 3 and accepts indices through 0x52, so table keys are raw Allegro key values 3–85. The table has 83 entries; 72 entries repeat the default target `0x41d423`. In the added lower range 3–46, only four entries differ from default:

| Key | Allegro enum | Original target | Observed action |
|---:|---|---:|---|
| 3 | `KEY_C` | `0x41dadd` | set sort method to 3 and mark list update |
| 6 | `KEY_F` | `0x41dab8` | set sort method to 4 and mark list update |
| 14 | `KEY_N` | `0x41db27` | set sort method to 1 and mark list update |
| 19 | `KEY_S` | `0x41db02` | set sort method to 2 and mark list update |

The other 40 keys in 3–46 go to the repeated default target. The locked Allegro 4.4.1 `keyboard.h` enum supplies the four symbolic values. These four semantically observed source cases generate the full 83-entry compiler table in `low-sort-keys-summary.json` and `full-owner-context-summary.json`; no data was inserted to make its size.

The isolated source is preserved in `low-sort-keys-source.c` and `full-owner-context-source.c`. The probe is diagnostic only; `replay_selector` remains DIFFER, and no candidate is promoted.
