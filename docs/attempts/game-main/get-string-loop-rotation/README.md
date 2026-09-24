# `get_string` loop rotation probes (2026-09-24)

Isolated GCC 4.4.1/TDM-2 research. These files are complete replacement bodies
and a retained copy of the current `main.c`; no maintained source, current card,
or ledger was changed. Probes used `--order current --no-prototypes` with that
retained TU, preserving the 63 exact peer functions.

## Results

| Probe | Source form | Candidate | First mismatch | Effective result |
| --- | --- | ---: | ---: | --- |
| `gsrot-baseline` | retained body | 790 B | 91 | 63 exact peers; 541 differing bytes (478 outside relocation fields) |
| `gsrot-goto-continue` | replace `continue` with `goto outer_iteration` | 790 B | 91 | Same effective output as baseline |
| `gsrot-shared-return` | route the three switch returns through `leave_string`, reusing `c` for the return value | 780 B | 91 | 63 exact peers; 526 differing bytes |
| `gsrot-close-while` | express close-button exit as `while (!closeButtonClicked)` | 761 B | 91 | 63 exact peers; 518 differing bytes |
| `gsrot-keypressed-guard` | process input only inside `if (keypressed())`, then always reach the cycle wait | 784 B | 91 | 63 exact peers; 539 differing bytes |

The `goto` spelling collapses to baseline output. Shared return and close-while
forms produce distinct layouts but neither restores the historical loop
rotation. All first differ at offset 91, so there is no candidate for FAST or
promotion.

The retained body sources are this directory's `gsrot-*.c` files. Full isolated
probe receipts are `docs/attempts/tu-context/game-main/gsrot-*.json`; compiler
objects and dumps are under `build/tu-context/game-main/gsrot-*`.

## Pass evidence and blocker

Adding GCC's `-fdump-tree-all` plus the existing cgraph/RTL dump flags was
byte-neutral: compiling the same baseline overlay path with and without those
diagnostic flags produced identical 212,239-byte objects (SHA-256
`d4670f0f98f88b7146e1eefab5ce3f88fa9ef78eb3c38a7c71d330ab3108e4e5`). The
tree dumps therefore can be read without confounding emitted bytes.

The baseline CFG at `main.c.013t.cfg` has a distinct outer head (`bb 8`, the
`closeButtonClicked` test) and a bottom polling latch (`bb 30`, branching to
`rest` or back to `bb 8`). `main.c.086t.loop` retains the bottom `rest` / count
check, and `.087t.loopinit`, `.089t.dceloop1`, `.099t.ivcanon`, `.108t.loopdone`,
and `.123t.optimized` do not move that latch ahead of the close-button test. In
`.123t.optimized`, the polling path still tests `cycle_count` at the bottom and
returns to the outer head only after the count becomes nonzero. The distinction
is already present in early GIMPLE and survives the loop optimizer; later RTL
`csa` and `peephole2` snapshots retain it. The existing disassembly finding
records the historical rotated layout.

The close-while variant is structurally closer but still differs: its optimized
GIMPLE waits on `cycle_count` first, checks `closeButtonClicked` after that wait,
then enters the next body. The historical code places the `cycle_count` test
before the close-button test and uses that same test as the outer back-edge.

An additional historical edge narrows the source-CFG discrepancy. In
`function_lines.py game-main get_string --source-view 5378 5450`, the
`keypressed()` false branch at offset 502 targets offset 232 (`+0xe8`), the
`cycle_count` test. That test branches to the `rest(2)` block at offset 660 and
the `rest` block jumps back to offset 232. Thus the historical no-key path
enters the cycle wait; the current `if (!keypressed()) continue;` GIMPLE edge
goes straight back to the outer head and skips it. `gsrot-keypressed-guard.c`
uses the historical no-key-to-wait edge, but its optimized GIMPLE still leaves
the polling latch at the bottom (`bb 26` / `bb 27`) and returns to outer head
`bb 7` only when the count becomes nonzero. Its strict result remains DIFFER.

The four bounded source forms either preserve this CFG or change its input,
return, or exit edges without causing the GCC loop pass to move the polling
latch ahead of the close-button test. The historical keypress edge is
inconsistent with the current `continue` path; correcting that edge alone is
insufficient.
The remaining blocker is the compiler's failure to rotate the corrected
early-GIMPLE loop, or another historical source-CFG detail not yet recovered.
Further cosmetic switch/continue/return reshaping is unsupported by these
results; any next probe needs a specific historical edge or early-GIMPLE fact.
