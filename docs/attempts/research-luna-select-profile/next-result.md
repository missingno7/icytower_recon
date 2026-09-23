# `select_profile` restored-CFG follow-up

## Finding

The scoped 2991-byte candidate contains the original UI paths, separate buffers with non-overlapping DWARF scopes, profile helper calls, and bitmap callback paths. A direct-call audit found one API mismatch: the overlay used `textprintf_ex` for the `Enter profile name:` line, while the executable calls `textout_ex`. The oracle switch dispatcher is also distinct: it subtracts scan code `0x3b`, bounds to `0x1a`, and jumps through the table at `0x41b009`.

## Isolated full-TU outcomes

- `textout_ex_only`: 2991/3070 bytes; first mismatch +12. The API correction does not change byte count.
- `switch_and_textout_ex`: 2998/3070 bytes; first mismatch +12. The source-backed switch plus API correction is 7 bytes larger than the scoped candidate and remains 72 bytes short.
- Both strict reports retain the exact same 11 `FUNCTION_MATCH` neighbors: `hash2`, `generate_profile_checksum`, `get_rank_id`, `get_rank`, `set_next_rank_message`, `profile_data_page_advanced`, `profile_data_page_basic`, `profile_data_page_extra`, `save_profile`, `load_profile`, and `delete_profile`. Each reports all 17 CU functions, initialized data, common/BSS allocations, and relocations. Neither is a CU or object match.

## Residual

At +12 the oracle saves `ctrl` from `[ebp+0x14]` into `ESI` (`8b 75 14`); the candidate loads the font global into `EAX` (`a1 ...`). The call and CFG differences identified here do not explain that register schedule or the remaining 72 bytes. No further source-backed missing block/interface difference was identified in this audit.

## Artifacts

- `adaptive-call-cfg-results.json`: evidence and compact results.
- `adaptive-textout-result.json`, `adaptive-switch-textout-result.json`: strict summaries.
- `overlay/textout_ex_only.*`, `overlay/switch_and_textout_ex.*`: isolated body/full-TU overlays.
- `build/textout_ex_only/`, `build/switch_and_textout_ex/`: strict reports, provenance, object files, compiler logs, DWARF and dependency artifacts.
- Earlier full history: `README.md`, `batch-summary.json`, `batch-results.json`, and `build/historical-select_profile.asm`.

No maintained source, cards, recovery state, ledger, generated state, or other agent directory was changed.
