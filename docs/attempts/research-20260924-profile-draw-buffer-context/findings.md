# `draw_buffer` current-order research (2026-09-24)

Scope: complete `game-profile` TU overlays compiled with locked TDM-2/GCC 4.4.1, current order, and production-equivalent `--no-prototypes`. All candidate bodies and generated comparisons are isolated under this research label or ignored `build/tu-context/`; no production source, current card, recovery ledger, or exact body was edited.

## Oracle and current body

- The current focused card is `docs/current/functions/profile/draw_buffer.json`: historical VA `0x4191c8`, historical size 185, candidate size 181, `DIFFER`, `SOURCE_CONTROL_FLOW_SHAPE`, first difference at function offset 27. The current CU has 11 exact functions.
- Historical DWARF gives `int draw_buffer(BITMAP *bmp, char *buffer, int x, int y)` and locals `int pos`, `char tempBuf[256]`, `int tempPos`; there is no historical `c` local. The current source uses an optimizer-only `char c` and retains the three evidenced locals/array.
- Original disassembly shows the two loop exits loading `buffer[1]` before incrementing the pointer: at `+0x2c`, `mov 1(%ebx),%al; inc %ebx; test %al,%al`; and at `+0xa1`, the same load/increment/test sequence. The current 181-byte body emits `inc %ebx; mov (%ebx),%al` at both sites. This is a legal equivalent schedule, but it is shorter and changes the branch layout. Historical line rows place the initial and next-byte loads within the same loop source region; the card retains the full row list.
- `docs/attempts/game-profile/draw_buffer.jsonl` already records eleven older attempts. Ten variants (including `buffer[1]` then increment, preincrement, separate increment then dereference, `while (*buffer)`, condition assignment, and a `for` loop) converge on the same 181-byte code. The postincrement loop-header version is 175 bytes and diverges earlier. The older TU notes identify the same original-load-before-increment distinction.

## New full-TU batch

Ten body overlays are retained under `bodies/`. Every probe compiled; all preserved the 11 exact peers. None made `draw_buffer` exact. Eight variants stayed at 181 bytes with the same first mismatch at offset 27. Effective instruction-byte dedup produced three code groups:

| Code group | Variants | Candidate | Result |
| --- | --- | ---: | --- |
| `2084e0b95b16` | `postinc_store_and_reordered_reset`, `inverted_branch`, `reset_before_draw`, `for_comma_load_then_increment`, `for_increment_then_load`, `no_char_local_direct_load` | 181 bytes | Same first mismatch, +0 exact peers, 11 retained |
| `b1ede055c39a` | `branch_local_updates`, `inverted_branch_local_updates`, `early_continue_explicit_update` | 181 bytes | Same first mismatch, +0 exact peers, 11 retained |
| `c4c411846ad9` | `do_while_explicit_guard` | 171 bytes | First mismatch offset 25; worse by 10 bytes, 11 peers retained |

The hashes are of the candidate instruction-byte sequences emitted in the TU probe receipts and are used only to deduplicate these experiments. Receipt paths are `build/tu-context/game-profile/draw_buffer_<label>/comparison.json`; retained source overlays are `bodies/<label>.c`.

The one allowed compiler-level discriminator tested with `tools/sweep.py` was `-Os`: `draw_buffer` became 167 bytes and first differed at offset 13. `-Os` is therefore not the missing 185-byte match for this candidate. The earlier sweep invocation with `-Os -O3` is not counted as an independent result because the last optimization flag wins.

## Blocker and next discriminator

No source-shaped loop, branch, branch-local update, update-expression, or local-removal hypothesis tested here changes the pointer-load scheduling into the historical `load [ebx+1]; inc ebx` pattern while retaining the exact peers. The current evidence points to an instruction scheduling/liveness difference after both control-flow paths merge/split, not missing behavior. The useful next step is recovering the original statement placement from historical DWARF line rows and comparing focused RTL/assembly scheduling for the two pointer-update sites. Avoid repeating the already-deduplicated loop spelling variants or retaining the shorter `-Os` output.
