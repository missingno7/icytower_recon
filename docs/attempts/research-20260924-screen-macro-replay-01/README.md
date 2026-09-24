# Screen-size macro replay in unresolved code

Isolated research on 2026-09-24. `src/`, `tools/`, the verified ledger, and generated current state were not edited. The strict starting state is 64/82 exact functions in `game-main`; current `src/recovery.json` has 41 DIFFER, 211 FUNCTION_MATCH, and one CODEGEN_SIMILAR overall.

## Search and historical support

The locked Allegro header defines `SCREEN_W` and `SCREEN_H` as `(gfx_driver ? gfx_driver->w/h : 0)` in `third_party/allegro-4.4.1/include/allegro/gfx.h:304-305`.

A repository search found these relevant dimensions:

| Site | Status / original CFG evidence | Decision |
| --- | --- | --- |
| `force_create_profile`, `src/main.c:6428,6431` | DIFFER. Original `0x40d460` checks `gfx_driver` and routes null to `0x40da0b`, where zero dimensions are supplied before the `create_bitmap` call. Original `0x40d485` does the same for the initial blit (`0x40da04` zeroes dimensions before its call). Later original sequences `0x40d7c5..0x40d812` and `0x40d87b..0x40d8b6` again test `gfx_driver`; null branches `0x40d904` and `0x40d8fc` feed the calls with zero dimensions. Thus the two remaining direct dimension pairs in the reconstructed body have clear source-level support for macro expressions. | Probed both remaining pairs together. |
| `main.c:5978` ad-hit check | The `gfx_driver && ...` short-circuit requires a non-null driver before reading `h`; no null-to-zero arguments. | Not a screen macro site. |
| `line_alert`, `main.c:1756-1758` | Already initializes dimensions to zero and reads members only inside `if (gfx_driver)`; current function is FUNCTION_MATCH. | No edit/probe. |
| `my_alert`, `main.c:1792-1793` | DIFFER; source already spells each macro expansion literally as `gfx_driver ? gfx_driver->w/h : 0`. Original `0x40ce9a` tests the pointer, takes a null branch, and reaches the same `rectfill` call with zero width and height. | Deduplicated: replacing this ternary with the macro changes no preprocessed expression. |
| `replay_selector`, `replay.c:907-908,943-944` | DIFFER; source already spells the same null-to-zero ternaries. | Deduplicated: no distinct macro candidate to compile. |

Captured focused original disassembly is in `original-force-create-prefix.txt`, `original-force-create-tail.txt`, `original-force-blit-cfg.txt`, `original-force-rectfill-cfg.txt`, and `original-my-alert-screen-call.txt`.

## Full-TU probe

`probe.py` changes only the two remaining `force_create_profile` argument pairs from direct member accesses to `SCREEN_W, SCREEN_H`; the current source already uses those macros for the first two pairs. The locked TDM-GCC 4.4.1 full `game-main` overlay build completed, with pass dumps and strict object comparison. Candidate source SHA-256: `7b233b8989895730e00b83066fad379034cd89cb5d01a03bfceb007372cc63fe`. Exact source-only diff: `source.diff`.

Strict outcome (`receipt.json`): 64/82 exact before and after; no exact gains or losses. `force_create_profile` remains DIFFER and is 1546 bytes versus the 1538-byte original (the prior macro baseline is 1490 bytes). `draw_results`, `log2file`, `testWindowResolution`, `new_game`, `uninit_game`, and `check_beta_tester` stay exact and retain their recorded peephole scratch sequences. The candidate adds no whole-TU exact-function result. That size result is not a behavioral reason to reject the source correction: the original CFG proves both calls use zero dimensions when `gfx_driver` is null, and the locked Allegro macros express exactly that behavior. No non-size-based blocker to retaining this source correction was found.

A complete retained body and minimal `TU_CONTEXT` spec are available as `force_create_profile_screen_macro_replay.c` and `tu-context-spec.json`. `prepare_transaction.py` ran `build_text`; `tu-context-reproduction.json` records byte-for-byte equality with the isolated overlay, matching SHA-256 values, one retained body, historical order, and no header edits. The correction was promoted as `force_create_profile_remaining_screen_macros_20260924`: the fresh strict check preserved all 64 exact functions, then function tests, diagnostic link, and global audit passed. `force_create_profile` itself remains DIFFER. Isolated object and compiler dumps: `build/tu-context/game-main/research-20260924-screen-macro-replay-01/`.

