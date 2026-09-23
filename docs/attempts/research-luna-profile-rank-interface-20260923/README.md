# Historical rank helper aggregate interface (2026-09-23)

## Finding

The historical `get_rank_id`, `get_rank`, and `set_next_rank_message` interfaces all use `Tprofile *`. The historical CU's `Tprofile` is the complete 1,360-byte record, not the candidate's 140-byte `Tprofile_rank` prefix view. Pointer ABI width happens to be the same, but the aggregate contract is not interchangeable.

The DWARF chain is independently visible in `evidence/census/dwarf-dies.jsonl`:

- `get_rank_id` definition DIE 196878, formal parameter DIE 196899; its type is `Tprofile *` (type DIE 196386). Its source declaration is line 160.
- `get_rank` definition DIE 196918, formal parameter DIE 196939; its type is `Tprofile *` (type DIE 196386). Its source declaration is line 175.
- `set_next_rank_message` parameter DIE 197047 is also `Tprofile *` (type DIE 196386).
- In this CU, typedef DIE 196228 `Tprofile` names struct DIE 195418, whose `DW_AT_byte_size` is 1360.

The original machine code dereferences that parameter at offsets `0x4c`, `0x50`, `0x58`, and `0x88`. The full type graph and `include/recovered/Tprofile.h` independently identify those as `best_floor` (+76), `best_combo` (+80), `no_combo_top_floor` (+88), and `ccc[0]` (+136). The source's current `Tprofile_rank` labels these same offsets `score`, `combo`, `ccc`, and `no_combo_lost`; those semantic names do not make the 140-byte view the historical parameter type. No fake 1,360-byte aggregate is warranted.

## Isolated full-CU test

The source-supported hypothesis—use historical `Tprofile *` signatures and the canonical fields at the byte offsets proved by DWARF—was tested in a full isolated `game-profile` TU overlay. The retained candidate and diagnostic receipt are:

- `docs/attempts/research-20260923-profile-view/profile-typed-rank-v2.c`
- `docs/attempts/tu-context/game-profile/luna-profile-view-typed-rank-v2-20260923.json`
- `build/tu-context/game-profile/luna-profile-view-typed-rank-v2-20260923/comparison.json`

The probe compiled with locked TDM-2 `-O2`; all 11 baseline exact functions remained exact, with no losses or gains. `get_rank_id` (75 bytes), `get_rank` (82 bytes), and `set_next_rank_message` (431 bytes) remained `FUNCTION_MATCH`. The overlay's DWARF aux signatures use `Tprofile *`. This validates an emission-preserving, historically supported source rewrite for these helpers. It does not claim whole-CU equality: other functions remain DIFFER, `whole_text_contribution_equal` is false, and `view_profile` remains DIFFER at 2160/2249 bytes.

The full-CU allocated contribution fingerprint was also unchanged in the prior audit: `.data` 416 bytes / 27 relocations, empty `.bss`, `.rdata` 1,860 bytes, and all 452 allocated-section relocations unchanged. Details are preserved in `docs/attempts/research-20260923-profile-view/README.md`.

## Acceptance boundary

Current cards `docs/current/interfaces/get_rank.json` and `get_rank_id.json` report `TYPE_LAYOUT_CONFLICT`: historical `Tprofile` is 1,360 bytes, candidate `Tprofile_rank` is 140 bytes, and the generated member comparison finds 37 differences. The candidate signatures and rank-view expressions remain in `src/profile.c`; no maintained file or recovery state was changed here. The old isolated test provides a concrete interface/type repair candidate, but it is diagnostic only and does not override the current interface gate. Preserve the complete `Tprofile` type and apply the four canonical member expressions if the cross-CU interface path is reviewed.

No additional compile was run: the same exact source hypothesis already has a full-CU isolated receipt, and a second identical overlay would add no evidence. This note re-audits that result against the actual original DIE graph and both current interface cards.
