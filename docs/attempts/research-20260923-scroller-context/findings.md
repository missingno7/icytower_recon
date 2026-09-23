# Scroller compiler-context research — 2026-09-23

## Strict state

`game-scroller/draw_scroller` remains `DIFFER` / `SOURCE_DIFFER`, 396 bytes, first mismatch offset 93. The six original candidate bytes differ at offsets 93, 96, 100, 103, 107, and 110; they are the register assignment/order used while preparing the first vertical `set_clip_rect` arguments. `body_edit_allowed` is false because the current card is `COMPILER_CONTEXT_DEPENDENCY`.

`scroll_scroller`, `restart_scroller`, and `init_scroller` remain strict `FUNCTION_MATCH` neighbors in the current CU. The `Tscroller` canonical layout is already recovered (2084 bytes with its ten recorded offsets); `draw_scroller` parameters and its sole local `i` have the historical types. No type difference is evidenced in the focused card. Twenty retained FAST/promotion records use the same body hash and repeat the six-byte mismatch; promotion rejections did not provide new evidence.

## Concrete TU hypothesis and experiments

Hypothesis: the `restart_scroller` peer immediately preceding `draw_scroller` in GCC's cgraph emission/context contributes to the target's register choices. The earlier isolated omission had observed a target change, and current probe source is pinned to the maintained `src/scroller.c` identity.

- Fresh baseline resolved-code identity: `8e3f418eaf7019f53f3f3a581cd5f9b0e22379479b897c3b2495491523bf147e` (396 B; six original mismatches).
- Omitting `restart_scroller`: identity `054ac64ee5511fb3b3e7bd0493ed1cfd79a6463e1dc1d8a0f165927de0f7d517` (396 B; original six plus four new differences at offsets 13, 15, 118, 121). This does not repair the target. The omitted peer is missing; `scroll_scroller` and `init_scroller` remain exact.
- Omitting `init_scroller` or `scroll_scroller` independently: both deduplicate to the baseline identity; all three remaining peers stay exact.
- Reordering the four declarations in an isolated `include/scroller.h` overlay (restart first, then full reverse): both deduplicate to baseline identity. All three exact neighbors are preserved. Candidate cgraph order remained `scroll_scroller`, `restart_scroller`, `draw_scroller`, `init_scroller`.
- Previously retained diagnostics: `-fno-unit-at-a-time` deduplicates to the restart-omission code class and makes `restart_scroller` DIFFER; `-fno-schedule-insns2` deduplicates to baseline. Neither was repeated.

The peer omission first changes RTL dumps in `expand`, then `initvals` and `unshare`; excerpts show changed temporary/label numbering for the target. This is evidence of TU context sensitivity, not a target match or proof of a specific allocator mechanism. The prototype-order negative rules out ordinary scroller-header declaration order as a useful lever.

## Artifacts

- `evidence/game-scroller/draw_scroller.json` and `.jsonl`: fresh baseline plus each peer omission, compiler commands, source/toolchain identities, focused RTL excerpts and effective code.
- `evidence/game-scroller/draw_scroller-rtl.json`: first changed passes for peer omission.
- `tu-context/game-scroller/luna-scroller-*.json` and `build-tu-context/game-scroller/luna-scroller-*/`: header-order overlays, comparisons and compiler dumps.
- `probe_compiler_context.py`, `probe_header_order.py`: local research harnesses. All output is under this directory.

No maintained source, current document, ledger or sibling repository was edited. Omitted-peer variants are diagnostic only and never promotion candidates.

## Blocker and next useful step

The type, local declaration, scroller-header prototype order, and simple peer-context hypotheses are either already exact or tested negative. Only `restart_scroller` / unit-at-a-time context has a distinct effective result, and it adds mismatches or loses an exact neighbor. The six original argument-scheduling differences remain unchanged.

The next useful supervisor investigation is to compare historical and candidate cgraph/RTL state for the call-argument setup, using additional evidence about the original TU declarations/peer bodies if available. A body edit is prohibited by the current card, and the PE cannot supply historical RTL. Do not continue body spelling experiments or treat either diagnostic output class as a match.
