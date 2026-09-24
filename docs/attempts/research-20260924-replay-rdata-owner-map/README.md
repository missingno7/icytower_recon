# Replay `.rdata` owner and displacement map

Read-only analysis of the existing PE and isolated owner-correct object. No selector body probes were run for this map, and no maintained source, generated current state, or recovery ledger was changed.

## Owners and offsets

| Item | Original replay contribution | Candidate `.rdata` object | Ownership evidence |
|---|---:|---:|---|
| `Harold\0` literal | `+0x11e` = VA `0x4d7a7e` | `+0x11e` | `create_replay` code ref at function `+0x7f`; literal content is in both pools |
| `replay_selector` switch table | `+0x1b8..+0x304` (332 B, 83 dwords) | `+0x1bc..+0x258` (156 B, 39 dwords) | Original indirect-jump xref at `0x41d685`; candidate `.text` relocation to `.rdata+0x1bc`; no variable DIE/COFF symbol inside either span |
| `save_replay` months initializer | `+0x440` (48 B, 12 pointers) | `+0x380` (48 B, 12 `.rdata` relocs) | DWARF local `months: char *[12]`, `DW_OP_fbreg -84`; Jan–Dec targets |
| `_REPLAY_HEADER` | `+0x470` = VA `0x4d7dd0` | `+0x3b0` (944) | Historical and candidate COFF static symbol; class 3, `.rdata`, six bytes `ITR140` |

The correct-owner probe links the candidate header at the same absolute address as the original: candidate base `0x4d7a20` plus `0x3b0` equals `0x4d7dd0`; original contribution base `0x4d7960` plus `0x470` also equals `0x4d7dd0`. Anchoring the candidate this way shifts earlier pool locations by `+0xc0` (192 B): candidate `Harold` becomes `0x4d7b3e`, exactly 192 B after original `0x4d7a7e`. The candidate and original `Harold` offsets within their own contribution are identical, so this is a late-owner displacement, not an early string-length change.

## Why the late owner is 192 bytes away

The source-level generated switch table is short by 44 entries (`44 * 4 = 176` B). Its candidate start is four bytes later than the historical start (`+0x1bc` vs `+0x1b8`), so the table end is only 172 B earlier (`+0x258` vs `+0x304`). After `Dec`, original data has 21 zero bytes before the naturally aligned month-pointer table; the candidate has one. The 20-byte padding difference brings the displacement at the month table and header to `172 + 20 = 192` B. In equivalent terms, the missing table contributes 176 B, its 4-byte later start offsets 4 B, and the alignment gap contributes 20 B: `176 - 4 + 20 = 192`.

This is a compiler-generated switch table with no source variable or COFF data symbol. The source-level route is to restore the historical dispatch cases; synthesizing table bytes or padding would not recover their code targets or semantics. The source case mapping is being handled in a separate lane.

## Relocations under owner-correct section anchoring

The existing strict comparison for `luna-create-replay-owner-static-upper-current-20260924` records these owner-sensitive edges (candidate VA versus original VA):

| Function | Function offset | Candidate target | Historical target | Delta / note |
|---|---:|---:|---:|---|
| `create_replay` | `+0x2c`, `+0x34` | `0x4d7dd0`, `0x4d7dd4` | same | Header refs align exactly |
| `create_replay` | `+0x7f` | `0x4d7b3e` | `0x4d7a7e` | `+192`, `Harold` |
| `update_file_list` | `+0x4f` | `0x4d7a20` | `0x4d7960` | `+192`, `.rdata+0` under owner-implied base |
| `load_replay` | `+0x10`, `+0x96` | `0x4d7b45` | `0x4d7a85` | `+192` |
| `load_replay` | `+0x71` | `0x4d7b48` | `0x4d7dd0` | Candidate points to duplicate `ITR140` at `.rdata+0x128`, not the owner |
| `get_replay_property` | `+0x13`, `+0xe3` | `0x4d7b45` | `0x4d7a85` | `+192` |
| `get_replay_property` | `+0x66` | `0x4d7b48` | `0x4d7dd0` | Candidate points to duplicate `ITR140` at `.rdata+0x128`, not the owner |

The three exact peers lost by the upper-case owner probe are `update_file_list`, `load_replay`, and `get_replay_property`. The early-pool relocations show the 192-byte base shift; the two hard-coded `memcmp(..., "ITR140", ...)` refs are a separate owner issue because the candidate copy at `+0x128` is 648 B before the real header. Existing isolated evidence says routing both comparisons through the named header removes that duplicate literal and aligns those owner refs, but does not move the header from `+0x3b0`. Later comparison-string refs also show 20-, 8-, and 32-byte deltas around the month-table alignment boundary.

## Scope and next dependency

Current `src/replay.c` still declares lowercase mutable `static char replay_header[] = "ITR140";` at line 46 and keeps the two comparison literals at lines 233 and 312. `save_replay` has its `months` initializer at line 372; the current TU definition list places it before `draw_replay_selector` and `replay_selector`. The existing owner trials varied header spelling, declaration placement, macro placement, visibility and historical/current function order without changing the effective misplaced owner output.

The actionable blocker is the source-semantic 44-entry prefix of the generated `replay_selector` dispatch and its natural consequences for later `.rdata`. Once the historical cases are mapped, re-run the isolated owner-correct candidate with the header comparisons sharing `_REPLAY_HEADER` and verify the seven exact peers. This map itself is not a source repair or promotion.

Evidence: `docs/attempts/research-20260923-create-replay/rdata-order/README.md` and `crosswalk.json`; `docs/attempts/research-20260924-create-replay-next/README.md` and `owner-fix-summary.json`; candidate object `docs/attempts/research-20260924-create-replay-next/build/game-replay/luna-create-replay-owner-static-upper-current-20260924/unit.o`; comparison `.../comparison.json`.
