# `add_itr_file` lexical-scope and CFG follow-up

Date: 2026-09-24. Research-only GCC 4.4.1 `-O2` full-TU overlays based on the owner-aligned replay TU at `property-case-order-source.c`. Each overlay changes only `add_itr_file`; its eight exact functions remain exact in every receipt. No maintained source, current generated state, or recovery ledger was edited.

## Historical evidence

The function is 360 bytes at `0x41e740`. Its original CFG is clear from `objdump`: the initial `name == "."` branch at `+0x3b` targets the shared epilogue at `+0xcc`; the attribute test at `+0x48` branches to directory handling at `+0xd8`; the replay path falls through extension checking and successful allocation/property/copy work, then reaches that epilogue. Negative replay-property results branch to an out-of-line handler at `+0x140`, which either returns via `+0xcc` or stores `-1000-res` and jumps back to the successful copy block. Directory processing follows the epilogue and ends with a jump back to it.

The original line table maps the function entry and initial locals at lines 608–610, the dot guard at line 613, the attribute guard at line 615, and later code to lines 618 and 629. DWARF places `res` (declared at line 629) inside a nested lexical block (DIE 224734; range-list offset `0x1430`); `length` and `name` are at function scope. This is a concrete distinction from the retained candidate body, which declares `res` at function scope.

## Isolated probes

I tested both source-level branch orientations, local `res` declarations immediately before/at the property call, lexical scopes around the replay-error handling, and two local sentinel predicate spellings. Existing attempt-ledger forms for straightforward directory/replay polarity, return-vs-goto, and physical source-block reordering were read and not repeated. The new effective outcomes are:

| Probe(s) | Source distinction | Size | First mismatch | Differing byte offsets | Unequal relocations |
|---|---|---:|---:|---:|---:|
| `luna-add-itr-lexical_after_malloc-20260924` | directory-first structured body; local `res` initialized after allocation | 353 | +59 | 288 | 24 |
| `luna-add-itr-lexical_before_malloc-20260924` | directory-first structured body; scoped declaration before allocation | 353 | +59 | 288 | 24 |
| `luna-add-itr-lexical_minimal-20260924` | directory-first body; local scoped `res` with distinct sentinel guard | 344 | +59 | 278 | 24 |
| `luna-add-itr-replay_first_scoped_res-20260924` | replay-first body; scoped assignment to `res` after allocation | 364 | +59 | 291 | 25 |
| `luna-add-itr-replay_first_file_gate-20260924` | replay-first body; positive `.itr` gate and scoped initialized `res` | 364 | +59 | 291 | 25 |
| `luna-add-itr-labels_local_res-20260924` | historical label order; scoped local initialized `res` and shared `done` | 357 | +59 | 265 | 22 |
| `luna-add-itr-labels_local_res_version_split-20260924` | historical label order; scoped local `res` with separated sentinel predicates | 360 | +59 | 290 | 25 |

`effective_outcomes.py` groups the seven probes into six effective machine-code outcomes. The after/before-malloc scoped variants collapse to the same output. Replay-first variants both produce 364 bytes, but are distinct effective outputs. The label-order local-res forms produce 357 bytes and 360 bytes respectively. Every report shows eight exact functions and no neighbor loss. The 360-byte candidate has 290 unequal bytes and 25 unequal relocations; equal size does not indicate a body match.

## Blocker and artifacts

The lexical-scope evidence is now tested, but it does not drive GCC 4.4.1 into the historical block placement. Even with the historical label order and `res` in a lexical block, the +59 branch remains a short conditional to an epilogue at `+0x62`; history has a six-byte near conditional to the epilogue at `+0xcc`. The directory path / early-return blocks remain compiler-reordered. The experiment therefore does not support further body spelling search without a new source-level fact that changes the CFG or a supervisor-approved compiler-context investigation. No strict candidate was found.

- Source base and exact overlays: this directory.
- Full comparison receipts: `build/tu-context/game-replay/<label>/comparison.json`.
- Effective-output grouping: `python tools/effective_outcomes.py game-replay add_itr_file --pattern 'luna-add-itr-*-20260924.json' --compact`.
- Current focused card and complete historical/candidate instruction evidence: `docs/current/functions/replay/add_itr_file.json`, `docs/current/function-evidence/replay/add_itr_file.json`.
- Maintained `src/replay.c` SHA-256: `73d99aea3da12bb730812e43443c1a0dc07b8457c3469c4d0b285ef0a1d20c93`.
- Maintained `src/recovery.json` SHA-256: `2f0710c753742dda1de1bb624cce6fa378ba14c6a205adb9e3552c67bbd8f360`.
