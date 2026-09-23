# Luna isolated research: game-menu family

Scope: diagnostic-only menu-family investigation. Maintained `src/`, generated current state, and `src/recovery.json` were not edited.

## Strict state

- Repository current progress records 208 `FUNCTION_MATCH` functions globally.
- `game-menu` CU comparison: 7/10 functions are `FUNCTION_MATCH`; `draw_menu`, `update_game_menu`, and `handle_menu` remain `DIFFER`.
- No exact candidate or production promotion was produced by this lane.

## Meaningful probe

Hypothesis: fixing the historical `update_game_menu` interface (`BITMAP *bmp`) instead of the maintained `void *bmp` could affect compiler output or neighboring caller bodies.

- Changed only the matching forward declaration and definition in isolated `menu-bitmap-interface.c`.
- Compiled the entire CU with the locked TDM GCC 4.4.1 command and compared against the original EXE.
- `BITMAP *` appeared in both generated interface entries, while `void *` was gone.
- `.text` hash stayed `199ab89acc4f063d1f6581ef1bb19e7bbca44260fb080b89d5a38e19a1c1d812`; `.data`/`.bss` stayed empty; all 10 candidate function byte sequences were unchanged from the current CU report. Exact CU function count stayed 7/10.
- The object identity changed because debug/interface metadata changed. Therefore the interface conflict is a real type-evidence defect, but correcting this pointer type does not address the current code-generation mismatches or alter the whole-TU emitted code in this CU.

## CFG evidence and current blockers

- `update_game_menu` has matching total direct-call count (14 original and candidate) but differing call topology: original has `is_down` twice and `is_right` three times; candidate has `is_down` three times and `is_right` twice. The 3rd candidate `is_down` call is emitted at `+0x234` with `ctrl`, while original’s late `is_down` at `+0x1d5` passes `&mp->ctrl`. The candidate’s extra `ctrl` call is in a different CFG path. Strict status stays `DIFFER`, first byte difference offset 103; signature-only probing leaves machine bytes unchanged.
- `handle_menu` has 20 original vs 21 candidate direct calls. `rest` is 2 vs 3, with candidate call sites at `+0x15b`, `+0x37d`, and `+0x3f4`; original sites are `+0x147` and `+0x38c`. Source has two textual `rest(2)` sites, so GCC duplicates a source-level call in its emitted CFG. Existing ledger has 16 FAST records and 11 unique body spellings; local body-only search has already explored substantially beyond the three-attempt production ceiling.
- `draw_menu`’s recorded decisive experiment already established a genuine candidate-only `DATAFILE *assets` local caused a 16-byte frame over-allocation. Removing it advanced the first mismatch from offset 8 to 16 and fixed the frame allocation; later expression and statement-order forms converged. Current blocker is the `bmp/m/mp` register allocation choice, not the old stack-frame issue. No need to repeat the recorded variants.
- A second `handle_menu` interface conflict remains on `view_profile` (`Tprofile` historically, opaque `void *` candidate), distinct from the tested `update_game_menu` correction.

## Additional CFG spelling probe

Rewrote the `is_down(ctrl) || is_down(&mp->ctrl)` branch as an explicit `if / else if`, duplicating only the evidenced increment-and-wrap block. With `--no-prototypes`, GCC produced the same 582-byte `update_game_menu` effective output as baseline (SHA-256 `71fba24f3aada86f3eef8e0e91ed4a1bbb96b3c2c6db40caa30b9dc6b9d1adfd`), still `DIFFER`, first difference offset 103, with zero gains/losses. This eliminates that source-shape hypothesis; more boolean spelling variants are not useful without new CFG evidence.

## Stop reason and next test

The pointer-type hypothesis is resolved: interface-only, no emitted code change. Repeating source spellings around that declaration has no information value. Next discriminating work should inspect the historical/candidate CFG around `update_game_menu` offsets 0x82–0x101 and 0x1cc–0x241 (especially why the late historical call receives `&mp->ctrl` while the candidate has another `ctrl` call), and inspect `handle_menu`’s two historical `rest` blocks against the candidate’s three CFG call sites. Any source-body exploration should remain in this isolated lane and use preserved semantic/call evidence, not byte-size targeting.

## Artifacts

- `docs/attempts/research-luna-menu-family/menu-bitmap-interface.c`
- `docs/attempts/research-luna-menu-family/iface-bitmap-v1-compile.stderr.txt`
- `docs/attempts/research-luna-menu-family/iface-bitmap-v1-comparison.json`
- `build/research-luna-menu-family/iface-bitmap-v1/unit.o`
- Existing source-history evidence: `docs/attempts/game-menu/{draw_menu,update_game_menu,handle_menu}.jsonl`
- Current focused evidence: `docs/current/functions/menu/{draw_menu,update_game_menu,handle_menu}.json`

## TU-context probes

Two target-body-preserving experiments tested whether preceding definitions affect `update_game_menu`:

1. `compiler_probe.py` baseline versus omitting `reset_menu`: target body hash stayed `9404056900fb2de60266dc528e3faef33031ea8604f737732dbda2b4353d393b`; generated code stayed 582 bytes with zero effective code-byte changes. Strict first mismatch remained offset 103.
2. Omitting `draw_menu` or `build_menu_string` changed two effective bytes; for the direct-callee `draw_menu` omission, `update_game_menu` changes the `%ecx` versus `%eax` register used for the `ctrl` null test at offsets 97/100. It remains 582 bytes and strict mismatch count worsens from 379 to 381. RTL text first diverges in early expansion passes. This shows an artificial callgraph/context sensitivity, but does not identify a historical source cause.
3. Captured a current-order production-equivalent baseline with `tu_context_probe --order current --no-prototypes`: 7 CU matches, no changed code in unchanged bodies, all 10 functions remain at their verified candidate offsets.
4. Replayed the retained `draw_menu` candidate body that removes the unsupported local through `tu_context_probe --no-prototypes`. `draw_menu` becomes 896 bytes (current baseline 956); exact count remains 7. The tool's raw `code_changed_with_unchanged_body` list names `update_game_menu` and `handle_menu`, but resolving same-CU call targets shows their effective function bytes are unchanged: only call displacements to the moved `reset_menu`/`draw_menu` targets differ because candidate offsets moved. Peephole scratch findings match baseline (`cx` for `update_game_menu`; `ax, dx, cx, bx` for `handle_menu`).

Interpretation: the retained `draw_menu` body variant shifts downstream layout but did not change downstream effective code in this probe. Omitting the direct callee definition does change two effective bytes in `update_game_menu`, while making its oracle mismatch worse. The omission is an artificial callgraph perturbation, not evidence that the historical TU omitted `draw_menu`. Do not manually retune downstream bodies based on these probes.

Artifacts:
- `docs/attempts/compiler-context/game-menu/update_game_menu.json`, `update_game_menu.jsonl`, and `update_game_menu-rtl.json`
- `docs/attempts/tu-context/game-menu/luna_menu_current_noproto_baseline.json` and `luna_menu_drawbody_context_v1.json`
- `build/tu-context/game-menu/luna_menu_drawbody_context_v1/`
- `docs/attempts/research-luna-menu-family/draw_menu-recorded-candidate.c`
- `docs/attempts/research-luna-menu-family/update_game_menu-nested-down.c` and `docs/attempts/tu-context/game-menu/luna_menu_nested_down_v2.json`
