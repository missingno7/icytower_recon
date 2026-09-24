# `create_replay` declaration-context probe

Date: 2026-09-24. Research-only full-TU probes with locked TDM-2 / GCC 4.4.1 at `-O2`. Maintained `src/replay.c`, `src/recovery.json`, generated current state, and all function bodies were left untouched.

## Result

The smallest tested context that makes the maintained `create_replay` body strictly `FUNCTION_MATCH` is changing only the header declaration and its one use from mutable `static char replay_header[]` to `static const char replay_header[6]`, retaining the existing `"Harold"` literal and body. The retained base is `maintained-const-header-source.c`; the canonical probe receipt is `create-replay-maintained-const-header.json`.

The probe reports 6 exact functions before and 7 after, with no losses. The six preserved production exact functions are `get_sort_method`, `set_sort_method`, `hash`, `destroy_replay`, `update_file_list`, and `get_replay_property`. `get_replay_property`'s source body is byte-for-byte the maintained body in this probe.

This is a strict function result only. It does not establish the historical header object's identity or make the replay CU an object/CU match. The historical storage card says the original owner is uppercase global `REPLAY_HEADER`, `const char[6]`, `.rdata`, initial bytes `ITR140` (`docs/current/storage/game-replay/224757.json`). The successful minimal probe instead has a lower-case file-static owner. It proves that this emitted function can be exact under that candidate context; it does not close the original storage ownership task.

## Uppercase owner control

Two probes replaced the maintained header with `const char REPLAY_HEADER[6] = "ITR140";` and made the unchanged `create_replay` body refer to `REPLAY_HEADER`:

- `create-replay-header-owner-current.json` places the declaration at the maintained declaration location.
- `create-replay-header-owner-top.json` places it immediately after the includes.

Both compile, but neither reaches `FUNCTION_MATCH`: `create_replay` is `CODEGEN_SIMILAR`, with the first mismatch at function offset 127 and two differing bytes. The resolved `.rdata` relocation for the `"Harold"` literal does not match the original target. These probes also regress maintained exact functions: 4 exact remain, with `get_replay_property` and `update_file_list` lost. Moving the global declaration to the top did not change that outcome.

The loss of `get_replay_property` is a preservation failure, not authorization to edit its protected body. The owner-aligned 9/15 `load_replay` branch uses a retained owner replacement for `get_replay_property`; that branch is excluded from this search and does not supersede the maintained exact body.

## Probe artifacts

- `maintained-const-header-source.c` — minimal successful context retained from the load-replay research.
- `header-owner.c`, `header-owner-top.c` — uppercase global owner controls.
- `../tu-context/game-replay/create-replay-maintained-const-header.json` — strict successful context receipt.
- `../tu-context/game-replay/create-replay-header-owner-current.json` and `create-replay-header-owner-top.json` — failed uppercase-owner controls.
- Full comparison reports are under `build/tu-context/game-replay/` with the matching probe labels.

## Causal follow-up: why the uppercase owner loses exact neighbors

Three additional locked full-TU probes separate definition order, linkage, and symbol spelling:

- Recompiling the uppercase global owner with `--order historical` produces the same effective outcome as both current-order uppercase global probes. The function order hypothesis is not supported.
- With the declaration kept external but named lower-case `replay_header`, the six exact neighbors remain exact. `create_replay` remains `CODEGEN_SIMILAR` because its two header relocations are unresolved against the historical uppercase storage symbol.
- With a private `static const` declaration named uppercase `REPLAY_HEADER`, the same exact-neighbor losses occur as with the external uppercase owner. So external versus private linkage alone does not explain those losses.

The strict reports show every changed operand in the two lost neighbors is a `.rdata` relocation: `get_replay_property` has 11 unequal `.rdata` relocations in the external uppercase probe; `update_file_list` has one. Their source bodies are unchanged. The create_replay global-uppercase probe also has a `.rdata` relocation mismatch to the `"Harold"` literal at function offset 127. This directly supports emitted `.rdata` target placement as the blocker. The evidence ties the shifted placement to introducing the uppercase-named const owner in these contexts; it does not establish a general GCC name-order rule.

Effective-output grouping for the seven probe receipts (`python tools/effective_outcomes.py game-replay create_replay --pattern 'create-replay-*' --compact --response`) found five outcomes. The current/top/historical-order uppercase global probes deduplicate together; the global lower-case and static uppercase probes are separate outcomes; the minimal static lower-case declaration remains the only strict `create_replay` result. This is sufficient to stop: changing definition order or linkage alone did not repair the uppercase-owner outcome.

Additional source artifacts: `header-global-lower.c`, `header-static-upper.c`. Receipts: `create-replay-header-global-lower.json`, `create-replay-header-static-upper.json`, and `create-replay-header-owner-historical-order.json` under `../tu-context/game-replay/`.