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
