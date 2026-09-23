# `load_character` Luna research

Research lane only; no maintained source, generated current state, recovery ledger, or accepted body was changed.

## Strict status

`load_character` remains `DIFFER`, 330/330 bytes, first differing function byte at +13. The production-equivalent whole-TU compile has 62/82 exact functions and no exact-function losses. Its `load_character` section has 15 differing byte positions, all register fields; all 18 relocations resolve equally. This is not a function match.

## Hypotheses and outcomes

Five isolated whole-TU probes were grouped with `python tools/effective_outcomes.py game-main load_character --pattern 'luna-load-character-*.json'`: all five produce the same effective function identity, `f896246c764546d6`, status DIFFER, size 330, first difference +13.

- Historical definition order versus current definition order: same target bytes and same candidate emission position (73). The Cgraph emission order is unchanged around this function, so source order does not explain this register role mismatch.
- Probe-added versus production-equivalent declarations: production-equivalent means `--order current --no-prototypes`. Both modes produce the same `load_character` bytes; whole-object hashes differ because other CU code changes. The no-prototype baseline avoids the tool's generated prototype block and reports no unchanged-body code changes.
- Parameter lifetime alias: `param-log-alias.c` captures `filename` into `log_filename` and uses the alias only at the later `log2file`. It compiles to the identical function bytes. This declaration/dataflow variation does not alter the allocation.
- Four earlier local variants are already recorded in `docs/attempts/game-main/load_character-finding.md`: declaration order, initialized `name`, function-scope `buf`, and nested guard. Each collapsed to the same output.

The original DWARF and current declarations agree on `filename` (`const char *`), `attrib` (`int`), `param` (`void *`), `name` (`char *`), `buf` (`char[1024]`), and static `count` at `0x4dd330`. The original and candidate direct callee sets agree: `get_filename`, `sprintf`, `exists`, `load_character_bmp`, `log2file`, and `strcpy`.

The production-equivalent peephole2 dump shows `load_character` emitted immediately after `init_game`. The current `init_game` predecessor is `DIFFER`. GCC's dump analyzer observes scratch-register finds `di, ax` within `load_character`, so the existing `persistent-peephole-scratch` mechanism is a concrete context hypothesis. The current context table marks this target `cursor_dependent`. This is evidence of a relevant peephole2 path, not proof that `init_game` alone caused the historical register assignment.

## Remaining blocker and next discriminating experiment

Local source/declaration forms have converged. The exact unresolved question is whether the historically correct emitted body/context of `init_game` leaves the GCC 4.4.1 peephole2 search cursor in the state that produces the original `filename`/`name`/`buf` register roles. Recover or obtain a historically grounded `init_game` candidate, overlay it in this isolated TU, and compare the target function bytes plus the `init_game`/`load_character` peephole2 scratch findings. Do not change `load_character` to compensate for this upstream context.

## Artifacts

- `param-log-alias.c`: isolated source candidate.
- `status.json`: compact machine-readable result.
- Full TU comparison, object, cgraph dump, RTL CSA/peephole2 dumps, debug info and dependency records are retained under `build/tu-context/game-main/luna-load-character-*`.
- Probe receipts are under `docs/attempts/tu-context/game-main/luna-load-character-*.json`.
