# do_replay_menu follow-up (2026-09-23)

## Scope and control

Ran a fresh production-equivalent whole-TU control with the retained `play_again-exit.c` body:

`python tools/tu_context_probe.py game-main src/main.c research-20260923-do-replay-menu-next-baseline --order current --no-prototypes --body do_replay_menu=docs/attempts/research-luna-do-replay-menu/play-again-exit.c --focus do_replay_menu`

It compiled successfully; 63/82 exact functions before and after; no gains or losses; no unchanged-body code changes; `do_replay_menu` remains DIFFER (2643/2661), first mismatch +364. Its effective identity is `9c5e2914f8b97f6e`, exactly the already known scoped-locals + play-again-exit outcome. This confirms the production-equivalent declaration context does not change that function's bytes. Receipt: `baseline-receipt.json`; full TU comparison and object: `build/tu-context/game-main/research-20260923-do-replay-menu-next-baseline/`.

## New concrete observations

At +364, the original initializes the filename fill with `mov $0x20,%al` then `mov $0x1ff,%ecx`; the current candidate reverses those independent setup instructions (`mov $0x1ff,%ecx`, then `mov $0x20,%al`). Both then select the same destination and use `rep stos`. The later original code confirms the two fills and NUL stores are consistent with the evidenced 512-byte `fname` and `comment` arrays. This is the previously exposed instruction-order mismatch, not a newly discovered source-level omission.

The fresh candidate and original each have 63 direct calls, but the verifier's current symbol normalization names the stack-probe edge `chkstk` versus `__chkstk`; the historical direct-call count is still one stack probe. This is a symbol spelling issue in diagnostic call counts, not an extra source call.

The fresh control adds no new effective output and supports the prior elimination: scoped DWARF locals repair the frame, play-again exit is repaired, intrinsic spellings collapse, scalar loops emit a different loop, and the known predecessor-context candidate changes a register assignment but leaves the fill setup ordering unchanged.

## Current blocker

No strict candidate. The first mismatch is an instruction-order/register-allocation difference between two independent operands in GCC's expanded fill operation. No remaining source spelling has independent source/DWARF support that plausibly changes that order; adding artificial state, asm, or compiler controls is outside the rules. Broader downstream differences remain after +364. A useful next investigation needs an independently evidenced compiler-context or source-sequence cause for GCC 4.4.1's fill setup order; another cosmetic `memset` spelling is not justified by the observed effective-output collapse.
