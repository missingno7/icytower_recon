# Recovery frontier

The recovered-game linker currently reaches only `draw_frame` and `init_game`,
but this is not a completion measure. `src/recovery.json` still records many
non-matching or missing bodies across the historical CUs, including main game
flow and presentation, replay, profile, menu, map, high-score, custom data,
and advertising paths. Future work must use the ledger's per-function status
and oracle verification, not link closure alone, to claim CU completion.
