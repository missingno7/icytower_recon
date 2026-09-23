# `play` offset `+19` `.rdata` owner

## Outcome

The relocation at function offset `+19` is independently attributable to the
initializer for `play`'s local `speeds` array. No source or TU probe was needed:
the candidate and original read-only sections each contain the exact nine-int
initializer once, and the independently extracted original occurrence is at
`0x4d6c80`. This maps candidate `.rdata` addend `6272` (`0x1880`) to that
initializer by content, not by trusting the instruction's historical operand.
No maintained source, generated card, or recovery state was edited.

## Evidence

- Original `play` DWARF identifies `speeds` as `int [9]` with a frame-relative
  location (`DW_OP_fbreg: -180`): `docs/current/function-evidence/main/play.json`.
- The maintained source and the retained historical-order overlay declare
  `int speeds[9] = { 1500, 3000, 4500, 6000, 7500, 9000, 10500, 1800000,
  9000000 };` at line 4182.
- The candidate object's `.rdata` sequence at addend `0x1880` is the nine
  little-endian int values above; a complete scan finds it once in `.rdata`,
  at addend 6272.
- A complete scan of the original PE `.rdata` finds the same 36 bytes once,
  at VA `0x4d6c80` (section offset 11392). This location is independently
  recovered by searching for the initializer bytes; it agrees with the
  historical instruction's immediate but is not derived from that immediate.
- The object inventory records the `+19` `DIR32` relocation against `.rdata`
  with candidate addend 6272. The current function card's generic section-base
  warning does not express this per-literal content match.

Initializer bytes (36 bytes):

```text
dc050000 b80b0000 94110000 70170000 4c1d0000 28230000 04290000 40771b00 40548900
```

## Scope and exact-set context

No compilation or effective-output probe was run. The retained context is
`docs/attempts/tu-context/game-main/luna-play-summary-historical-order-split-20260924.json`,
which records 63 exact functions including `new_game` and `run_demo`. Since no
source was changed, that exact set is unaffected.

## Remaining limit

This establishes the owner/content of this one literal relocation. It does not
resolve other `.rdata` relocations, prove `play`'s body/layout, or make the
whole CU exact. The generated current card remains unchanged by design.
