# `init_game` argument allocation and local scope probe — 2026-09-24

Isolated research only. No maintained source, generated current state, or
recovery ledger was changed. All successful probes used the retained
`checkFile=argv[i]` candidate together with the previously source-backed leading
newline and `play_char` field corrections.

## Historical entry roles

The original prologue is 15 bytes. At function offset `+12`, it copies
`argv` from `12(%ebp)` to `ESI`; it does not copy `argc` to a register. The
historical DWARF location list keeps `argc` frame based across the function
entry and the option parser. At `+572` and `+869`, the original compares
`argc` directly from `8(%ebp)`. `argv` remains in `ESI` for the parser, where
`argv[i]` is loaded into `EAX` at `+600` and then retained in `EDI` when needed
as the replay path.

With the historical `checkFile` lifetime represented in candidate source, the
first strict mismatch is `+14`. The candidate copies `argc` from `8(%ebp)` to
`ESI` at `+12`, then copies `argv` from `12(%ebp)` to `EDI` at `+15`. At its
option parser, the candidate compares `argc` in `ESI`, copies it to `EDI`, and
loads `argv[i]` into `ESI`. This is a structural allocation difference, not a
branch-displacement or relocation-layout difference. The function remains
`DIFFER` at 5688 bytes versus 5788 historical.

The focused card's original DWARF places both `check` and `checkFile` in the
lexical block beginning at original offset `+600`. `checkFile`'s location
changes across `+584..+1324`; the historical line table places the parser at
1489–1497. These facts suggested declaration scope as a possible source of the
entry allocation difference.

## Causal scope trials

The first probe moved only `char *checkFile` from function scope into the
`if (argc>2)` parser block. Its complete function output was identical to the
outer-scope control: same `+14` first mismatch and 5688-byte size. The second
probe also moved `int check` into that block, matching the two named locals'
historical lexical ownership. It produced the same output again. Both retained
63 exact CU functions, with no gains or losses. Therefore these declaration
scopes do not explain the argument-register reversal.

An initial `--research-base` invocation used a function-only candidate as if it
were a complete TU and failed because required includes were absent. It made
no maintained changes. The valid follow-up used the supported `--body` overlay
against `src/main.c`.

## Disposition

No remaining source or compiler-state evidence identifies why historical GCC
kept `argc` in its incoming stack slot while assigning `argv` to `ESI`. The
known `checkFile` location evidence does not justify forcing a register choice;
the two scope-only tests disprove that candidate cause. The broader
instruction-selection/layout mismatch also remains. Do not add source padding
or edit neighboring functions based on this result.

## Artifacts

- Candidate bodies: `checkfile-block-scope.c` and
  `check-and-checkfile-block-scope.c` in this directory.
- Successful probes: `build/tu-context/game-main/init-game-checkfile-block-scope-20260924/`
  and `build/tu-context/game-main/init-game-checkfile-and-check-block-scope-20260924/`.
- Control receipt and object: `docs/attempts/tu-context/game-main/init-game-checkfile-lifetime-20260924.json`
  and `build/tu-context/game-main/init-game-checkfile-lifetime-20260924/`.
- Source evidence: `python tools/function_lines.py game-main init_game --source-view 1375 1410`
  and `python tools/function_lines.py game-main init_game --source-view 1489 1497`.
