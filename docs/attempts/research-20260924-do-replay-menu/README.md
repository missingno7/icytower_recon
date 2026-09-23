# `do_replay_menu` current-order follow-up — 2026-09-24

## Scope and control

Research-only overlays; no maintained source, generated current state, or `src/recovery.json` was edited. I read the current focused card/evidence, `docs/attempts/game-main/do_replay_menu-finding.md`, `docs/attempts/research-luna-do-replay-menu/README.md`, the requested `research-20260923-do-replay-menu-next` README/control receipt, and retained current-order TU receipts (`drm-1`–`drm-4`, `drm-verify`, and `luna-do-replay-menu-*`). All new probes use `game-main src/main.c --order current --no-prototypes` and isolated complete body overlays.

Fresh current-body control `luna-drm-current-control-20260924` reproduces the card: `do_replay_menu` is `DIFFER`, 2643/2661 bytes, first mismatch +8. The candidate prologue allocates `0x145c`; original allocates `0x185c`. The current maintained source has one function-scope `lastGameFile[2048]` and omits the evidenced `ret='l'` after the play-again selection.

## DWARF / source-supported target form

Tested the retained isolated `play-again-exit.c` body as `luna-drm-scoped-exit-control-20260924`. It separates the two non-overlapping `lastGameFile[2048]` locals into their historical scopes, keeps the save-path locals in their evidenced scope, and restores `ret='l'` after the play-again choice. This is supported by the focused DWARF local DIE/range evidence and original instruction at +0x107. Its prologue now uses `0x185c`, matching the historical frame. It produces a distinct 2643-byte outcome with first mismatch +364 (historically +0x16c) and 2052 differing bytes. At +364 the remaining exposed issue is the original `mov $0x20,%al` before `mov $0x1ff,%ecx` versus candidate's reversed setup before `rep stos`.

This reproduces the known retained result, but clarifies that the current maintained body does not include those evidenced scope/exit corrections. It remains `DIFFER`; this diagnostic body was not copied to `src/`.

## Caller-context test

Used `main_menu_callback-rank-candidate.c` as the predecessor body with the same corrected `do_replay_menu` overlay. This candidate is the previously retained source-backed caller-context probe. Its historical context requires two declaration edits: add the adjacent historical `get_rank(Tprofile *)` declaration and include `allegro/platform/aintwin.h` after `winalleg.h` for `_win_hcursor`. The first compile without this declaration context failed at `_win_hcursor`; the corrected isolated context compiles without new implicit declarations.

The current-order result `luna-drm-rank-predecessor-context-20260924` remains `63/82` exact, with no gains or losses and all current exact neighbors preserved. It emits a third distinct `do_replay_menu` effective identity (`2cfea875896db232` vs corrected control `9c5e2914f8b97f6e`) and remains 2643/2661 with first mismatch +364. The corrected predecessor overlay changes code elsewhere (including `my_alert`, which has an unchanged body) and changes the target's instruction sequence, but does not remove or move the +364 fill-byte/count order mismatch. Whole `.text` is unequal. This re-confirms current-order TU context sensitivity without establishing that this alternate predecessor is historically correct or fixing the target.

## Deduplication / neighbors

`python tools/effective_outcomes.py game-main do_replay_menu --pattern 'luna-drm-*-20260924.json' --compact` groups three probes into three effective target outcomes:

- `07fee387349d51e9`: current maintained body, first +8;
- `9c5e2914f8b97f6e`: scoped locals + play-again exit, first +364;
- `2cfea875896db232`: same target body with rank-candidate predecessor context, first +364.

Each TU receipt retains 63 strict function matches out of 82, no gains/losses, no whole-text equality; candidate `do_replay_menu` remains `DIFFER`. The main-menu predecessor context is source-supported but only a context discriminator: it changes target code while the fill setup ordering remains mismatched. There is no exact candidate or promotion receipt.

## Artifacts

- `body-current.c`
- `rank-predecessor-declarations.json`
- `build/tu-context/game-main/luna-drm-current-control-20260924/comparison.json`
- `build/tu-context/game-main/luna-drm-scoped-exit-control-20260924/comparison.json`
- `build/tu-context/game-main/luna-drm-rank-predecessor-context-20260924/comparison.json`
- Failed initial predecessor compile is retained under `build/tu-context/game-main/luna-drm-rank-predecessor-context-20260924/` with its error log.

## Handoff

The actionable source-backed next step is to serialize the retained DWARF scope/exit candidate if desired, then investigate the +364 setup order from new historical source or compiler-lowering evidence. Current evidence does not justify more cosmetic `memset` spellings: `memset` and `__builtin_memset` collapse, scalar loop expansion differs, and a predecessor-context perturbation changes the target's effective output without changing this order.
