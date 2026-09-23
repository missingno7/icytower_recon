# `show_credits` isolated research (2026-09-23)

## Strict status

`DIFFER` (654 candidate bytes / 634 historical bytes); no candidate was promoted.
The current production-equivalent TU baseline (`--order current --no-prototypes`)
retains 63/82 exact functions, with no gains or losses. All probes used isolated
body overlays and left maintained source and recovery state unchanged.

## Useful evidence

- Current focused card: `docs/current/functions/main/show_credits.json`.
- Historical ledger: `docs/attempts/game-main/show_credits.jsonl` (14 attempts).
- Probe receipts: `docs/attempts/tu-context/game-main/luna-show-credits-*.json`.
- Full compile comparisons: `build/tu-context/game-main/luna-show-credits-*/comparison.json`.
- Candidate definitions: this directory (`cfg-explicit-order.c`, `cfg-goto.c`,
  `cfg-guarded-do.c`, and reconstructed ledger bodies 8 and 9).

The raw first differing byte at offset 26 is a `_screen` relocation whose
candidate and historical addresses differ because of data layout. Do not use it
as the body mismatch. The entry x87 sequence agrees structurally with evidence:
integer volume load, store to `double vol`, divide by the historical float
constant, and store to `double vol_step`. The later control-word save/restore
around conversion to the audio volume also appears in both instruction streams.
DWARF confirms `vol` and `vol_step` are `double`, `gc` is signed `int`, and
`logoBMP` is `BITMAP *`; the interface card says the function signature agrees.

The original CFG is clear in the verifier disassembly and source-line map. After
resetting `closeButtonClicked` and `cycle_count`, it tests Esc and
`cycle_count <= 149`; snapshots `gc`; runs focus/audio work; waits while
`gc == cycle_count`; exits on `closeButtonClicked`; decrements `vol`; then
returns to the Esc/count test. The current candidate's optimized loop emits an
additional Esc/count test after the wait/close-button path before decrementing
`vol`. On that exit path it can omit the decrement, which is locally dead. This
accounts for the actual CFG/code-size difference; relocation operands and
function target addresses also differ under current CU/data layout.

The historical direct call set is present. `draw_sprite` is an Allegro inline
expansion rather than a missing out-of-line call. The emission position is 48 in
both layouts and the predecessor is the historical `show_instructions`, which
is exact. Switching between current and historical definition order did not
change this function or any CU exact-function count.

## GCC pass probe

To locate the CFG change, I compiled the production-equivalent baseline, the
guarded-do form, and the explicit-goto form with unchanged `-O2 -g -mfpmath=387`
options plus diagnostic `-fdump-tree-all -fdump-rtl-expand`. Their emitted
object hashes exactly equal the corresponding ordinary TU probes, so the dump
flags did not change code generation. All pass dumps are retained in
`compiler-dumps/`.

The baseline has one Esc/count test in `003t.original` and still one in
`065t.tailr2`; the volume subtraction precedes it. At `066t.ch` (GCC loop header
copying), GCC clones that loop-header test into the entry path: the key and
cycle-count tests each go from one to two. The loop's latch test remains after
the volume subtraction. At `085t.sink`, the dump explicitly reports sinking
`vol_43 = vol_300 - vol_step_4`; the subtraction moves behind the duplicated
Esc/count test because its local result is dead on the exit path. Later passes
retain this order.

The guarded-do and nested-guarded-do forms already contain two tests in
`003t.original`, and `ch` adds no further copy. `sink` still moves their volume
subtraction after the post-body test. The explicit-goto form starts with one
test, follows the same `065t.tailr2` → `066t.ch` 1-to-2 transition as baseline,
and then the same sink movement. Its effective function identity is identical
to baseline. The two guarded-do forms also collapse to the same effective
function identity. Thus GCC canonicalizes both tested alternative source
structures to the same CH/Sink mechanism; no supported local form has yet
preserved the original single-test loop.

## Experiments and effective outcomes

Four isolated current probes (`baseline`, `cfg-explicit-order`, `goto-cfg`, and
`historical-order`) collapsed to one effective function identity
`7f11e57156718292`, 654 bytes, `DIFFER`. This confirms that `for (;;)` with an
explicit guard and a labeled `goto` do not escape GCC's current loop lowering.

The retained ledger contains 14 previous trials and 10 unique source bodies.
Replaying its two materially different loop forms in the current TU produced
627-byte and 624-byte outcomes (`DIFFER`), but those respectively move the
volume decrement before the work/audio and make the first loop iteration
unconditional, so neither models the observed original CFG. A guarded `do`
form produced a new 658-byte outcome (`DIFFER`) and still tests Esc/count before
the decrement. Effective identities for this batch are available through:

```text
python tools/effective_outcomes.py game-main show_credits --pattern "luna-show-credits-*.json"
```

## Remaining blocker

The local loop-spelling family has converged: source forms either collapse to
the 654-byte output, collapse to a 658-byte guarded-do output, or produce a
different but unsupported path order. DWARF settles local types and interface;
the historical emission predecessor and full definition order do not explain
the loop shape. The discriminating mechanism is now narrowed to the historical
GCC lowering trajectory: current one-test GIMPLE is duplicated at `ch`, then
`sink` reorders the dead local subtraction. A remaining useful probe must show
why the historical build avoided one of those steps, with the locked options and
source/control-flow evidence. Do not treat size proximity as recovery.
