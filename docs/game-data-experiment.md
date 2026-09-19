# Partial `game_data.c` experiment

`destroy_game_data` and `create_game_data` are byte-exact at `-O2`.
The allocator/initializer reconstruction uses the recovered `Tgame_data`
layout, its five-element paired-counter loop, and its chained assignments. The
compiler, object identity, local compiler inputs, function boundaries, and
relocations are recorded in `build/experiments/tdm-2/game-game-data/O2`.

The remaining functions are retained as explicit unknowns in `src/game_data.c`:
`add_jump_sequence`, `add_combo`, and `getGameDataXML`.
Their original text is used only as an oracle for the comparison report.
