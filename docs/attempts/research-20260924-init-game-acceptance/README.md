# `init_game` acceptance follow-up — 2026-09-24

Research-only current-order, no-prototype full-TU probes against current `src/main.c`. No maintained source, generated current state, or recovery ledger was changed.

## Corrected checkFile candidate

`literal-fields-checkfile-assigned.c` applies three source-supported changes: the historical leading newline in the `INIT GAME` literal; stores to `play_char.max`, `.value`, and `.bmp`; and a lexical-block `checkFile` local assigned from `argv[i]` at the start of each parser iteration before `replay_path` or option tests use it. The `check` local is also in the historically evidenced parser block. A complete diff audit against `current-body.c` found only these changes.

Fresh probe label: `init-game-acceptance-literal-fields-checkfile-assigned-20260924`. GCC compile succeeded. `init_game` is 5688/5788 bytes and remains DIFFER; first mismatch is +14 (entry register assignment). The whole TU retains 63 exact functions, with no gains or losses and no implicit declarations. `new_game` remains FUNCTION_MATCH (1139 bytes, historical position 64); `run_demo` remains FUNCTION_MATCH (159 bytes, position 79). There are 23 accepted storage owners and zero rejected; `.data` and `.bss` hashes equal the previous source-backed probe. The checkFile source lifetime has a distinct effective output from the literal+fields beam and is not deduplicated with it.

## Failed negative retained

`literal-fields-checkfile.c` and its original probe/receipt are preserved unchanged as a failed negative. That body declared `checkFile` and used it for option tests without assigning it, so it contains undefined behavior and is not a valid historical candidate. Do not use its corresponding `init-game-literal-fields-checkfile.tu-context.json` spec. The corrected candidate has a separate body, spec, receipt, build label, and output.

## Promotion preparation

The corrected raw transaction spec is `init-game-literal-fields-checkfile-assigned.tu-context.json`. The literal+fields intermediate candidate and spec remain available for serial validation. These diagnostic probes do not replace the formal transaction check, including its ordinary-link gate.
