# `play` scoped continuation audit (2026-09-24)

## Decision

No compiler probe was run. Current evidence does not tie the remaining frame excess to an untested source declaration, type, lifetime, CFG edge, or historical context alternative. A source rewrite now would be an ungrounded register/frame target. The next recovery decision is unchanged: keep `play` as a strict `DIFFER` and continue another evidence-backed front.

## Pinned current facts

- Current focused card: `docs/current/functions/main/play.json`; strict status `DIFFER`, difference class `STACK_FRAME_LAYOUT`, candidate body size 17,396 bytes, historical span 17,420 bytes.
- First mismatch is function offset +8; the prologue allocates 0xa1c bytes versus the historical 0x9fc (32-byte excess). This identifies a frame/spill symptom, not a missing historical operation or layout-only match.
- Current maintained source already contains the evidence-backed results-block lexical move recorded in `docs/attempts/game-main/play-control-flow-20260923.md`: original DWARF scopes put `hy`, `gotHigh`, `qualify`, `qualifyValue`, and `gameover_bmp_id` after the replay filename buffer scope. The move aligned `speeds`, `rec_ctrl`, and the reused `fbuf`/`qualifyValue` location, but left the 32-byte excess.
- The same retained note identifies the remaining register/spill difference at an earlier arithmetic site as a symptom without evidence that the source expression itself is wrong. Rewriting it to force a register would be target fitting.
- The summary hint family is closed locally: `docs/attempts/research-supervisor-play/play-summary-rtl-common-tail-20260923.md` shows two source `new_rand` calls survive optimized GIMPLE and RTL, then one disappears at GCC 4.4.1 RTL `181r.csa` as the suffix is commoned. Equivalent source duplication is not discriminating.
- Current main.c strict-count evidence is taken from generated current progress; this research did not compile any candidate and therefore makes no peer-effect claim.

## Hypothesis outcomes considered

A new declaration/lifetime probe would be informative only if current DWARF or the target residue mapped a specific untested object to the excess frame region and predicted a concrete change in allocation or instruction sequence. Current retained evidence instead shows the previously identified scope correction already in place and offers no such mapping. The known source-spelling family around the summary call is compiler-canonicalized. Therefore neither a one-off edit nor a batch of cosmetic variants would separate causal explanations.

## Reopen condition / next discriminating experiment

Reopen this branch when one of these appears: (a) an original-versus-candidate local-location comparison identifies a still-mismatched live range/slot plausibly accounting for 32 bytes; (b) a historical CFG or line/DWARF trace identifies a missing predecessor that affects the spill/register pressure at the cited arithmetic site; or (c) a TU-order/predecessor experiment predicts a named downstream emission change while preserving exact peers. Then freeze predictions, compile the smallest control/variant pair in historical order with `--no-prototypes`, deduplicate effective `play` output, and compare the target residue and all exact peers.

## Provenance

No maintained source, ledger, or generated current state was changed. No recovery credit is claimed.

Source/card/evidence SHA-256:
- `src/main.c`: `2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044`
- `docs/current/functions/main/play.json`: `4eb1a09961c40ac18a1dae4a25043bf3e0568f486e860916d1321784c90ed4ad`
- `docs/attempts/game-main/play-control-flow-20260923.md`: `35c8aa6837daad845c3f9bf9c601dd292e0e089c2d651468d5a828a46de9d803`
- `docs/attempts/research-supervisor-play/play-summary-rtl-common-tail-20260923.md`: `48d66cf762a88c22f3a5b66206d035b71ddf12c5b018a4b6bef074a0250d55f3`
