# `calc_replay_checksum` earliest divergence under GCC (2026-09-24)

Research-only investigation on the owner-aligned `game-replay` TU using the
locked TDM-2 GCC 4.4.1 `-O2 -mfpmath=387` build. No maintained source, current
state, or recovery ledger was changed.

## Earliest byte and RTL evidence

For the accepted `swap-posts` overlay, the first differing byte is function
offset `+21` (PE VA `0x41bad9`): historical `lea 0x11(%edx,%eax),%ecx`
encodes ModRM `0x4c`; candidate `lea 0x11(%edx,%eax),%edx` encodes `0x54`.
The arithmetic and field-load sequence match through this instruction. The
historical code keeps the first accumulator term in ECX, then loads
`no_combo_top_floor` into EDX. GCC keeps the accumulator in EDX and loads the
field into ECX. This is a register-allocation mismatch, not another arithmetic
or `tc_posts`/`rejump` operand-order mismatch.

Dump-enabled recompiles of the exact `control` and `swap-posts` owner-aligned
sources were byte-neutral: each object hash matched its existing no-dump
object. In both focused `calc_replay_checksum` dumps, the accumulator result
is virtual register 108 through `168r.asmcons`. It first appears assigned to
hard register DX in `172r.ira`, and stays DX in `174r.postreload`, `181r.csa`,
and `182r.peephole2`. The `swap-posts` change is in a later expression; it
does not alter this first allocation. The original EXE has no RTL dump, so IRA
is the earliest candidate pass where the divergence can be located, not proof
of the historical compiler's internal choice.

The original arithmetic around the first mismatch confirms the established
source-supported accumulator: `(biggest_lost_combo * 17 + 17) +
no_combo_top_floor * 127`. Its machine sequence computes `17 * biggest + 17`
into ECX, computes `127 * no_combo` into EAX, then adds EAX to ECX. The
candidate computes the same value and order into EDX. This local fact does
not explain the remaining body-wide mismatch.

## Bounded source-shape check

One source-backed shape was checked in a scratch full-TU overlay, preserving
the other checksum body and every exact peer: split the established
accumulator into `sum = biggest * 17 + 17;` followed by
`sum += no_combo * 127;`. It remained `DIFFER` at 671 versus 676 bytes; first
mismatch moved earlier to `+13`, and 374 bytes differed. It does not support
the split-assignment hypothesis. No broader source-shape batch is justified
by this result.

The source-backed operand-order lead therefore reaches a concrete stopping
point: the postswap matches field-load order but GCC's IRA selects a different
destination register for the first accumulator. No original source-expression
or compiler dump evidence identifies a safe source change that will reproduce
ECX while preserving the rest of the body.

## Artifacts

- Pass dumps: `build/tu-context/game-replay/luna-checksum-rtl-cause-20260924/`
- Strict split-shape comparison: `build/tu-context/game-replay/luna-checksum-rtl-cause-20260924/split-initial-accumulation/`
- Starting source variants and strict comparison: `docs/attempts/research-20260924-checksum-full-context/`
