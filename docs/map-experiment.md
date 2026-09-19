# map.c recovery

`reset_map`, `is_solid`, and `get_level` match complete 53-byte, 107-byte,
and 40-byte bodies at -O2. DWARF fixes the `Tfloor` layout at six integers
and `Tmap` at 32 floors plus its scroll offset.

`getFloorData` has the historical 107-byte extent and matches its signed
tile-row calculation, bounds checks, empty-row check, first edge, and output
order. Its right-edge `+17` selects `add` instead of the original `lea`.
`add_floor` now has a 599-byte source reconstruction. It shifts the 31 prior
floors, evolves the new room's `level` and periodic `level / 5` `sign` marker, applies the
250/2500/5-floor reset rules, computes replay-controlled floor widths, and
selects the new room's tile interval using the named `floor_size_modifiers`
table. Its historical body is 608 bytes and differs in
compiler block layout, so it remains `DIFFER` without exact credit. In the
shrinking-floor path, the source now preserves the original unconditional
`rand()` call and retains its result in `width` until the computed limit is
known; the remaining nine-byte gap begins at the `floor_shrink` register
allocation. This is a
partial-CU result only; see
`docs/experiments/game-map-O2.json` for the comparison record.
