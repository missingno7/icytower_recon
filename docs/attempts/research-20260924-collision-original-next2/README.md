# `handle_player_collision_original`: declaration follow-up

## Result

The follow-up does **not** change the next recovery decision. The function remains unresolved, and the tested declaration family collapses to the existing output. Stop declaration spelling edits here; move to first-divergent GCC pass or historical compiler-context evidence if this function is resumed.

## Control and prediction

Run on HEAD `22423901dd54a51eefb1b18fcf9c5f75eab065a4`, with receipt-pinned maintained `src/main.c` SHA-256 `bee055ec1ae6c0dc3cea12de393560b0974302b0cf559cca6dd3cfb55f924533`. All six receipts (control and five probe receipts, including the duplicate late-declaration confirmation) record this identical source identity, so they share one whole-TU context cohort. The earlier source extraction hash `47c443d6...` was observed before the concurrent serialized source transaction; it is not the compiler input identity and is excluded from the cohort claim. Locked `tdm-2` GCC 4.4.1, project `-O2` profile, complete historical-order `game-main` TU, no generated prototypes. The strict CU comparator reported 64/82 exact functions in the baseline.

The precompile prediction was: if changing function-scope declaration order or the start of `solid2`'s declaration changed the historical player/status register choice at +0xcd and preserved all exact peers, declaration liveness/order could explain the residue. If the variants collapsed, close this source family and move up to pass/context evidence.

DWARF names `solid1` and `solid2` as signed `int` locals at function scope and gives them distinct location ranges. The focused card has first mismatch +205 (0xcd), 449 candidate bytes versus 456 historical bytes. At that point the candidate and oracle choose opposite EAX/EDX roles for the player pointer and status load.

## Batch

Four semantically equivalent declaration forms were tested against the same whole-TU context: reverse declaration order, combined declaration, initialization in each declaration, and moving `solid2`'s declaration to immediately before its first assignment. Their complete bodies and SHA-256 values are in `outcomes.json`; retained `.c` candidates are beside this report.

All variants compiled and deduplicated with the baseline to effective function identity `128ed0e2d4e76fcc`. Every result remained DIFFER at 449/456 bytes, first mismatch +205, with 153 differing bytes. Each strict receipt retained exactly 64/82 functions, with no gains or losses. The second late-declaration receipt is a duplicate independently generated spelling/control check and has the same outcome.

## Evidence and scope

- Full 82-function receipts and compiler comparisons are linked in `outcomes.json`; they include object sections, symbols, common/BSS, and relocation records.
- `run.py`, `reverse.c`, `combined.c`, `initialized.c`, and `late_solid2.c` retain the mechanical batch and candidate sources.
- Prior zero-guard spellings and explicit edge join are recorded in `docs/attempts/research-20260923-collision-original/README.md`; they changed later control flow but left the +205 residue.
- This branch establishes only that the tested declaration forms do not affect the effective output under this context. It gives no historical declaration proof and no recovery credit.

## Next discriminating step

If this target is revisited, compare the first relevant GCC pass for a source-backed candidate with the locked baseline and oracle instruction sequence. If candidate forms already converge before register allocation, stop local body spelling and investigate predecessor/TU/compiler state. Do not spend another round on declaration permutations.
