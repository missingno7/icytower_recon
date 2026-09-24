# `check_characters` call-layout context audit — 2026-09-24

Isolated supervisor research; no maintained source, generated current document, or recovery ledger changed.

## Current proof and source evidence

The focused card marks `check_characters` `FUNCTION_MATCH` / `BODY_MATCH_LAYOUT_BLOCKED`: candidate and historical bodies are both 345 bytes; all 15 relocations resolve equally, with no CFG or data-owner mismatch. The candidate preserves the original eight branches and ten calls. `num_chars`, `characters`, and `play_char` references are independently resolved; no ownership prerequisite is open. `check_beta_tester` is the same exact immediate emission predecessor in both objects.

Five direct same-CU call operands differ only in displacement: four calls to `for_each_directory` at offsets +117, +192, +312, +336 and one to `set_current_avatar` at +261. Each resolves to the correct historical function entry. Relevant relative-layout evidence in the card: `for_each_directory` historical/candidate offsets 25184/23756; `set_current_avatar` 900/900; `check_characters` 32380/31456. This is a natural placement gap across other CU contributions, not a body-source defect.

## Prior negatives checked

- `docs/attempts/game-main/check_characters-supervisor-review.json` records the pre-promotion failure where the body still wrote `curr_char`; that source/typed-data issue was repaired and is not the current blocker.
- `docs/attempts/check-characters-layout-admission.json` records that `grinder_task begin` rejects this body because `BODY_MATCH_LAYOUT_BLOCKED` is protected.
- `effective_outcomes.py` has 424 retained contexts for this target (74 normalized outcomes across the entire historical probe archive). Those contexts vary the exact-function set; they are not a reason to edit this protected body or select an arbitrary compiler state.
- The current source-order card already says historical definition order agrees with maintained order.

## Bounded current/historical order batch

Two fresh full-TU overlays used current `src/main.c`, `--no-prototypes` (preserving the maintained declaration context), and no body replacements:

- `check-characters-layout-current-order-20260924`
- `check-characters-layout-historical-order-20260924`

Both compiled successfully and produced one deduplicated normalized `check_characters` output (`37e0d2e383690ddb`): strict `FUNCTION_MATCH`, 345/345 bytes, 0 differing body bytes, 0 unequal relocations, frame `0x21c`, 8 branches, 10 calls. Both retained 63/82 exact functions with no gains or losses. `new_game` remains 1139-byte `FUNCTION_MATCH`; `run_demo` remains 159-byte `FUNCTION_MATCH`. Definition order therefore does not repair or worsen the decoded call layout. Receipts are in `docs/attempts/tu-context/game-main/` under the two labels above.

## Disposition

There is no strict source candidate to seek: the function already has a strict body match. Its five direct-transfer operands are layout blocked, and the source-order hypothesis deduplicates. Further changes to this body would violate its protection rule; further CU layout work must correct source-backed size differences in the intervening nonmatching functions while preserving all 63 exact peers.
