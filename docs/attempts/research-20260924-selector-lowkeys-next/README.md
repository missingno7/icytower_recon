# Replay selector lower key range probe ? 2026-09-24

Research only. This isolated current-order full-TU compile starts from the current accepted `src/replay.c` and adds only four source-backed `switch (kp)` cases. No maintained source, current generated state, or recovery ledger was edited. Locked compiler: TDM-2 GCC 4.4.1, `-O2`.

## Original CFG facts

The original `replay_selector` dispatch at VA `0x41d685` subtracts 3 from `readkey() >> 8`, checks the normalized index against `0x52`, then indirect-jumps through the table at `0x4d7b18`. This is 83 entries for raw Allegro keycodes 3?85. The historical table contains 72 default-target entries (`0x41d423`). In its lower raw-key range 3?46, 40 entries also target that default. Four lower keys take source-visible sort actions:

| Raw key | Allegro key | Historical target | Action |
|---:|---|---:|---|
| 3 | `KEY_C` | `0x41dadd` | `set_sort_method(3)`; set `need_to_update` |
| 6 | `KEY_F` | `0x41dab8` | `set_sort_method(4)`; set `need_to_update` |
| 14 | `KEY_N` | `0x41db27` | `set_sort_method(1)`; set `need_to_update` |
| 19 | `KEY_S` | `0x41db02` | `set_sort_method(2)`; set `need_to_update` |

These map to the locked Allegro 4.4.1 `keyboard.h` enum. The prior CFG/source crosswalk is retained at `../research-20260923-create-replay/rdata-order/lower-range-cfg.json` and `helper-context-findings.md`; table ownership/relocation evidence is in `crosswalk.json`.

## Current-source probe

Inserted just before the existing `KEY_UP` arm, the source-backed cases are:

```c
case KEY_C: set_sort_method(3); need_to_update = 1; break;
case KEY_F: set_sort_method(4); need_to_update = 1; break;
case KEY_N: set_sort_method(1); need_to_update = 1; break;
case KEY_S: set_sort_method(2); need_to_update = 1; break;
```

The full current TU compiled successfully. All seven previously exact peers stayed `FUNCTION_MATCH`: `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, `load_replay`, and `get_replay_property`. No peer gains/losses occurred. `replay_selector` remains `DIFFER` (candidate 2493 B vs historical 2845 B); the experiment does not establish full function equality or acceptance. Whole text contribution is not equal.

## Artifacts

- `current-source.c`: exact current-source baseline snapshot.
- `low-sort-cases-source.c`: isolated full-TU candidate.
- `evaluation.json`: compiler identity, strict comparison-derived statuses, peer context, and report pointer.
- `comparison.json`, `unit.o`, `relocations.txt`: comparison receipt, candidate object, and relocation dump.
- `run_probe.py`: reproducible isolated probe driver.

## Combined owner and selector probe

A second isolated current-order compile combines the four selector arms above with `static const char REPLAY_HEADER[6] = "ITR140";` and the local alias `#define replay_header REPLAY_HEADER`. This follows the historical COFF owner evidence (file-static, not external). The candidate `_REPLAY_HEADER` is section 7 `.rdata`, storage class 3, value `0x470`, matching the historical owner. `create_replay` is now strict `FUNCTION_MATCH` at 254/254 bytes.

The switch table is 83 relocated DWORDs / 332 bytes, at candidate `.rdata+0x1bc..+0x308`; historical is `.rdata+0x1b8..+0x304`, so the table still begins 4 bytes late. `replay_selector` remains `DIFFER` at 2493/2845 bytes. Of the seven exact peers in the selector-only probe, `load_replay` and `get_replay_property` regress (first byte differences at +113 and +102); `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, and `update_file_list` remain exact. The combined source therefore does not preserve all seven peers and is not promotable.

Combined evidence: `combined-summary.json`, `combined-evaluation.json`, `combined-comparison.json`, `combined-symbols.txt`, `combined-relocations.txt`, `combined-unit.o`, and `low-sort-static-uppercase-source.c`.
