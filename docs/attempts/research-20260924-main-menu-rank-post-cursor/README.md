# `main_menu_callback` rank call family after cursor and data owners

## Baseline

The source under investigation is the newly promoted local worktree source based on HEAD `ca7c5e4e4df85489829f3909e7695b14d1f50c53`, including the accepted cursor branch and symbolic blit keys (these source promotions are not yet committed). Its SHA-256 is `193a83d13cd6603525b40c23111d86f08b951691cb548afdfb38e3860fbab31e`. The fresh current-order `--no-prototypes` TU control retained **64/82 FUNCTION_MATCH** functions, with no gains, losses, or changed effective bytes in unchanged bodies. Whole text, object and CU equality remain false.

The control callback is DIFFER at 3,051 bytes versus 3,741 historical. It is missing the historical `get_rank` (four calls) and `get_rank_id` (one call) edge families. Its current direct-call total is 55 versus 62 historical.

## Original evidence

The original main-CU function DIE is at `evidence/census/dwarf-dies.jsonl` offset 129865, named `main_menu_callback`, VA `0x4100f8` to `0x410f95`. It includes `welcomeMessage` as `char[512]` at frame base offset -544 and records global `profile` as `Tprofile *`. Original lines 5236–5241 map to this CFG and call sequence (offsets are relative to the function start):

- `stricmp(profile->handle, "guest")` branches to the guest presentation at `+0x9ac`.
- On the non-guest path, `get_rank_id(profile)` is called at `+0x78f`; its return is tested, with the zero edge reaching the empty-rank-string path at `+0xd58`.
- The one `get_rank_id` and all four `get_rank` calls pass the loaded `profile` pointer unchanged. `get_rank` calls occur at `+0x7c3`, `+0x83b`, `+0x8b3`, and `+0x92b`.
- The four calls feed four shadow/highlight `textprintf_right_ex` draws. The original caller-side interface is consistent with the main/profile-CU DWARF signatures `get_rank_id(Tprofile *)` and `get_rank(Tprofile *)`. Current `src/profile.c` still has a conflicting `Tprofile_rank *` view; the generated interface cards report a 37-member / 1,360-vs-140-byte layout conflict. The probe declaration below is caller-side evidence only; it does not settle that cross-CU conflict.

The retained prior line/CFG report is `docs/attempts/research-main-menu-rank-interface-full-20260923/README.md`; the original call listing can be regenerated with `python tools/function_lines.py game-main main_menu_callback --source-view 5225 5242`.

## Isolated rank presentation probe

A retained complete callback body replaces the current version/welcome placeholder with the source-backed version stamp, guest branch, and rank presentation block. The only added declaration is `extern char *get_rank(Tprofile *profile);` in the probe overlay; `get_rank_id(Tprofile *)` is already declared by current main.c. The probe used the same locked TDM-2 compiler, current TU emission order, and `--no-prototypes` as the baseline.

- Compile succeeded; no new implicit declarations.
- **64/82 exact functions** remain, with no losses or gains.
- Historical missing rank edges are all represented. Candidate direct-call total is 66 versus 62 historical; the remaining multiplicity differences are other pre-existing call families.
- `main_menu_callback` remains DIFFER: 3,530 bytes versus 3,741 historical, with 3,249 differing bytes. Its first mismatch remains entry allocation at offset `+8` (candidate `0x4c`, original `0x6c`). No function, object, or CU match is claimed.
- The probe reports `do_replay_menu` under `code_changed_with_unchanged_body`; that function is already DIFFER in both reports, so the 64 exact-function set is unchanged. Five additional raw call fields move with same-CU layout.

This trial answers the call-family question: the historically evidenced guest/rank block removes both missing-edge findings and preserves all 64 exact functions. It does not narrow strict byte differences enough to justify source-form sweeps. Stop this branch here; resolve the separate profile type/interface conflict and other callback mismatches before reconsidering these calls.

## Artifacts

- `main_menu_callback-rank-presentation.c`: complete isolated body.
- `rank-declaration.json`: caller-side declaration and type-evidence note.
- `cu-inventory.json.gz`: for both runs, all 82 function records, all initialized-data symbols, BSS and COMMON symbols, section hashes/sizes, initialized-data comparison, and every object relocation (4,461 baseline; 4,492 variant).
- Receipts: `docs/attempts/tu-context/game-main/rank-post-cursor-control-20260924.json` and `docs/attempts/tu-context/game-main/rank-presentation-post-cursor-20260924.json`.
- Strict object/function reports and objects: `build/tu-context/game-main/rank-post-cursor-control-20260924/` and `build/tu-context/game-main/rank-presentation-post-cursor-20260924/`.

No maintained source, generated current state, or recovery ledger was edited. The inventories and probe are diagnostic evidence only.

## Native promotion after isolated research

The supervisor verified the historical guest literal and its four draw calls at original lines 5244-5248, then used `promotion-spec.json` with the retained callback and caller-side `get_rank(Tprofile *)` declaration. The native `tu_context_task.py` plan preserved 81 definition islands. `check` returned ACCEPTABLE with 64/82 exact functions before and after, no gains or losses. `promote` passed 156 function acceptance tests, diagnostic link, and global audit. The accepted transaction and strict check receipt are `docs/attempts/tu-context/transactions/main_menu_rank_presentation_20260924.json` and `main_menu_rank_presentation_20260924-check.json`. The callback remains DIFFER; the profile-CU callee type conflict and remaining callback mismatches remain open. This is an evidence-backed partial source correction, not recovery credit.
