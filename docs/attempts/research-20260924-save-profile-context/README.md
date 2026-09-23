# save_profile layout blocker

## Current evidence

The focused card reports `save_profile` as `FUNCTION_MATCH`, `BODY_MATCH_LAYOUT_BLOCKED`, 1073/1073 bytes. All bytes match after resolving same-CU call targets; this is not a CU or object match. The function's historical and candidate emission positions are both 12, with `view_profile` as the predecessor in both. `view_profile` is still `DIFFER`; the historical exact prefix ends earlier. The immediately following `load_profile` matches. The CU has 11 `FUNCTION_MATCH` functions out of 17.

The five same-CU calls in `save_profile` target `generate_profile_checksum` and the four profile page builders. Their raw relative displacements differ with peer placement, but each independently resolves to the same historical target. No relocation mismatch, literal diagnostic, parameter/local type mismatch, or function byte mismatch is recorded for `save_profile`.

DWARF names the parameter `Tprofile *`; the source uses the alias `Tprofile_create *` for the same typedef. The original local inventory has `file[1024]`, `time_t now`, `struct tm *my_time`, integer date fields and `i`, and four output pointers, which agree with the source-level roles. The source line number differs from the historical line table because the reconstructed file has additional declarations/comments; function order and emitted predecessor agree.

## Retained negatives and isolated declaration probe

The five retained body attempts contain two unique bodies. The older body changed several output-label spaces and the padding argument to `profile_data_page_general`; it remained `DIFFER` at offset 290 with a literal-content difference. The current body is the other unique body and retains the seven-space padding argument. Repeated FAST records for that body remain `DIFFER` only because raw same-CU call layout is compared before target resolution. One attempt failed to compile because of unrelated `font`, `screen`, and `gfx_driver` conflicts.

The helper declaration is a concrete source difference: the current local prototype uses `unsigned int` for `get_profile_dir_for_profile`'s length, while its historical interface card records `size_t`. An isolated copy changing only that spelling to `size_t` compiled with locked TDM-GCC. Receipt `docs/attempts/tu-context/game-profile/research-20260924-save-profile-size_t.json` reports `save_profile` still `FUNCTION_MATCH`, 11 exact functions before and after, no gains/losses, and no code changes in unchanged bodies. On this 32-bit target the spelling does not distinguish the layout issue.

Prior `sp-*` TU-order experiments also retained `save_profile` at position 12 with the same nonmatching `view_profile` predecessor; variants lost `generate_profile_checksum` and gained no exact functions. They provide no source-order repair.

## Stop point

No remaining source-backed fact predicts a change to `save_profile`'s resolved body. Its five internal call displacements depend on the current peer layout, while the incoming predecessor `view_profile` is still different. Fixing peer bodies or moving functions is outside this function's protected scope and would alter CU context without evidence that it changes the resolved calls. A fresh strict CU after upstream peer recovery, or original object/relocation records, is needed to establish complete layout. Keep status unchanged; do not claim CU/object equality.

## Artifacts

- Focused card: `docs/current/functions/profile/save_profile.json`
- Detailed function evidence: `docs/current/function-evidence/profile/save_profile.json`
- Strict CU report: `docs/current/reports/game-profile.json`
- Retained function attempts: `docs/attempts/game-profile/save_profile.jsonl`
- Isolated declaration source and receipt: this directory and `docs/attempts/tu-context/game-profile/research-20260924-save-profile-size_t.json`

No maintained source, ledger, generated status, or exact function was changed.
