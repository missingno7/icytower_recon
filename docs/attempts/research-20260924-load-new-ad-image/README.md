# `load_new_ad_image` layout review (2026-09-24)

## Outcome

No function-source probe was justified. The current function card marks the 100-byte body `FUNCTION_MATCH` / `BODY_MATCH_LAYOUT_BLOCKED` and explicitly forbids body edits. Its only direct-transfer mismatch is the same-CU call to `log2file`: historical relative displacement is `-33913`; candidate is `-32913`, while independent resolution reaches the same `log2file` entry. All four direct calls resolve, there is no indirect control flow, and the source CFG is a single null check followed by logging, optional bitmap destruction, bitmap load, and pointer assignment. A body variant cannot repair this placement-only operand without violating the protected-body rule.

## Evidence and negative context

- Card: `docs/current/functions/main/load_new_ad_image.json`. Source body is `src/main.c:1833-1844` (SHA-256 `937aa5aa589810ea987da08cb9f379711d207c496341d75ebf3179bf2d68d9b4`). DWARF records only `pAd: const FLDAdSpot *`, in scope DIE 134576, using location list `0x78af`; no lexical sub-blocks are reported.
- Historical disassembly calls `fldads_get_random_ad`, `log2file`, `destroy_bitmap`, `load_bitmap` at body offsets 8, 33, 50, 79. The candidate call at offset 33 resolves to the same historical same-CU `log2file` target. No call/data/CFG evidence points to a source expression change.
- Historical and candidate emission position is 80, immediately after exact `run_demo`; historical prefix is not exact. `log2file` is exact as a function body, but its candidate emission offset is 28352 versus historical 28920. The card therefore classifies this as `SAME_CU_CALL_LAYOUT` and routes it to supervisor.
- Existing historical-order whole-TU receipt `docs/attempts/tu-context/game-main/luna-play-summary-historical-order-split-20260924.json` has 63 `FUNCTION_MATCH` functions (including `new_game`, `run_demo`, and `load_new_ad_image`), no gains or losses, and the same 79-predecessor position. Its recorded raw changes to `load_new_ad_image` are relocation-sensitive; it reports no confirmed unchanged-body effective code changes. The order-only probe did not supply a mechanism to move this callee relative to the caller.
- Prior generated-prototype multiplicity/order variants are summarized in `docs/attempts/research-prototype-context/README.md`: every variant retained the same 63 exact functions. Their raw changes included this function, but no confirmed effective-code change was reported. This is negative context evidence, not a new probe of this function.
- Separate interface evidence in the card reports `fldads_get_random_ad`'s return aggregate has the same 16-byte size but three pointer members differ in const qualification (`char *` historical vs `const char *` candidate). The call ABI and this function's code remain equal; this is an interface/type blocker, not evidence for a body edit. Its global storage declarations for `pFLDAd` and `pFLDAdBitmap` agree.

## Handoff boundary

No new isolated compile or source variant was run: the only evidence-backed lever is the earlier same-CU emission context, which has already been tested in the retained historical-order receipt; the function body is protected, and an unrelated declaration/type edit has no demonstrated effect on the `log2file` relative call. Resolving the blocker requires an evidenced emission/layout change that preserves the exact-neighbor set, plus independent resolution of the recorded callee aggregate interface conflict. No maintained source, recovery data, or generated card was changed.
