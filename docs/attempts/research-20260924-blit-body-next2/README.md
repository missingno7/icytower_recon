# blit_to_screen body follow-up after accepted storage-owner transaction

Status: isolated research only. No maintained source, generated current state, recovery ledger, or acceptance rule was edited.

## Pinned whole-TU control

Compiled HEAD source `src/main.c` in historical definition order with locked `tdm-2`, no generated prototypes, and no diagnostic dumps. Receipt: `docs/attempts/tu-context/game-main/research-20260924-blit-body-next2-control.json`.

- Compile: OK.
- Strict exact functions: 64/82 before and after; no gains or losses.
- `blit_to_screen`: DIFFER, 1239 candidate bytes / 1415 historical bytes, function position 43 in both.
- The exact peer count confirms the accepted BSS owner state is preserved in this control.
- The source identity in the receipt is the current accepted `src/main.c` SHA-256 `bee055ec1ae6c0dc3cea12de393560b0974302b0cf559cca6dd3cfb55f924533`.
- Retained body snapshot `docs/attempts/game-main/bodies/blit_to_screen.c` SHA-256 `f661069a59455ba2e7ab2ad70ae2f549e112b4911a1da3660345dad2952f47dd`.

## Predictions and result

Before the baseline compile, prediction was: reproducing the accepted source and historical order should keep 64 exact functions, preserve `blit_to_screen` at position 43, and leave its body unresolved. That prediction held. The control did not discriminate a body spelling because it made no source change.

The first raw residue is at `+0x13`: the conditional branch that skips the debug key-selection region targets historical offset `+0x8f` and candidate offset `+0x93` (displacement bytes `0x7b` vs `0x7f`). This occurs before the mode 0–6 dispatch body. The current focused card also reports `_key` operand identities differing by 8 bytes at six early key loads (`+21..+135`). That is a separate global-layout/relocation question; it does not explain the mode 3–6 local-scope evidence.

## Mode 3–6 evidence audit

Current focused evidence is `docs/current/functions/main/blit_to_screen.json` and `docs/current/function-evidence/main/blit_to_screen.json`; line/CFG trace was generated with `tools/function_lines.py game-main blit_to_screen --blocks` and `--source-view 2260 2345 --calls-by-line`.

- Mode 3 (historical source line 2293–2294) has its own loop local `y`, iterates to 480, computes the horizontal offset from `logic_count`, `fixsin`/`itofix`/`fixtoi`, and `ply[player_id]->level`, and calls `blit` once per iteration. The retained source has a separate mode-3 block and the same loop/call shape.
- Mode 4 (lines 2297–2302) has a branch-local `y` for `level % 480` and two `blit` calls with source-y offsets `y` and `y - 480`. The retained source matches this shape.
- Mode 5 (lines 2304–2307) and mode 6 (lines 2309–2312) have separate lexical blocks and duplicate signed-int `x`/`y` DIEs in each block (`125070/125084` and `124991/125005` respectively). The retained source declares `dx`/`dy` and `x`/`y` independently in each branch, clamps x/y, converts the interior values to int, then calls `stretch_blit` once per branch.
- Historical direct call relocations in the function are four `blit` calls and one `stretch_blit`; the other visible transfers are indirect Allegro dispatches. This agrees with the modes' source call multiplicity and does not support deleting a branch or call.
- The candidate source already matches the DWARF-supported branch-local lifetime structure. Moving those declarations to a shared outer scope or collapsing the duplicate locals would contradict current DIE evidence. No compiler probe was run for such an unsupported change.

## Decision

The declaration/lifetime hypothesis for modes 3–6 is exhausted by positive DWARF-to-source parity, not by a failed spelling sweep. It does not explain the first historical residue at `+0x13`; this follow-up therefore makes **no change to the next body-recovery decision** and earns no recovery credit. Do not run a mode 3–6 declaration-count sweep.

The next discriminating work should trace the four-byte debug-off skip displacement to its concrete block-size difference in lines 2270–2277 and reconcile candidate versus historical instruction groups there, while preserving the accepted BSS owners and the 64 exact peers. Only after that boundary is explained should the later mode-family instruction residues be reconsidered. Strict acceptance remains unchanged.
