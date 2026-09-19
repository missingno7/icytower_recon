# map.c recovery

`reset_map`, `is_solid`, and `get_level` match complete 53-byte, 107-byte,
and 40-byte bodies at -O2. DWARF fixes the `Tfloor` layout at six integers
and `Tmap` at 32 floors plus its scroll offset.

`getFloorData` has the historical 107-byte extent and matches its signed
tile-row calculation, bounds checks, empty-row check, first edge, and output
order. Its right-edge `+17` selects `add` instead of the original `lea`.
`add_floor` remains missing. This is a partial-CU result only; see
`docs/experiments/game-map-O2.json` for the comparison record.
