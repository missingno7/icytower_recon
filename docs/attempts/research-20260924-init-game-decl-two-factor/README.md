# Two-factor declaration-context follow-up (2026-09-24)

This report follows the frozen predictions in plan.md, committed as fe243514
before the two new compiles. It uses the locked tdm-2 GCC 4.4.1 profile,
historical whole-TU definition order, no added prototypes, the original EXE
only as verifier, and the native strict comparison. No maintained source,
accepted body, recovery ledger, generated current state, or oracle was edited.

## Inputs and parity

The pinned main.c SHA-256 is
2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044;
the ledger SHA-256 is
1fdd09a43371e21578c7ed5eb6d9c7f16f3cc00ebe4f796f76ba83a106c01a56.
Both were rechecked before compiling. A (neither group blanked) and D (both
blanked) were reused only after checking these identities, tdm-2, historical
order, no generated prototypes, no new implicit calls, and 64/82 exact peers.

The 14 removable 81-declaration legacy blocks were split into E (blocks 2-8)
and L (blocks 9-15). Each new input blanks 567 declaration lines with
equal-length spaces. All four inputs and the compiler's four generated overlays
have 311,717 bytes and 6,667 lines. Relative to A, B and C change disjoint
byte positions, and their union is exactly D's changed positions. The builder
preserved those positions exactly. Input hashes are in inputs.json; compiler
object hashes and strict output are in results.json and the TU receipts.

The two new diagnostic builds used -fdump-tree-all -fdump-rtl-expand. For each,
the dump and no-dump object SHA-256 hashes agree; pass-neutrality.json records
them. Existing A/D neutrality was checked in the preceding experiment.

## Four-corner response

| Corner | Blanked group | First parser-loop PHIs at 023t.ssa | Optimized initialization order | init_game effective ID | play effective ID |
|---|---|---|---|---|---|
| A | neither | check, replay_path, i | i, replay_path, check | 556ba3421a62e9b5 | bd705b3885b45e8a |
| B | E only | replay_path, i, check | check, i, replay_path | 313d88cd7b6220b8 | b41f7150cadbea90 |
| C | L only | replay_path, i, check | check, i, replay_path | 313d88cd7b6220b8 | b41f7150cadbea90 |
| D | both | replay_path, i, check | check, i, replay_path | 313d88cd7b6220b8 | d051a652b7fa5f35 |

For init_game, either group alone is sufficient to produce D's effective
emission. B, C, and D first differ from A at candidate function +0x248, where
A starts with mov $1,%ebx and the others start with a zero stack store. The
same PHI and optimized-order class accompanies this change. For play, each
single group produces the same third effective class, while both groups produce
D's different class. Thus response is target-specific and cannot be treated as
a monotonic declaration-count gradient or attributed to only E or only L.

## Strict oracle residue and protected peers

Every corner retains exactly 64/82 FUNCTION_MATCH functions, including
new_game and run_demo. There are zero exact gains, losses, or newly implicit
declarations. init_game remains DIFFER, 5780/5788 bytes, with the same first
historical mismatch at +14: candidate loads argc into ESI where the original
loads argv. Its differing-byte counts are A=5321 and B=C=D=5310; all four
retain the same 0x72c frame, 93 branches, 252 calls, and 419 unequal relocation
operands. A decrease of 11 differing bytes is diagnostic, not acceptance.

play remains DIFFER, 17396/17420 bytes, with its first historical mismatch at
+8 in all corners. Differing-byte counts are A=16141, B=C=16143, D=16138.
Its 0xa1c frame, 514 branches, 289 calls, and 864/885 unequal relocations do
not change across the corners. These full-function oracle residues are separate
from the candidate-to-candidate +0x248 init_game instruction-order observation.

## Scoped negative and next discriminator

The frozen recovery-facing criterion was a change to a specific historical
residue, especially init_game +14, while preserving exact peers. None occurred.
The experiment therefore closes this duplicate-declaration-count branch.
Further arbitrary counts or one-sided subset bisection are not justified by
these four corners. This says nothing about an independently evidenced
historical declaration set or another source/TU mechanism.

The next discriminating recovery experiment requires historical declaration
visibility/order evidence (for example a surviving header/source declaration
map) that selects one specific main.c context. Compile that context as a full
historical-order TU and ask whether the +14 argv/argc register role changes
without losing exact peers. If such evidence remains unavailable, no
count-based source edit or promotion is warranted. A GCC UID trace could
explain the diagnostic mechanism, but by itself would still not establish
historical source or recovery credit.

Artifacts: plan.md (precompile predictions), generate.py and inputs.json
(source/context hashes), pass_probe.py and pass-neutrality.json (diagnostic
neutrality), analyze.py and results.json (four-corner classes/residues), and
the two new strict receipts under docs/attempts/tu-context/game-main with
labels init-decl-two-factor-{early,late}-20260924. Full objects and dumps
remain local under build/tu-context/game-main. The two new source snapshots
are local and reproducible with generate.py at this source hash.
