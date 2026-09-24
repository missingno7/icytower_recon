# blit_to_screen function-static declaration probe

Status: isolated research only; no source, oracle, recovery ledger, or production record changed.

## Question and evidence

The current focused card allows source investigation (`SOURCE_CONTROL_FLOW_SHAPE`, `body_edit_allowed=true`), but the stronger source fact is the separate current static-scope card: original DWARF DIE 124685 and COFF `_blit_mode.40598` identify `blit_mode` as a function-static BSS object owned by `blit_to_screen` (original declaration line 2268). The current reconstruction instead has top-level `int blit_mode;` at `src/main.c:359`, with a COMMON `_blit_mode` symbol. Current code defines the modes 0 through 6, but its strict body remains 1239/1415 bytes with first residue at +0x13 and current main TU has 64/82 exact functions.

The two retained body attempts are an older incomplete switch and the current fuller if/else reconstruction; neither tests the authenticated storage-scope distinction. The retained function body and new candidate are archived in this folder.

## Predictions, written before compilation

Single discriminating hypothesis: give the retained `blit_to_screen` definition its evidenced `static int blit_mode` local, and remove only the reconstructed top-level declaration in the isolated overlay.

- If code and peers remain identical, the existing relocation ambiguity is explained by declaration ownership, but the 176-byte body residue remains a separate CFG/body task. Do not treat ownership repair as a body match.
- If the function's effective instructions or relocation ownership changes, compare those against the target and identify whether the change resolves the `_blit_mode` prerequisite; strict match still requires every function relocation and full function equality.
- If exact peers change, retain that context branch as diagnostic and do not promote it. The change must not be compensated by editing peers.
- If the tool cannot remove the top-level declaration while preserving this single-factor source variant, record the tooling blocker and stop.

The diagnostic `--statics historical` control was compiled first and left the source declaration unchanged; it produced the same 64/82, 1239-byte `blit_to_screen`, and 79/82 historical predecessor exact count as the no-static baseline. Therefore this follow-up uses the evidenced declaration move directly in an isolated overlay; it does not imply a historical source fact beyond the DWARF/COFF evidence above.

## Control receipt

`research-20260924-blit-screen-next-baseline` used the current source, historical definition order, no generated prototypes, and the locked whole-TU compiler. It compiled successfully: 64 exact before/after, no gains/losses, 79/82 predecessor exact, `blit_to_screen` 1239/1415, candidate/historical position 43. No body-independent effective-code comparison was available for six listed functions in the no-dumps receipt.

Control and candidate source/context hashes and strict outputs are recorded in the receipts after compilation.
## Static-owner result and peer regression diagnosis

The isolated follow-up compiled successfully with the locked compiler, historical TU order, and no generated prototypes. It used `candidate-static-local.c` plus `source-without-global.c`; no production file or acceptance rule changed.

- Current control: 64/82 exact; `blit_to_screen` 1239/1415, historical position 43; 79/82 exact at the historical predecessor boundary.
- Static-owner candidate: 63/82 exact; no gains, only `draw_progress_bar` lost. `blit_to_screen` stays 1239/1415 at position 43 and still differs at +0x13. Its `_blit_mode` relocation is now independently owned by the function-static BSS DIE/COFF object at historical VA 5100324. The `_key` targets remain eight bytes above historical (`+56..+62` resolve to original offsets `+64..+70`).
- `draw_progress_bar` remains 486 bytes and its candidate/historical relative layout, masked instruction bytes, and body shape are all equal. The only failing fields are two absolute BSS relocations at function offsets +23 and +443: control `.bss+12` resolved to VA 5100332; static-owner candidate `.bss+16` has no resolved VA because section-base evidence is conflicting. The strict state changes from `FUNCTION_MATCH` to `CODEGEN_SIMILAR`; no body bytes changed.

The conflicting base evidence is concrete. In the control, both `p` (candidate BSS offset 8 → original VA 5100328) and `logfilename` (offset 32 → VA 5100352) imply section base 5100320. With `blit_mode` local, the candidate BSS offsets become: `_blit_mode.43224` 8 → VA 5100324, `_p.42647` 12 → VA 5100328, `_value.42616` 16 → VA 5100332, and `_logfilename.42125` remains 32 → VA 5100352. The first three imply section base 5100316; `logfilename` still implies 5100320. The relocation in `draw_progress_bar` therefore cannot be accepted through one independently proven section base.

Relevant storage evidence:

- `docs/current/storage/game-main/124685.json`: original `blit_mode` DIE/COFF local BSS owner, VA 5100324.
- `docs/current/storage/game-main/120529.json`: `p`, an exact function-static owner, original VA 5100328.
- `docs/current/storage/game-main/120199.json`: `value`, original VA 5100332, but its DIE is under lexical block 120168 and is currently labelled `UNRESOLVED_LEXICAL_SCOPE`; its parent chain reaches DIE 120129, `draw_progress_bar`. The candidate production DIE is a function-static `draw_progress_bar::value` at offset 12; in the static-owner probe its COFF symbol moves to offset 16.
- `docs/current/storage/game-main/127958.json`: `logfilename`, exact function-static owner, original VA 5100352, candidate offset 32 in both contexts.

