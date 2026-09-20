# map.c recovery

`reset_map`, `is_solid`, and `get_level` match complete 53-byte, 107-byte,
and 40-byte bodies at -O2. DWARF fixes the `Tfloor` layout at six integers
and `Tmap` at 32 floors plus its scroll offset.

`getFloorData` has the historical 107-byte extent and preserves its signed
tile-row calculation, bounds checks, empty-row check, both edges, and output
order. It remains `DIFFER`: the original computes the right edge with
`lea ebx, [eax + 17]` before loading the `fx2` pointer, while the current
source-equivalent candidate emits `add eax, 17` and uses `ebx` for that
pointer. Historical DWARF lists only `y` as a local, and both a direct
shifted-plus-17 expression and a temporary-right-edge probe produced the same
candidate, so neither artificial form is retained.
`add_floor` now has a 606-byte source reconstruction. It shifts the 31 prior
floors, evolves the new room's `level` and periodic `level / 5` `sign` marker, applies the
250/2500/5-floor reset rules, computes replay-controlled floor widths, and
selects the new room's tile interval using the named `floor_size_modifiers`
table. Its historical body is 608 bytes and differs in
compiler block layout, so it remains `DIFFER` without exact credit. In the
shrinking-floor path, the source now preserves the original unconditional
`rand()` call and retains its result in `width` until the computed limit is
known. Its guard now compares the float limit before integer conversion, which
matches the original x87 sequence. The historical lexical `int max_w` local is
also restored for the bounded-width branch, preserving the oracle's debug
scope without changing the 606-byte candidate body. The high-level shrink
ladder now uses the oracle's visible default-and-refine order: width 5, then
width 4, then the 3/2 terminal selection. The first remaining difference is at
function offset 297 (`0x416905`): the candidate loads `floor_shrink` into
`edi`, while the original loads it into `esi`. The later shrink-width blocks
then use a different but equivalent layout, so the 606-byte candidate cannot
receive exact credit against the 608-byte historical body. A
`-fno-reorder-blocks` probe changed earlier matched code and was rejected.
This is a partial-CU result only; see
`docs/experiments/game-map-O2.json` for the comparison record.
