# do_replay_menu follow-up: shared name-copy call

Research-only TU probe. Canonical sources, current state, ledger, and maintained bodies were not edited.

## Candidate

`main.c` is the full retained `game-main` overlay from `drm-save-init-all-20260924`, with the two-branch `pname` copy changed to the equivalent shared-call form:

```c
strcpy(pname, isGuest ? " - " : profile->handle);
```

This candidate source form is structurally supported by the original data flow, though the exact C syntax is not uniquely proven. Original instructions at `0x41112a..0x41113e` test `isGuest`; the `je` at `0x41112c` sends the non-guest path to `0x411790`, while the guest path loads the literal pointer at `0x411132` and joins the shared call setup at `0x411137`. The non-guest block at `0x411790` loads `profile->handle`, then jumps to that same setup at `0x411137`. Both paths therefore reach the single pname `_strcpy` call at `0x41113e`. The function has two direct `_strcpy` calls total: the pname initialization call at `0x41113e`, and a separate comment-copy call at `0x4118d6` (`demo->comment` destination). The previous candidate split the source into `if/else`; GCC folded the guest literal copy into stores and emitted a separate non-guest call, so its machine CFG did not represent this shared call. A conditional argument is a plausible source form consistent with the original, but other C forms can produce the same CFG.

## Fresh result

Probe receipt: `build/tu-context/game-main/research-20260924-do-replay-menu-shared-copy/comparison.json`.

- Compile succeeded; 63 strict exact game-main functions before and after; 0 gains, 0 losses; 79/79 historical predecessor identities retained.
- `do_replay_menu`: 2643/2661 bytes, `DIFFER`; first byte mismatch at function offset `0x196` / VA `0x41112e` (candidate branch displacement `0x5a`, original `0x5e`).
- The candidate now has the shared direct `strcpy` call form, but remains 18 bytes short. No `FUNCTION_MATCH` claim.

## Current blocker

The expected source CFG for the first guest-name copy is now represented and does not lose any existing exact peers. Its immediate residual is a four-byte branch-target displacement difference after the copy; the remaining 14-byte size deficit is still unlocalized. Next work should compare the typed/DWARF-scoped blocks and call edges after the guest-path join, starting at `0x41112e`, without revisiting local names or buffer/initialization hypotheses.

Source: `docs/attempts/research-20260924-do-replay-menu-shared-copy/main.c`.

## Audit against maintained `src/main.c`

The extracted complete body (`do_replay_menu.c`) was diffed against the maintained definition. Every source difference is accounted for by original instruction/DWARF evidence:

1. **Play-again exit:** the retained body sets `ret='l'` after `play_again=1`. Original instructions `0x411095..0x4110a4` store `1` to `play_again`, load `0x6c` (`'l'`) into the loop-result register, and jump back to the loop test. The maintained body omitted that assignment.
2. **Local lexical scope:** DIE `130898` owns `status`, `action`, and `fname`, `pname`, `comment`, `fpath`, `buffer`; the retained body declares them inside the save-replay branch. DIE `131107` owns one `lastGameFile` in the view-replay branch; DIE `131035` owns the second `lastGameFile` in the nested save path, and DIE `131074` owns `thisChecksum` within that nested scope. Maintained declarations were function-wide. DWARF types identify `buffer` as `char[1024]` and each `lastGameFile` as `char[2048]`; the retained body uses those extents. `lets_save` has no location and remains undeclared.
3. **Filename/comment/name initialization:** original instructions `0x411104..0x41110f` fill 511 bytes of `fname` with spaces then zero `fname[0]`; `0x411116..0x411122` fill 511 bytes of `pname`; `0x411132..0x41113e` copy either the guest placeholder or `profile->handle`; `0x411143..0x411165` fill 511 bytes of `comment` then zero `comment[0]`. The retained body matches these writes. Maintained code instead zeroed the last byte of `fname` and `comment` and omitted the `pname` fill.
4. **Shared name-copy edge:** `0x41112c` branches non-guest execution to `0x411790`, which loads `profile->handle` and rejoins at `0x411137`; guest execution loads the placeholder and falls into the same argument setup. Both reach `_strcpy` at `0x41113e`. The retained conditional-argument expression represents this observed shared call and its pointer selection. The exact original C spelling is not uniquely recoverable from the machine code.
5. **Remaining statements and control flow:** no other semantic source differences appeared in the body diff. The already-separated `status`/`action`, explicit checksum capture, and three draw clusters match the prior evidence in `do_replay_menu-finding.md` and the focused card.

Fresh current-order/no-prototypes probe of the extracted body: `build/tu-context/game-main/research-20260924-do-replay-menu-body-current/comparison.json`. It compiled, preserved all 63 exact peers (0 gains/losses), and changed no unchanged body. `do_replay_menu` remains `DIFFER`, 2643/2661 bytes; first difference remains the branch displacement at `0x41112e`. The research spec is `transaction.json`; it is only a probe recipe and has not been planned or applied as a production transaction.
