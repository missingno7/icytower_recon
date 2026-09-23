# Replay context research (2026-09-23)

This is a read-only research lane. It does not change `src/`, generated current state, `src/recovery.json`, accepted bodies, or neighboring repositories. New files are confined to this directory; compiler products are under the ignored `build/tu-context/game-replay/replayctx-cs-late-20260923/` directory.

## Strict result

`load_replay` remains `DIFFER` / `SOURCE_DIFFER`: candidate 1148 bytes vs original 1136, first raw difference at function offset `0xab` (`0x41ce93`), with 39 relocations. The isolated full CU remains 6/15 `FUNCTION_MATCH`; complete `.text`, object, and CU equality are false. No candidate is ready for promotion.

## New evidence: declaration-line hypothesis eliminated

The original DWARF gives `load_replay` locals in this declaration order: `pf` line 266, `r_temp` and `r` line 267, `i` line 268, `sum` line 269, and `cs` line 346. Maintained code declared `cs` alongside the other locals at function entry. I moved only `int cs;` to immediately before its first assignment, matching its historical declaration location while leaving all executable statements unchanged.

The runtime function output is byte-identical to the baseline (`load_replay` function-byte SHA-256 `a783610b14bf303072729751155d46e2765307ffd82119dcc590078ae0ca5b96`, size 1148, same first difference, same relocation count and 6/15 CU strict count). The object hash differs because the source/debug metadata changed. This eliminates local declaration placement as the cause of the code mismatch.

## Existing replay hypotheses retained

- `docs/attempts/research-luna-replay-load/README.md` and `probe-summary.json`: changing `pf` from `void *` to original-DWARF `PACKFILE *` leaves all emitted `load_replay` bytes identical; historical definition order and moves that do not alter cgraph order also leave the bytes identical. Current candidate peephole2 dump shows the scratch addition; original machine code uses different register roles through the repeated `ccc`/`jc` field reads.
- `docs/attempts/research-luna-replay-interface/README.md` and `outcome-summary.json`: original `Treplay_post` is an unnamed 24-byte struct with seven members and implicit padding at offsets 6–7. The maintained explicit `reserved[2]` is invented. Removing it changes `replay_selector` by 20 bytes but does not improve strict status; a typedef/assertion declaration restores the prior compiler output. Every tested selector variant remains `object_match=false`, `cu_match=false`, with 6/15 strict functions.
- `docs/attempts/game-replay/draw_replay_selector-finding.md` and `replay_selector-finding.md`: extensive direct-call argument decoding exists for the selector family. The historical draw routine includes a header/table/warning UI absent from the maintained candidate. A partial source reconstruction regressed code size because it allowed GCC to shrink a large stack frame; the required not-yet-decoded call region should be completed before measuring. The caller has a second draw call with `rep=NULL`, a pre-wait selection snapshot, and a different interpolation target.

## Stop point and next useful work

No new effective function output or strict candidate resulted from the local-scope probe. Remaining `load_replay` difference is a GCC codegen/register-allocation mismatch around the repeated `r->ccc[]` and `r->jc[]` reads, with shifted cleanup target and additional candidate moves/padding. Source-order and local-type experiments already converge. Further equivalent local declaration/source spelling trials are unlikely to add information. A discriminating next step would need a new pass-level/register-allocation explanation or recovered historical source/header context.

## Artifacts

- `probe_load_cs_late.py`, `load-cs-late.c`: exact isolated transformation and source overlay.
- `load-cs-late-summary.json`: focused measured result.
- `load-cs-late-comparison.json`: full function, initialized data, common storage, and relocation comparison.
- Compiler output: `build/tu-context/game-replay/replayctx-cs-late-20260923/`.
