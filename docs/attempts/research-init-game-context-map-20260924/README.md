# `init_game` main-TU context map (2026-09-24)

Isolated compiler/context analysis only. No maintained source, generated card, or
recovery ledger was changed. Collision-vector analysis is kept in its own
research folder; no output from that work is reused here.

## Emission neighborhood

In the historical main-CU order and locked TDM-2 `-O2` candidate, positions
71–75 are `check_characters`, `init_game`, `load_character`, `check_dir`, and
`take_screenshot`. The predecessor and successor around `init_game` are the
same in original and candidate. Their current statuses are respectively exact,
different, different, exact, exact. The candidate `init_game` is 5666 bytes
versus 5788 original; the following `load_character` is 330 bytes on both sides
but remains `DIFFER`.

`init_game` itself is the immediate predecessor to `load_character`; the
historically ordered callback functions follow as `load_character` then
`check_dir`. `take_screenshot` follows both. The earlier dedicated
`init_game` context probe set already tested the current body, a retained prior
body snapshot, and two compiler sensitivity controls. All keep 63/82 exact
functions with no losses and emit the same effective `load_character` body.

## Calls and callback ownership

The compiler cgraph has a direct `init_game -> check_characters` edge. It has
no direct `init_game -> load_character` or `init_game -> check_dir` edges:
`check_characters` passes those functions to `for_each_directory` at source
lines 2036/2039 (`check_dir`) and 2044/2046 (`load_character`). Its cgraph
summary reports the four `for_each_directory` calls, while independent COFF
`.text` references in `check_characters` resolve to the corresponding candidate
function entries at offsets +109/+304 for `check_dir` and +184/+328 for
`load_character`. This keeps callback address ownership distinct from call
edges.

The emitted `load_character` and `check_dir` bodies each call same-CU
`log2file` (at function offsets +217 and +28 in the context comparison); both
calls resolve to the correct target. For `check_dir`, the displacement alone
is layout-dependent. The `log2file` to `check_dir` span is 120 bytes shorter
than historical, with `init_game`'s 122-byte reduction mostly offset by two
extra bytes of inter-function padding. See
`docs/attempts/research-check-dir-layout-20260924/README.md` for the exact
address and displacement receipts.

## Literal ownership

At `init_game+32`, candidate code loads `.rdata+0x6aa` for `log2file`. Its
payload is `INIT GAME`; the historical operand points at `\nINIT GAME`. This is
the first reported byte difference and is source-visible at candidate
`src/main.c:2308` versus historical line 1393. The current literal card marks
placement/owner as unproven. A single observed historical address and unique
candidate content location are diagnostic; they do not establish a binding or
explain the other broad `init_game` differences.

The comparison inventory contains 409 `init_game` relocations, including 122
`.rdata` references and 9 with no independently established section base. The
compiler verifier records some targets as unique content locations, but the
function card still lists unresolved literal evidence; these records do not
prove historical literal identity or ownership. The independent call graph and
callback relocation ownership above remain usable without assigning these
literal owners.

## GCC context evidence and blocker

Existing locked compiler dumps include cgraph, CSA, and peephole2 stages. Across
the current and retained earlier `init_game` bodies, the extracted peephole2
scratch finds remain `init_game: si, di, ax, dx, cx, bx` and
`load_character: di, ax`; `check_dir` has no extracted scratch find. In the
cgraph summary, the current/snapshot `init_game` body differs in estimated
instructions (4303 vs 4287 at the finalized summary) and bytes (1776 vs 1784),
while `load_character` stays at 125 and `check_dir` at 70; all retain the same
source call edges. The two appended-call sensitivity controls also leave the
target scratch sequence and effective body unchanged. These dumps do not expose
the persistent GCC `search_ofs` cursor value, so unchanged findings do not prove
that the hidden cursor state is identical.

No available historical source evidence selects a different `init_game` body,
and every tested snapshot converges on the same `load_character` output. A new
pass-dump run would repeat existing evidence until such a source-backed context
variant exists. The exact blocker is a missing historically grounded
`init_game` definition or direct compiler-state trace; do not compensate by
editing `load_character` or `check_dir`, and do not add size padding.

## Receipts

- Focused cards: `docs/current/function-evidence/main/init_game.json`,
  `docs/current/function-evidence/main/load_character.json`,
  `docs/current/function-evidence/main/check_dir.json`.
- Literal record: `docs/current/literals/game-main/6aa.json`.
- Context and pass-dump analysis:
  `docs/attempts/research-historical-order-load-character-20260923/README.md`,
  `docs/attempts/research-historical-order-load-character-20260923/status.json`,
  `docs/attempts/research-luna-init-game-context/README.md`, and
  `docs/attempts/research-luna-init-game-context/status.json`.
- Baseline object comparison and locked compiler dumps:
  `build/tu-context/game-main/luna-init-context-baseline-final-20260923/`.
- Snapshot and compiler-sensitivity comparisons:
  `build/tu-context/game-main/luna-init-context-saved-body-final-20260923/`,
  `build/tu-context/game-main/luna-init-context-trailing-rest-control-20260923/`,
  and `build/tu-context/game-main/luna-init-context-trailing-fourarg-control-20260923/`.
