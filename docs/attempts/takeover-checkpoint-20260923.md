# Reconstruction checkpoint — 2026-09-23

## Verified baseline

- Checkout: `main` at `dc62a0ad25e16566fd142c59fc44b7950bdd9b48` when work began. Twenty-one `docs/experiments/*.json` files were already modified; none was overwritten intentionally or staged here.
- Oracle fixture SHA-256: `7570c6b0c7cddf6180d7c421bdc7d7bc1486c47a6d62cc6fde90670f62d4388d`. TDM-2 lock SHA-256: `dfde67e60d23238d9489b5898bd3ebf758d6ebb871721cc16804b49c93bd9b22`; pinned `gcc.exe`: `13ce95bd196a45f232c99acca1fd1ef81c0db3d5937349e4beafb8724a006986`.
- `python tools/refresh_recovery.py --verify-all` freshly compiled and compared all 25 game-tree CUs. It reproduced 204 `FUNCTION_MATCH`, 3 `CODEGEN_SIMILAR`, 46 `DIFFER`, and 33,186/116,113 strictly verified game-function bytes. `game-main` was 58/82. `python tools/check_function.py game-timer fps_counter` reproduced a 45/45-byte strict function match with zero relocation mismatches. `timer.c` has three exact functions and complete 152-byte text, but `object_match` is false.
- `python tools/audit.py` passed fixture, census, toolchain, upstream, and generated-ledger invariants. The ordinary source link succeeded but included two known synthetic gameplay replacements; it does not establish recovery. `python tools/recovered_game_link.py --diagnostic` now produces a separately named, explicitly incomplete executable. No full-EXE equality has been claimed or tested.

## Fresh main.c context experiment

Command: `python tools/tu_context_probe.py game-main src/main.c takeover-20260923 --order historical --body draw_frame=docs/attempts/game-main/draw_frame-merged.c --body play=docs/attempts/game-main/play-merged.c --focus draw_frame --focus play --focus run_demo --focus stopGameMusic --no-dumps`.

Record: `docs/attempts/tu-context/game-main/takeover-20260923.json`; object SHA-256 `ebc6943ca2296924926c84bb912da7d97fb5123db4e716c84ef90c125556320b` (the overlay source and object identities are in the record). The generated order puts `draw_frame` at historical position 41, `play` at 78, then `run_demo` at 79; 79/82 functions have their historical predecessor. The probe gains `draw_progress_bar`, `log2file`, and `open_web_browser`, loses `run_demo`, and changes code in many untouched bodies. It is not a promotable TU state. `draw_frame` is 8,506/8,518 bytes and `play` is 16,863/17,420; all observed historical direct call edges are present, but neither body matches. The first differences at offset 8 are stack allocations (draw: `0x1dc` versus `0x1cc`; play: `0x9fc` versus `0xa3c`), while aligned instruction comparison shows broader control-flow/code-generation differences. Do not target the peephole cursor or `run_demo` directly.

## Corrective changes and remaining work

- `function_data_refs.py` now uses actual PE section ranges. It finds previously omitted `play` globals at `0x4bc020` (`hasFocus`), `0x4bc024` (`lastFocus`), `0x4bc0c0` (`hints`), `0x4bc174` (`checkMusicVoiceID`), and `0x4bc17c` (`start_speeds`). It distinguishes an empty string at `0x4d4bb3`, known objects, null pointers, and unknown references.
- `unused_locals.py` ignores candidate comments and strings, preserves distinct DWARF locals, and reports location attributes. Its output is an investigation lead, not behavioral proof. `play` has nine unmentioned DWARF locals in the current retained candidate; several have no surviving location attribute.
- Gross source deficits now outrank a first stack-frame difference in `classify_diff.py`, so production `draw_frame` and `play` are routed as `SOURCE_INCOMPLETE`. Their body candidates remain separate. The recovered-game link/stage path refuses incomplete source; diagnostic linking remains available.
- A bounded `change_profile` task was opened and aborted without editing source. Original offset 13 jumps to shared `select_profile` setup at offset 76 using `eax`; current code emits a null-path `xor edx,edx` at offset 192 and a jump back. The same mismatch remains in historical TU order. Failure is recorded in `docs/attempts/game-main/change_profile.jsonl`. Do not repeat cosmetic condition rewrites without a new caller/declaration hypothesis.
- The active `main_menu_callback` is a strong but incomplete candidate containing a known synthetic Welcome back text slice; the source itself flags the missing original rank/version presentation. It is recorded separately from the two wholesale synthetic bodies in the provenance manifest.
- The current main dependency task is to recover the missing source/control-flow shape in the retained `draw_frame` and `play` bodies, verify all instructions and data references, then test them together in historical TU context. `draw_frame`'s early floor/stripe region and `play`'s game-over/result blocks have the largest localized differences. Use `tools/line_budget.py` only as a locator; exact comparison and relocation checks remain the acceptance gate.

## Resume commands

`python tools/audit.py`; `python -m unittest discover -s tools -p test_recovery_diagnostics.py -v`; `python tools/recovered_game_link.py --diagnostic`; and the combined probe command above. Re-run `python tools/refresh_recovery.py --verify-all` after meaningful source or verifier changes so the current ledger and link receipt are fresh.

## Later work in this run

After committing the diagnostic corrections as `08dba07f`, the original menu rank/version strings, four rank draws, cursor selection, two fixed-point head bitmap planes, and face-reset ordering were reconstructed in a separate `main_menu_callback` body. The latest historical-order combined probe compiles it to 3,775/3,741 bytes with every original direct call edge present; the original frame allocation and initial instructions now align through offset 72, but it is still `DIFFER`, and the unit still regresses `run_demo`. See `docs/attempts/game-main/main-menu-rank-20260923.md` and the adjacent TU probe records. Production source and recovery statuses remain unchanged by this experiment.
