# `extractHTTPResponse` entry-home RTL boundary (2026-09-24)

Research only. No maintained source, current card, recovery ledger, or accepted
body was changed.

## Result

The candidate's two register-parameter stack homes first appear in the available
RTL snapshots at `172r.ira`. At `168r.asmcons`, the formals are still pseudos
initialized from `%eax` and `%edx`; those insns have no stack destination. In
`172r.ira`, GCC has materialized them as frame stores. The indexed-output
candidate uses `-0x838(%ebp)` for `pHTTPData` and `-0x834(%ebp)` for
`iResponseBytesCount`, matching its emitted prologue. The historical executable
uses `-0x834(%ebp)` and `-0x82c(%ebp)`.

The stores remain at those offsets in `178r.pro_and_epilogue`; that pass emits
the frame allocation and prologue around the already materialized homes. Thus
the earliest candidate-side evidence places the choice at IRA/frame-slot
assignment, before prologue emission. The original executable has no compiler
RTL dump, so this does not identify which historical pass decision differed.

The dump pair covered maintained `src/httpget.c` and the indexed-output full-TU
overlay. Both compile with the locked TDM-2 GCC 4.4.1 build at `-O2`, with
`-fdump-rtl-all`, `-fdump-ipa-cgraph`, `-fdump-rtl-csa`, and
`-fdump-rtl-peephole2`. Their candidate homes are identical. The output-index
helper change therefore does not discriminate or cause this entry-home
difference.

## Source evidence and stop point

Historical DWARF gives the two parameters `%eax`/`%edx` only across the first
36 bytes of the function, then has no parameter location. It records the outer
locals `slaskbuf`, `linebuf`, `i`, and `pResponse` in the maintained declaration
order; both arrays retain their historical frame locations. It does not declare
the prologue homes as source-variable locations. The earlier helper-call
overlay also restored only the first home and lost two exact neighboring
functions. No alternate local declaration order, type, or lifetime is supported
by the source evidence, so there is no justified source edit or additional
variant from these observations.

## Artifacts

- Baseline RTL: `build/tu-context/game-httpget/httpget-stackcause-baseline-20260924/`
- Indexed-output RTL: `build/tu-context/game-httpget/httpget-stackcause-indexed-20260924/`
- Original prologue: `docs/attempts/research-20260923-httpget-context/extractHTTPResponse-original-disasm.txt`
- Candidate prologue offsets and prior DWARF assessment:
  `docs/attempts/research-20260924-httpget-output-index/followup-stack-homes.md`

Conclusion: the candidate-side home offsets are an IRA/frame-layout result;
historical pass causality and a source-backed discriminator remain unavailable.
