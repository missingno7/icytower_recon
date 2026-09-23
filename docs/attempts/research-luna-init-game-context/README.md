# `init_game` context check for `load_character`

Isolated GPT-6 Luna/high research. No maintained source, generated current state,
recovery ledger, or accepted body was changed.

## Strict status

The fresh production-equivalent control is 63/82 exact. `load_character` remains
`DIFFER`, 330/330 bytes, first difference +13. Its original and candidate call
sets agree, as do all 18 independently resolved relocations. This is not a
function match.

## Context tested

`init_game` is the target's immediate predecessor in both historical and current
cgraph emission order (position 72); `load_character` is position 73. The current
`init_game` is `DIFFER` (5666 candidate bytes versus 5788 historical) and its
focused card records peephole2 scratch finds, so it remains a credible context
dependency. The target's compiler context is not cleared by declaration-order or
prototype changes already recorded in
[`research-luna-load-character`](../research-luna-load-character/README.md).

I compared the current baseline with a retained earlier complete `init_game`
candidate. That candidate restores several original-DWARF-named locals and their
separate lifetimes (`checkFile`, `ext`, `buf`, `profiledir`, and `last_cc`); it is
not an exact historical body. The `load_character` relocation displacements
changed with layout, but effective instructions and targets did not. Both
versions have the same extracted peephole2 scratch sequence for `init_game`
(`si, di, ax, dx, cx, bx`) and `load_character` (`di, ax`). Two diagnostic tail
call controls also left the effective target identity and those scratch sequences
unchanged; they are compiler-sensitivity controls, not historical source
hypotheses.

Across six saved TU probes, `effective_outcomes.py` reports one target outcome:
`f896246c764546d6`, `DIFFER`, size 330, first difference +13. Do not count the
raw displacement-only changes as changed target code.

## Established and unresolved

- The historical-order and production-order controls retain the same target
  output and emission predecessor.
- The tested earlier `init_game` source snapshot changes raw layout displacements
  only; it does not reproduce the historical register roles.
- The available compiler probe can overlay complete bodies, retain GCC dumps,
  report peephole2 scratch allocations, and compare effective function output. No
  tooling barrier prevented this investigation.
- The decisive experiment still needs a historically grounded `init_game` body
  or an independently justified body/context variant. The retained/current
  candidates differ from history, and the existing probe evidence cannot say
  whether the true historical peephole2 cursor state would produce the original
  `load_character` register assignment.

Do not edit `load_character` to compensate for the upstream context. Resume after
new `init_game` source evidence or a discriminating compiler-state trace exists.

## Artifacts

- `status.json`: compact outcomes and stop reason.
- Full TU reports, GCC cgraph/RTL/peephole2 dumps, objects, and overlays:
  `build/tu-context/game-main/luna-init-context-*`.
- TU receipts:
  `docs/attempts/tu-context/game-main/luna-init-context-*.json`.
- Retained historical candidate used for the source-snapshot comparison:
  `docs/attempts/game-main/bodies/init_game.c`.
- Non-candidate peephole sensitivity controls:
  `init_game-trailing-rest-probe.c` and `init_game-trailing-fourarg-control.c`.
