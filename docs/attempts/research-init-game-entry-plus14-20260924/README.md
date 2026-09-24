# `init_game` entry allocation follow-up — 2026-09-24

Isolated current-order, no-prototype full-TU research after the accepted `init_game` correction. No maintained source, generated current state, or recovery ledger changed.

## Direct evidence at the first mismatch

The focused current report says `init_game` is 5688/5788 bytes, first difference at function offset `+14`, candidate byte `08`, original byte `0c`. This is an operand difference in the prologue, not a relocation or literal mismatch. Historical instructions at `+12` load `argv` from `12(%ebp)` into ESI (`8b 75 0c`); current candidate loads `argc` from `8(%ebp)` into ESI (`8b 75 08`) and then copies `argv` into EDI (`8b 7d 0c`). The current generated card still labels this `LITERAL_CONTENT_DIFFERENCE`; the byte evidence shows that classification is stale after literal repair.

The original formal-parameter DIEs have location lists at `0x6382` (`argc`) and `0x63d2` (`argv`). The `argc` list describes a frame-relative location at entry and EBP+8 across its later live ranges. The `argv` list transitions from its incoming frame location to DWARF register 6 (ESI) at function offset `+92`; historical line/source-view also shows `argv` in ESI at entry. This confirms the historical register role. It does not identify which C source lifetime or declaration detail caused GCC to choose that role.

## Retained negative batches checked

- `research-initgame-entry-scope-20260924`: moving `checkFile` into the parser block, then moving both `check` and `checkFile`, left the effective function output at +14/5688. These probes already negate those scope hypotheses.
- `research-luna-init-game-context`: six saved body/context probes converge for their target; earlier complete bodies and tail-call sensitivity controls did not provide a source-backed register-allocation explanation.
- `research-prototype-context`: generated prototype count/order can change initialization ordering and object identity, but historical prototype multiplicity is unproven and `init_game` was unavailable to that batch's canonical effective comparison. It does not authorize choosing a prototype arrangement.

## Discriminating lifetime probe

The accepted source has a `replay_path` local at function scope. All of its reads/writes are inside the `argc>2` branch, while the historical local DIE inventory has no `replay_path` DIE. I narrowed its declaration to that branch as a semantics-preserving lifetime hypothesis; no other body text changed. The full-TU probe `init-game-entry-plus14-replay-path-block-scope-20260924` compiled successfully, retained 63 exact functions with no gains/losses, and kept `new_game` and `run_demo` FUNCTION_MATCH. `init_game` remained 5688/5788 and first differed at +14.

`effective_outcomes.py` gives this variant a distinct normalized output (`def16219bc072578`), so it is not merely a relocation/layout duplicate. Its strict comparison summary is worse (5176 differing bytes versus 5171 in corrected accepted body); it does not move the parameter allocation. Do not promote it. Receipt and object are in `docs/attempts/tu-context/game-main/init-game-entry-plus14-replay-path-block-scope-20260924.json` and `build/tu-context/game-main/init-game-entry-plus14-replay-path-block-scope-20260924/`.

## Disposition

The known legal scope hypotheses have been tested or lack positive historical evidence. The remaining mismatch is GCC's parameter register allocation. The existing prototype-context evidence also shows that pre-expansion declaration state can affect this TU, but no historical prototype topology or compiler-state trace selects the matching variant. Do not add a forced register, volatile use, padding, or arbitrary prototype count. Further progress requires source/header declaration evidence or an independently justified compiler-state trace.
