# `play` summary call-prefix cause check (2026-09-24)

## Result

The retained two-arm candidate remains `DIFFER` at 17,429 bytes and emits six
`new_rand` calls, as already established through GCC 4.4.1 RTL stage
`181r.csa`. A full isolated historical-definition-order compile produced the
same effective `play` output as the retained split probes (effective outcome
identity `76e71104a738dd74`). Thus historical definition order alone does not
explain why the original keeps two random/divide prefixes.

The original source view (`python tools/function_lines.py game-main play
--source-view 4740 4790`) shows the no-prefix call at offset 16845 with its
divisor in ESI at 16855, then the shared `strcpy` setup at 16867. The
high-score-prefix path has a second call at 16921, its divisor in ECX at
16931, and jumps back to that same setup. Both prefixes select `hints` and
converge before `strcpy`.

Historical DWARF does not establish a named-local lifetime that explains the
register difference: `falling` is locatable through 16857, ending just after
the first divisor move; `gotHigh`, `pos`, and `skip_keys` have no location
range at either call offset, and `quit` is stack-based. This is a register
observation, not proof that `falling` or another local causes it.

## Isolated probe and neighbor check

- Receipt: `docs/attempts/tu-context/game-main/luna-play-summary-historical-order-split-20260924.json`
- Overlay TU: `build/tu-context/game-main/luna-play-summary-historical-order-split-20260924/overlay/src/main.c`
- Candidate body: `docs/attempts/research-supervisor-play/play-summary-high-split-production.c`
- Prior pass/RTL evidence: `docs/attempts/research-supervisor-play/play-summary-rtl-common-tail-20260923.md`

The compile succeeded with `--order historical --no-prototypes`. It retained
63 exact functions, with no gains or losses; `new_game`, `run_demo`, and the
other previously exact neighbors remain exact. Raw relocation-sensitive bytes
changed for `_mangled_main`, `do_replay_menu`, `load_new_ad_image`, and
`run_demo`, but the tool reported no unchanged-body effective code changes.
Some effective comparisons were unavailable, so this diagnostic is not a CU
or whole-text match claim.

## Next evidence boundary

The historical CFG already shares the copy tail; ordinary duplicate-source
spelling was shown to common in RTL, and changing whole-TU definition order
did not affect that result. Available DWARF does not identify the unnamed
register-pressure cause. Further source perturbations would be speculative
without historical intermediate register-liveness evidence or another
source-backed distinction that changes dataflow at one prefix. No maintained
source, generated card, or recovery ledger was changed.
