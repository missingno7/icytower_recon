# `check_dir` same-CU call layout note (2026-09-24)

No maintained source or recovery ledger was edited. `check_dir` is already
`FUNCTION_MATCH` / `BODY_MATCH_LAYOUT_BLOCKED`: its 103 body bytes and all
resolved data/calls match, but its same-CU `call log2file` displacement differs
because `log2file` and `check_dir` do not have the original relative placement.
The source body is at `src/main.c:1963–1973`; its interface card is `AGREE`, and
the function card explicitly sets `body_edit_allowed: false`. Original DWARF
records parameters `filename`, `attrib`, and `param`, a lexical-block `name`,
and `buf[1024]` at frame offset -1040; the current body has the matching
local buffer in the guarded branch. There is no source-backed `check_dir` body
or declaration hypothesis to test.

## Localized placement cause

In the isolated historical-order control, `log2file` starts at candidate offset
28352 and `check_dir` at 37812, a 9460-byte gap. Their original VAs are
`0x40da58` and `0x40ffc4`, a 9580-byte gap. The call at `check_dir+0x1b`
therefore has candidate displacement -9492 versus the original -9612. Its
resolved target is correct in both cases; only the relative call operand is
layout-dependent.

`init_game` is the only size-changing function between the endpoints in the
control: original 5788 bytes, candidate 5666, a 122-byte reduction. The sum of
function sizes from `log2file` through the function immediately before
`check_dir` is 9564 original / 9442 candidate (also -122). Inter-function
padding totals 16 / 18 bytes respectively, leaving the observed endpoint gap
120 bytes shorter in the candidate. All other functions in this interval have
equal original and candidate sizes. The current `init_game` card is `DIFFER`,
5788/5666, with major CFG/literal mismatches; no size-only adjustment is
justified by this evidence.

## Deduplicated historical-order contexts

Existing isolated historical-order full-TU receipts consistently place
`log2file` and `check_dir` at offsets 28352 and 37812, keep `check_dir` as
`FUNCTION_MATCH`, and retain 63/82 exact functions with zero losses (except the
separate local-static experiment, which loses `draw_progress_bar` and keeps
62/82). These context changes modify bodies outside the interval or storage
unrelated to the call; they do not create distinct `check_dir` evidence.

- `docs/attempts/tu-context/game-main/luna-main-menu-scope-baseline-historical-20260924.json`
- `docs/attempts/tu-context/game-main/luna-play-summary-historical-order-split-20260924.json`
- `docs/attempts/tu-context/game-main/drm-historical-order-scoped-exit-20260924.json`
- `docs/attempts/tu-context/game-main/luna-show-credits-historical-order-20260923.json`
- Full comparison: `build/tu-context/game-main/luna-main-menu-scope-baseline-historical-20260924/comparison.json`

The remaining cause is the unresolved source/body layout of `init_game` inside
the call's target-to-site interval. `check_dir` itself needs no edit. A future
probe should be tied to evidence that changes the historical `init_game`
control flow or surrounding emitted layout, and must preserve the existing
63 exact-function set.
