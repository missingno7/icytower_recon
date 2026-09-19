# particle.c recovery

All three historical particle functions match at -O2, including the complete
304-byte logical text contribution, padding and independently resolved calls
to `new_rand`. There are no initialized data or common allocations. This is
not object or debug-metadata equality.

DWARF establishes a 24-byte particle: intensity, x/y 16.16 fixed positions,
x/y fixed velocities, and color. The reset routine clears only intensity for
512 entries. The allocator finds the first vacant slot and returns zero if
none is available, which intentionally collides with a valid first slot.

The recovered vertical random velocity divides its centered 16.16 value by
50. A candidate using 100 produced the same body size but differed at the
magic signed-division shift, so it was rejected. The update routine preserves
the fixed gravity increment and the one-in-five color update.

Particle and the recovered exact `new_rand` body are included in the separate
synthetic custom-audio PE. It remains outside the natural integration layout
experiment because main.c is still partial. See
`docs/experiments/game-particle-O2.json` for full verification records.
