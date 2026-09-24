# `_strptime` follow-up: no discriminating local experiment remains

Scope: isolated assessment of `game-strptime/_strptime`. No maintained source, recovery ledger, generated current state, or production build inputs were changed.

## Live strict baseline

Re-ran `python tools/check_function.py game-strptime _strptime` against the current repository. Result: `DIFFER / SOURCE_DIFFER`, candidate 2005 B versus historical 2028 B, 1376 differing bytes, first mismatch at +8. The current candidate reserves 108 bytes versus the original 76. The card still reports the unresolved `__imp__tzname` relocation owner at +0x36b. Existing exact peers remain `first_day`, `match_string`, and `strptime`; the check did not promote anything.

Current source SHA-256: `eb169b0ef065cd2329fab7f07e9a73b446bbc0a59e0c12f029ec4d64fbce6389` (same source snapshot already used by the retained context work).

## Existing hypotheses and outcomes (no repeats)

- Definition/emission context: six current and historical-order probes, including helper and wrapper reorderings, all preserved the three exact peers and collapsed to `_strptime` effective-output identity `cd7ad95100fd447d`. Full historical source order is not a useful next discriminator under this locked build context.
- Helper expansion: expanding all three week-number helpers produced that same output. Source spelling/expansion in this tested family is canonicalized.
- `first_day` inline decision: isolated `noinline` is the one tested source lever that changes the effective parser. It yields 2017 B, moves the first mismatch to +216, changes direct-call count from 29 to 32, and reduces the frame from 108 B to the historical 76 B. It remains broadly different (1375 differing bytes) and leaves all exact-peer counts unchanged. Historical DWARF proves a `first_day` function exists and original transfer evidence shows three direct calls, but does not establish that the source carried a `noinline` attribute. Do not promote that attribute as historical evidence.
- Interface evidence: the public wrapper is an exact witness for the first three register-passed parameters and fourth stack state pointer. No currently retained caller observation discriminates a different `_strptime` ABI.

## Decision

No bounded source-backed/CFG/pass experiment is justified by the current evidence. The only tested lever that affects the relevant call/frame shape is the already-run `first_day` noinline probe; repeating it or sweeping attribute variants would not discriminate historical source. The 76-byte frame alignment is diagnostic only: the noinline candidate still has a 1375-byte body mismatch and unresolved relocation ownership.

The next recovery decision is to pause local code-shape grinding and obtain an independent discriminator: the original `F:\projects\icytower\trunk\source\strptime.c` (including `first_day` declaration and parser body), or a pinned source revision with evidence that accounts for the stateful `%Z`/`gmt` extension and exact call structure. A pass dump of only the candidate cannot identify a historical divergence without historical source/IR. Separately, `__imp__tzname` ownership needs strict proof before any acceptance attempt; prior alias probes are diagnostic support only and have not updated the current proof state.

This branch yields no strict function match or recovery credit and does not change the next recovery decision beyond confirming that another local source rewrite is unwarranted.

## Minimal retained references

- Current strict receipt: `build/fast/game-strptime/_strptime.json`
- Focused card: `docs/current/functions/strptime/_strptime.json`
- Context/order results: `docs/attempts/research-20260924-strptime-context/HANDOFF.md`, `full-historical-order.comparison.json`, `full-historical-order.receipt.json`
- Prior deduplicated context inventory: `docs/attempts/research-strptime-context-20260924/README.md`
- Inline hypothesis and compiler receipts: `docs/attempts/research-20260924-strptime-next-inline/README.md`, `docs/attempts/tu-context/game-strptime/research-20260924-strptime-next-inline-*.json`