This peer regression is a relocation proof/evidence gap, not changed instruction bytes. The original `value` DIE's lexical ancestor is available in `evidence/census/dwarf-dies.jsonl`; the current owner matcher does not expose that ancestry in the focused storage card. The smallest useful next step is a report-only owner diagnostic that follows DIE 120199 → lexical block 120168 → `draw_progress_bar` and checks the candidate COFF offset 16 against original address 5100332. Keep strict acceptance unchanged; do not edit `draw_progress_bar`.

An alternate TU order is not justified: both measured candidates use historical order, `blit_to_screen` is at the same historical/candidate position 43, and the loss is explained by BSS owner/base evidence. No broad reorder search was run.

## Hashes and artifacts

- Production source snapshot: `src/main.c`, SHA-256 `2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044`.
- Retained full function candidate with local static: SHA-256 `6cf24de9904f048431678576742130297b3d038250893dd08b1fb0e62800aefc`.
- Isolated source baseline with only the top-level `blit_mode` declaration removed: SHA-256 `74d91d18f9e47c43df696b8b2aa93b1afb3d03d294f441025a04ae393a84939a`.
- Static-owner compiled TU and strict comparison: `build/tu-context/game-main/research-20260924-blit-screen-next-static-owner/` (`comparison.json` SHA-256 `fdaea7847aecde12469845d88f2530db5737643f6b9104fc1c47352625b0529e`).
- Baseline compiled TU and strict comparison: `build/tu-context/game-main/research-20260924-blit-screen-next-baseline/`.
- `--statics historical` control left top-level `blit_mode` unchanged and produced the same 64/82, 1239-byte function outcome as the pinned baseline. The tool's declaration edit spec intentionally does not remove uninitialized object declarations, so the specific variant used a retained research-base source copy.

## Follow-up plan: `old_msc` BSS owner (predictions frozen before compiles)

Original instruction evidence at source line 5288 has only a `bg_menu` test, setup of `adjust_sample(bg_menu, options.msc_volume, 128, 1000, 1)`, and the call. It has no old-volume load/compare and no old_msc store. Original DIE 129968 is an `int` local in `main_menu_callback` with no location/address. There is no evidence for an automatic snapshot/capture value; this experiment therefore retains an unused automatic `int old_msc` DIE and follows the historical `if (bg_menu)` behavior, with no assignment. It removes the candidate-only function-static BSS object and its unsupported compare/write. No exact function body is modified in production.

We reuse A only if current `src/main.c` and retained `blit_to_screen` context hashes still match the first probe; B likewise only if its prior source/context hashes match. A = existing baseline, current static `old_msc` + global `blit_mode`; B = existing static-owner result, current static `old_msc` + function-static `blit_mode`. New C = automatic-unused `old_msc` correction only; D = C plus function-static `blit_mode`.

Predictions recorded before compiling C/D:

- C should remove the candidate-only `_old_msc` BSS owner, keep `blit_to_screen`'s existing global-symbol relocation state, improve `main_menu_callback` only around line 5288, and restore `draw_progress_bar`'s strict relocation if its BSS section base becomes unique. It should preserve the 64 exact peers.
- D should resolve `blit_to_screen`'s `_blit_mode` ownership as in B while removing `_old_msc`; if `_old_msc` was the sole conflicting anchor, `draw_progress_bar` should return to exact and the TU should retain all 64 exact peers. If D still loses the peer, that falsifies the single-owner explanation and we stop without a BSS/order sweep.
- Neither C nor D is predicted to make `main_menu_callback` a strict match; its large unrelated body mismatch remains. Neither variant earns recovery credit unless the native strict comparator says exact.

A and B are the pinned historical-order/no-prototype results already recorded above. Their source and body hashes are rechecked before reuse. C/D use complete retained function bodies, the locked compiler, historical order, no prototypes, and isolated overlays.

## Follow-up result: old_msc × blit_mode BSS interaction

Original `main_menu_callback` line 5288 was checked with `tools/function_lines.py`: only `bg_menu` is loaded/tested, then arguments for `adjust_sample` are prepared and the call executes. There is no old_msc load/compare/store in the original emitted range. The original DIE 129968 is an `int` function local with no location/address. Therefore no historical instruction evidence supports capturing the old volume before the slider update. The isolated source variant keeps `int old_msc;` as an unused automatic for the DIE, changes the guard to `if (bg_menu)`, and removes the static object and assignment. This is a source-backed unlocated local, not a guessed capture.

