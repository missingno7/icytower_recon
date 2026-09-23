# Isolated Luna research: `load_replay`

## Scope and baseline

Research only. No maintained source, recovery ledger, current generated view, accepted body, oracle, or other task's file was modified. Artifacts are isolated in this directory. The parent supervisor independently reports a fresh `--verify-all` baseline of 204 exact functions.

The current focused card is `docs/current/functions/replay/load_replay.json`. It says `DIFFER` / `SOURCE_DIFFER`, candidate size 1148 vs historical 1136, first raw mismatch at +0xab, 39 relocations with 22 not independently matching, 11 branches on each side, 38 direct calls, four referenced globals, and one untyped literal diagnostic. The owning CU currently has 6/15 strict function matches in the isolated full compare.

The unmodified candidate body is copied as `baseline.c`; no production begin/edit/promotion workflow was used. Full reports retain each probe's function bytes, relocation mapping, object inventory, and CU result.

## Hypotheses and experiments

| Probe | Hypothesis | Result |
|---|---|---|
| `baseline` | Reproduce current focused evidence from an isolated copy and confirm effective output | Reproduced `load_replay` 1148/1136, first difference +0xab, same 6/15 CU strict count. Emitted-function byte SHA-256: `a783610b14bf303072729751155d46e2765307ffd82119dcc590078ae0ca5b96`. |
| `typed-packfile` | Original DWARF local `pf` is `PACKFILE *`, while maintained source says `void *`; pointer declaration may affect codegen | DWARF-accurate type edit preserved the exact same emitted-function byte identity, size, first difference, relocation count, and CU strict count. This establishes the local type fact, but it does not explain this code mismatch. |
| `historical-order` | Historical DWARF definition order may change GCC whole-TU state reaching `load_replay` | Current-source historical-order overlay retained identical function bytes and same candidate offsets. Historical ordering alone is eliminated for the current candidate. |
| `create-after-load`, `draw-after-load` | Moving a callee or an unrelated large peer may change codegen context | Both overlays compiled with the same cgraph emission order as baseline; `load_replay` bytes stayed identical. GCC cgraph keeps `create_replay` before its caller `load_replay`. Do not repeat source-order variants that leave this graph fixed. |

Compiler artifacts in `compiler-dumps/` include candidate IPA cgraph, RTL csa and peephole2 dumps. `load_replay` is emitted after `create_replay`; candidate peephole2 dump shows one scratch-register addition (`ax`) in `load_replay`. That dump exposes candidate behavior only; original executable evidence cannot establish historical RTL or peephole cursor state.

Instruction alignment localizes a prominent difference to the 5× `ccc` / 5× `jc` reads and neighboring field reads: original retains replay pointer `%edi` and file pointer `%ebx`; candidate swaps these roles and adds moves, with a padding `xchg %ax,%ax`. Candidate's cleanup target is 12 bytes later than the original. This is a codegen/register-allocation difference, not a size proof or a confirmed semantic divergence. Branch and call counts agree, but that alone is not proof of CFG equivalence.

## Stop reason and next discriminating work

The tested type and source-order hypotheses collapse to one effective function output. The current card and instruction evidence expose no missing caller prototype, parameter ABI mismatch, or simple declaration-width/signedness issue. The remaining blocker is the GCC 4.4.1 code-selection cause for the register-role shuffles around the array-field read loops; source spelling, local pointer type, and historical definition order did not move it. There are no isolated exact bytes to promote.

A next useful experiment needs new evidence about those reads or a compiler mechanism: map the original DWARF line/location ranges for `i`, `pf`, and `r` through the ccc/jc region and compare with current candidate debug locations; if those agree, inspect a targeted GCC pass trace for the first point where the register roles diverge. Do not continue cosmetic source-form changes in the same spelling family.

## Compact outcome index

`probe-summary.json` records source/object/function-output hashes and strict statuses. `context-order-summary.json` records cgraph emission orders and focused statuses. `*-comparison.json` contains full per-function and CU comparison evidence. `historical-source-order.c` and `create-after-load.c` / `draw-after-load.c` are isolated TU candidates. `compiler-dumps/` contains detailed GCC diagnostics.
