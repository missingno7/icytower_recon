# Partial `game_data.c` experiment

`add_jump_sequence`, `add_combo`, `destroy_game_data`, and `create_game_data`
are byte-exact at `-O2`. The appenders preserve the recovered short-circuit
conditions and field-write order. The allocator/initializer reconstruction uses
the recovered `Tgame_data` layout, its five-element paired-counter loop, and
its chained assignments. The compiler, object identity, local compiler inputs,
function boundaries, and relocations are recorded in
`build/experiments/tdm-2/game-game-data/O2`.

`getGameDataXML` is reconstructed from the original serializer's fixed replay
layout and XML literals. It allocates the original 128000-byte output buffer,
formats the player, game, claimed and actual result blocks, and retains both
mutually exclusive output paths: `cmdline.tiny` emits only the result verdict,
whereas the normal path emits the optional combos, jumps, keys, and sample-data
blocks selected by the corresponding command-line flags. The actual level rows
remain gated by the claimed replay counters, including the original off-by-one
claimed-counter layout.

Its local serializer buffers use the original DWARF bounds: `playerTag` and
`keysTag` are 256 bytes, `gameTag` is 512 bytes, `claimTag` and `actualTag`
are 1024 bytes, and the combo, jump, and sample-data buffers are each 5120
bytes. Those bounds restore the historical 0x485c stack allocation. DWARF also
confirms `misses` as an `int` local scoped only to the tiny-output branch; the
source preserves that lexical scope. The resulting 1853-byte candidate still
differs from the 1855-byte original in formatter and branch scheduling.
