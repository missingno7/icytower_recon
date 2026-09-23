# `tc_posts`/`rejump` source-order probe: instruction analysis

## Result

The isolated reversal changes one source expression from

```c
sum += r->tc_posts * 127 + r->rejump * 13;
```

to

```c
sum += r->rejump * 13 + r->tc_posts * 127;
```

The locked GCC 4.4.1 candidate then loads and computes `tc_posts` before
`rejump`, matching the historical PE's field order. This is the expected
right-subexpression-first lowering of the commutative `+`: the control emits
`rejump` then `tc_posts`, while the reversed source emits `tc_posts` then
`rejump`. It provides a concrete source-order hypothesis for this pair. The
machine code cannot prove original C operand order, since both operands are
side-effect-free and their mathematical sum is commutative.

## Instruction and CFG effects

In the control candidate, the relevant sequence at object offsets `0x1a1` to
`0x1bd` loads `[r+0xa0]` (`rejump`), forms `13*rejump`, then loads
`[r+0xd4]` (`tc_posts`) and forms `127*tc_posts`. It combines the terms with
two `lea` instructions. In the reversed candidate, offsets `0x1a1` to `0x1bc`
load `[r+0xd4]` first, then `[r+0xa0]`, combine with `add`, and accumulate
with one `lea`. The arithmetic result expression is unchanged modulo signed
overflow behavior; the candidate instruction order now agrees with the PE's
`0x41bb4f` through `0x41bb6c` sequence.

This smaller expression lowering also changes later register-allocation/code
selection: the control has a three-byte `lea esi,[esi+0]` at object offset
`0x22d`; the reversed candidate has no corresponding instruction. The
subsequent float-loop instructions and branch structure are otherwise the
same after accounting for shifted offsets. The reversed object is four bytes
shorter overall, one byte from the expression sequence and three from this
redundant `lea`. This explains the shorter candidate without implying that
the later code is a strict historical match.

Both variants retain the same six-branch control-flow shape: five loops and
the conditional replay-data entry/exit. Source order changes the instruction
schedule and one redundant instruction, not loop bounds, branches, memory
owners, relocations, or DWARF locals. Original DWARF still identifies only
`r`, `i`, and `sum`, with the same inline `hash` instance; it supplies no
source expression tree or grouping evidence.

## Interpretation and stopping point

The field-load order is a concrete, historically aligned result for the
reversed source operand order. It is consistent with a source expression
whose left term is `rejump` and right term is `tc_posts`, given this GCC's
observed lowering. It does not establish source grouping or explain the
remaining body-wide mismatch. The diagnostic raw-byte count remains
non-credit: the variant is still `DIFFER` (671 bytes versus 676), with the
first mismatch at offset 21. No branch, neighbor-function, interface, or
relocation evidence supports a wider compiler-context cause. Since another
parenthesization of these same pure integer terms would not test a distinct
causal hypothesis, this line of probing stops here.

Evidence: original PE `assets/icytower15.exe`, `_calc_replay_checksum` at
`0x41bac4`; candidate objects and strict reports under
`build/tu-context/game-replay/luna-checksum-fullctx-{control,swap-posts}-20260924/`;
source variants `control.c` and `swap-posts.c` in this directory. No
maintained files were edited.
