# `load_character` current-context baseline — 2026-09-24

Research only. Maintained source, current generated state, production ledgers,
and accepted bodies were not edited. No source variants were compiled.

## Probe and prediction

Reproduce the current whole-TU baseline at HEAD `22423901dd54a51eefb1b18fcf9c5f75eab065a4`
with `tools/tu_context_probe.py game-main src/main.c`, current definition
order, no generated prototypes, and `load_character` focused. This checks
whether the currently accepted CU context still emits the previously retained
`load_character` outcome and exact-peer count. If intervening context changes
do not affect its emitted stream, its effective identity should remain
`f896246c764546d6`; a changed identity would establish a context-sensitive
emission change, while the strict function comparison independently decides
whether recovery status changes.

Command:

```powershell
python tools/tu_context_probe.py game-main src/main.c research-load-character-next2-current-baseline-20260924 --order current --no-prototypes --no-dumps --focus load_character
```

## Result

- Compile succeeded. The whole-TU receipt retained **64/82 exact functions**
  before and after, with no exact-function gains/losses and no changed
  unchanged-body code.
- `load_character` remains **DIFFER**, 330/330 bytes, 92 instructions,
  first mismatch +13, 15 differing bytes, all 18 resolved relocations equal,
  six calls and 7 branches. Candidate and historical function positions are
  both 73.
- Its current effective identity is `9aab2a102371322cb1ef09602ee01adb2208a08a1cbb5a932c2bcacb0df0ba1a`,
  distinct from the older retained `f896246c764546d69c2d8ba5da5db0a8ee340687027c787d71c68738764bbfbc`.
- Comparing the two candidate instruction streams shows register-selection
  changes at offsets +177/+184 (`ecx` to `eax`) and +247/+253 (`edx` to
  `edi`), plus five changed string-pool immediates/call displacement fields.
  The initial +13 register mismatch persists. This is a new effective output
  class, not a strict gain.

The old comparison was built from a different retained source context: its
overlay hash is `1420f42d9e30b68d01e929d46939651a34e118669b6009f78d46cce9f02014ef`,
whereas this run's overlay hash is
`bee055ec1ae6c0dc3cea12de393560b0974302b0cf559cca6dd3cfb55f924533`.
The source diff includes multiple unrelated retained changes, including
`init_game`, menu/profile code, type declarations and the recent BSS ownership
work. Therefore this comparison establishes sensitivity to the newer whole-TU
context but does **not** isolate a cause or credit any one source edit.

## Decision

This changes the next diagnostic decision: preserve the current-context output
as a separate beam candidate and compare it when testing historically supported
predecessor/compiler-state hypotheses. It does not justify another local
`load_character` spelling trial, a body repair, or recovery credit. The original
entry register mismatch remains unresolved. Continue with the higher-level
`init_game`/GCC context investigation; do not edit `load_character` to
compensate for an upstream state change.

## Artifacts

- Exact probe receipt: `current-baseline-receipt.json` (SHA-256
  `f115eb11be8b59591de41f2d76809f81946413a8760480e51e2026c8d80e1782`).
- Full comparison and object: `build/tu-context/game-main/research-load-character-next2-current-baseline-20260924/comparison.json`
  and `unit.o`; current overlay at the same directory's `overlay/src/main.c`.
- Full current comparison is 5,771,505 bytes. The older candidate receipt and
  context are `docs/attempts/tu-context/game-main/research-20260924-main-load-character-current.json`
  and `build/tu-context/game-main/research-20260924-main-load-character-current/`.
- Current focused strict evidence remains
  `docs/current/functions/main/load_character.json` and
  `docs/current/function-evidence/main/load_character.json`.

Next discriminating experiment: replay the same whole-TU baseline with the
specific historically supported `init_game` declaration/PHI-order variants
under investigation, then compare `load_character` effective identity,
peephole2 scratch findings, and exact-peer effects. Do not widen local source
search unless that context probe exposes a target-specific new mechanism.
