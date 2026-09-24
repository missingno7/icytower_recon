# `game-profile/load_profile` context audit (2026-09-24)

## Strict result

The fresh FAST strict check is `FUNCTION_MATCH / BODY_MATCH_LAYOUT_BLOCKED`, 188/188 bytes, `SAME_CU_CALL_LAYOUT`, with no first difference and body edits forbidden. Its single raw transfer/layout diagnostic is the call at `+0x9d` to `generate_profile_checksum`: the candidate and historical resolved values are equal, while their unrelocated layout operands differ because the function entries occupy different section positions. This is not a function body mismatch or an interface failure.

The current interface card is `AGREE`: historical `Tprofile *(char *)`. `src/main.c:305` declares that exact spelling. `src/profile.c` has two `Tprofile_load *` prototypes and a `Tprofile_load *` definition; the local alias is `typedef Tprofile Tprofile_load`, so its canonical type is the same aggregate and the conflict report records no `load_profile` conflict. `get_profile_dir_for_profile` is now `size_t`-typed and `view_profile` is typed in the retained source context; neither creates a load-profile interface conflict.

## Isolated declaration probes

`tu_context_probe.py` compiled three isolated full-CU variants: retained-source control, both forward prototypes changed to `Tprofile *`, and both prototypes plus the definition changed to `Tprofile *`. All report 17 functions and preserve the same 11 strict `FUNCTION_MATCH` peers, including `load_profile`; there are no gained/lost matches. Each has the same `.text` SHA-256 `3581c9818f490d9665338ef0d5c352cc10dde84b523368263ee59127db303f77`, `.data` SHA-256 `5618f673f15838cd049186c9beebe1f671910e934be5c5156078c856217d4e9c`, `.rdata` SHA-256 `3c136d39e301b6daaab87af4e9ce8972cca4b66c81182998c1f69f4d5548c5d5`, empty `.bss`, same initialized-data comparison, same commons, and identical 494 code/data/rdata relocations. Each has 798 total object relocations; debug relocations/sections differ with source spelling, so no object/CU equality is claimed.

The three spellings therefore deduplicate to one code/data outcome. The direct spelling has no strict or codegen advantage. Keep the current definition/interface as-is and preserve the exact peers; route the observed `SAME_CU_CALL_LAYOUT` status through its existing layout-claim path if a receipt is needed, never through body editing.

## Artifacts

- Isolated source overlays: `overlays/profile-load-direct-Tprofile.c` and `overlays/profile-load-direct-Tprofile-all.c`.
- Probe object reports: `build/tu-context/game-profile/profile-load-current-control/comparison.json`, `.../profile-load-direct-Tprofile/comparison.json`, and `.../profile-load-direct-Tprofile-all/comparison.json`.
- Commands: `python tools/check_function.py game-profile load_profile`; `python tools/tu_context_probe.py game-profile src/profile.c <label> [--research-base <overlay>] --order current --no-prototypes --no-dumps --focus load_profile`.

No maintained source, generated current file, or recovery ledger was edited.
