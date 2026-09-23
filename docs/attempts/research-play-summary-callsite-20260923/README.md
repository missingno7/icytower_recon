# `play` summary hint call-site investigation (2026-09-23)

## Result

No new source rewrite or TU probe was justified by the available evidence. The
current production body and current-order `--no-prototypes` TU already have a
baseline receipt, and the existing isolated two-arm trial already showed that
GCC 4.4.1 common-tails the duplicate hint call during `181r.csa`. The requested
register distinction remains observed but unexplained. This note makes no
claim that a named local causes it.

## Evidence reviewed

- Current source: `src/main.c`, summary block around lines 5499-5525. It has a
  `gotHigh` prefix `memcpy`, followed by the guest check and one hint `strcpy`.
- Historical bytes: `python tools/function_lines.py game-main play --source-view 4736 4782`.
  At original offset 16822, the `gotHigh` test branches around the prefix copy.
  The no-prefix route has `new_rand` at 16845 and materializes the divisor in
  ESI at 16855. The prefix-copy route reaches the second guest check and has
  `new_rand` at 16921, materializing the divisor in ECX at 16931. Both paths
  reach the common `strcpy` setup at 16867 / label `415be3`.
- Historical DWARF: `python tools/function_lines.py game-main play --blocks`.
  The `falling` loclist includes `16813..16857`; the range ends exactly at the
  divisor-register move's following instruction boundary. This is a location
  observation, not enough to attribute the register choice to `falling`.
  `gotHigh`, `pos`, and `skip_keys` have no location interval at offsets 16845
  or 16921; `quit` has a stack location. Loclists do not identify an unnamed
  compiler temporary that could account for a register being occupied.
- Current-order production context: `build/tu-context/game-main/luna-supervisor-play-current-no-protos-20260923/`
  contains `unit.o`, `dwarf.txt`, and `comparison.json`. The matching focused
  card is `docs/current/functions/main/play.json` (`DIFFER`, historical size
  17420).
- Existing two-arm experiment and optimizer boundary:
  `docs/attempts/research-supervisor-play/play-summary-rtl-common-tail-20260923.md`;
  receipt `docs/attempts/tu-context/game-main/luna-play-pass-summary-split-repro-20260923.json`;
  isolated source `docs/attempts/research-supervisor-play/play-summary-high-split-production.c`;
  pass/RTL dumps under `docs/attempts/research-supervisor-play/build/`.
  The duplicate non-guest suffixes survive through `179r.dse2`, then one call
  disappears in `181r.csa` while the common label gains another use. The trial
  remains `DIFFER` at 17,429 bytes; no production source or ledger was changed.

## Why no new probe was run

The current source already represents the visible branch distinction: the
high-score path first writes the prefix, whose leftover bytes can matter when
the later hint is shorter. The existing split trial tested spelling-level
duplication and established tail merging. Available DWARF and machine code do
not provide a supported source-level distinction that predicts the ESI versus
ECX divisor choice. A further arbitrary temporary, volatile, or control-flow
rewrite would repeat the earlier low-information trials rather than test an
evidenced lifetime hypothesis.

The concrete missing evidence is historical compiler intermediate state around
the two blocks (RTL pseudos/register liveness before allocation, or an equivalent
historical source/lifetime fact). The binary gives the final register choices;
the available DWARF maps only some source variables and leaves the relevant
register-pressure cause unidentified. Without that evidence, source liveness
cannot be responsibly reconstructed from this register difference alone.

## Scope

This investigation was read-only against maintained source, cards, recovery,
and ledgers. All artifacts cited above are existing retained artifacts; this
folder contains the compact handoff only.