| Corner | old_msc source | blit_mode source | Exact peers | draw_progress_bar | blit_to_screen | main_menu_callback |
|---|---|---|---:|---|---|---|
| A (pinned control) | static local | global common | 64/82 | FUNCTION_MATCH | DIFFER 1239/1415 | baseline DIFFER |
| B (pinned first probe) | static local | static local | 63/82 | CODEGEN_SIMILAR | DIFFER 1239/1415; blit_mode owner resolves | baseline DIFFER |
| C (new) | unused automatic; no compare/store | global common | 63/82 | CODEGEN_SIMILAR | DIFFER 1239/1415; global owner unresolved | DIFFER 2883/3741 |
| D (new) | unused automatic; no compare/store | static local | 64/82 | FUNCTION_MATCH | DIFFER 1239/1415; blit_mode owner resolves | DIFFER 2883/3741 |

C falsifies the prediction that removing only `old_msc` would restore the BSS anchor. D confirms the interaction: the pair of source-supported scope corrections returns the exact peer set to 64/82 with no gains/losses. `draw_progress_bar` relocations at +23 and +443 resolve to original VA 5100332 in D. Candidate local BSS symbols become `someCounter=0`, `blit_mode=4`, `p=8`, `value=12`, `count=16`, `number=20`, `logfilename=32`; their independently evidenced original addresses produce one base, 5100320. In C, the order is `someCounter=0`, `p=4`, `value=8`, `count=12`, `number=16`, `logfilename=32`, yielding conflicting bases 5100324 and 5100320. The static `blit_mode` object fills the four-byte gap needed to make the retained `p` and `logfilename` anchors agree after `old_msc` is removed.

`main_menu_callback` remains DIFFER (first byte mismatch +8, candidate 2883 vs 3741), and `blit_to_screen` remains DIFFER (first byte mismatch +0x13, candidate 1239 vs 1415). D resolves both `_blit_mode` relocations at +31/+50 to VA 5100324, but does not close the function's body/CFG mismatch. No function is newly exact; the result preserves all 64 previously exact peers.

Predicted automatic capture before slider update was not compiled: original instructions provide no load or use that could establish the captured value. No protected body or production source was edited. A/B are reused only with matching base/body hashes; C/D compiled in isolated historical-order overlays with no generated prototypes. This closes the bounded 2×2; no further local count/order sweep is justified by these outcomes.

## Current-order D control (prediction frozen before compile)

Question: does the combined old_msc automatic-unused + function-static blit_mode context retain the exact peers when compiled in current source definition order instead of historical order? D historical is 64/82 with no gains/losses; its BSS owners align, `draw_progress_bar` is FUNCTION_MATCH, while `main_menu_callback` and `blit_to_screen` remain DIFFER.

Prediction: if current-order D has any exact-peer loss or changes the target body/relocation result, a serialized transaction needs the historical definition-order edit in addition to the two source-backed storage/body changes. If it also retains the same 64 peers and target residues, historical order is unnecessary for this narrow change. This single control does not authorize a broader order search.

The compile will reuse the same isolated source-without-global baseline and complete retained bodies as D, changing only `--order current`; no production source, protected body, oracle, or acceptance state is modified.

## Current-order D result

The isolated current-order/no-prototype D compiled successfully. It retains 64/82 exact functions with no gains or losses, matching historical-order D. The focal bodies and relocation results are identical: `main_menu_callback` DIFFER 2883/3741; `blit_to_screen` DIFFER 1239/1415 with `_blit_mode` relocations +31/+50 resolving to 5100324; `draw_progress_bar` FUNCTION_MATCH 486 B with `.bss+12` relocations +23/+443 resolving to 5100332. The BSS local offsets match historical D exactly (`someCounter=0`, `blit_mode=4`, `p=8`, `value=12`, `count=16`, `number=20`, `logfilename=32`); `p` and `logfilename` both anchor base 5100320. For this combined source correction, a wholesale historical definition reorder is not required to preserve exact peers or these target results. This does not recover either large target function and does not authorize a production change by itself.

## Serialized acceptance

The separate `blit_mode_old_msc_20260924` TU_CONTEXT transaction used the two
retained complete bodies and an exact removal of the top-level `int blit_mode;`
declaration. The planner required storage card DIE 124685 to prove original
function-static BSS scope and the retained owner body to declare the matching
static local. Its generated source SHA-256 was
`bee055ec1ae6c0dc3cea12de393560b0974302b0cf559cca6dd3cfb55f924533`,
identical to the isolated current-order D overlay. The fresh whole-TU check
returned ACCEPTABLE, 64/82 exact before and after, zero losses, and no proven
owner regression. Promotion then passed 156 function tests, the diagnostic
link, and the global audit. Current storage card 124685 is `EXACT_OWNER`.
The promoted transaction records are under
`docs/attempts/tu-context/transactions/blit_mode_old_msc_20260924*.json`.
Neither `blit_to_screen` nor `main_menu_callback` became a function match; no
new function bytes are counted as recovered.
