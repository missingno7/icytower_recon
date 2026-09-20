# Recovery frontier

The recovered-game linker now produces an executable from the independently
compiled source candidates. It is not executed and link closure is not a
completion measure: `src/recovery.json` still records many
non-matching or missing bodies across the historical CUs, including main game
flow and presentation, replay, profile, menu, map, high-score, custom data,
and advertising paths. Future work must use the ledger's per-function status
and oracle verification, not link closure alone, to claim CU completion.

The main-CU ledger was refreshed from a current isolated `-O2` comparison:
collision modes, player input, frame blitting, string input, alert handling,
and `play` have source candidates and are `DIFFER`, rather than missing.

Run `python tools/next_frontier.py` to produce a ledger-derived P0--P5
worklist. Use `python tools/classify_diff.py <comparison.json>` before
changing a `DIFFER` body: the classifier distinguishes incomplete source,
same-CU call layout, relocation/literal layout, alignment, and unresolved
instruction-selection cases when the report provides enough evidence.
