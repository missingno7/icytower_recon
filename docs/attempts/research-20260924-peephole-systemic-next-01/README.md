# Main TU peephole context: allocated-bitmap guard

Research only, 2026-09-24. Production source, ledger, tools, and generated
current state were untouched. `probe.py` compiled a full isolated main.c
overlay with the locked TDM GCC 4.4.1 command and pass dumps. `analyze.py`
compared the object with the original executable using the strict verifier.

The earlier diagnostic put `if (!gfx_driver) return;` after two
`gfx_driver` dereferences in `force_create_profile`. It increased that
candidate body from 1458 to 1470 bytes, added a DX peephole scratch choice,
and regressed five later emitted exact functions. This probe instead puts
`if (!bg) return;` immediately after `bg=create_bitmap(...)` and before the
first `blit`. It is a plausible failure guard, but **not established as
historical source**.

| Full TU variant | Exact functions | `force_create_profile` bytes | Its visible peephole scratch | Exact peer losses against baseline |
| --- | ---: | ---: | --- | --- |
| Retained baseline | 63/82 | 1458 | none | none |
| Prior `gfx_driver` guard | 58/82 | 1470 | DX | `log2file`, `testWindowResolution`, `new_game`, `uninit_game`, `check_beta_tester` |
| New allocated-bitmap guard | 63/82 | 1466 | none | none |

The new variant has **the same complete strict exact-function set** as the
baseline: no gains and no losses. The five peers regain their baseline visible
peephole choices (DX; CX/BX/AX/DX; CX/BX/SI/AX; DX/CX; BX respectively).
`force_create_profile` remains DIFFER against the original 1538-byte body;
neither guard is a function match or a proposed production edit. The
downstream exactness establishes that this source-level failure check can be
expressed without perturbing those peers under the locked compiler. The
allocation-result guard branches on the returned value, while the earlier
global-pointer guard caused a memory comparison to acquire scratch DX at
peephole2. A persistent `peep2_find_free_register` cursor remains an
inference from reference GCC source and these dumps, not an observed locked
compiler variable.

`analyze.py` also attempted raw normalized CSA and peephole2 section equality
for the five peers. Its deliberately narrow normalizer leaves transient GCC
declaration IDs (`D.50927` versus `D.50930`) and label numbers (843 versus
844), so those fields are false and **do not establish a pass difference**.
The strict object comparison and extracted scratch choices are the usable
outcomes here. The prior baseline-versus-global-guard study already showed
identical normalized CSA and first visible difference at peephole2.

The bitmap-result guard has no support in original control flow: original
`0x40d47a` calls `create_bitmap`, stores EAX as `bg` at `0x40d47f`, then
loads and tests global `gfx_driver` at `0x40d485`; it never tests `bg` before
the first `blit`. The original also tests `gfx_driver` at `0x40d460` before
`create_bitmap`. Null routes at `0x40da0b` and `0x40da04` supply zero
dimensions and continue the calls. This matches upstream historical Allegro
`gfx.h:304-305`, which defines `SCREEN_W` and `SCREEN_H` as
`(gfx_driver ? gfx_driver->w/h : 0)`. The current body used raw member access.

## Source-backed macro probe against current 64-function state

`probe_screen_macro_current.py` replaced **only** the first two width/height
argument pairs in current `src/main.c` with `SCREEN_W, SCREEN_H`. Its source
SHA-256 was `5d9e491689df8bef83e4752e68366e7878d34e3380615efc980d476e876ec4c3`.
The strict full-TU result is 64/82 exact, with no gains or losses;
`draw_results` and all five previously sensitive peers remain exact.
`force_create_profile` is still DIFFER at 1490 versus original 1538 bytes.
Its visible peephole scratch list remains empty and the five peers retain
their baseline choices. This is source-backed CFG evidence for the first two
macro calls, not a whole-function proof.

The complete retained definition is `force_create_profile_screen_macros.c`.
`tu-context-spec.json` requests historical order, no generated prototypes,
and just that one body. `prepare_transaction.py` confirmed `build_text` with
the spec reproduces the verified full overlay byte-for-byte with no header
edits. Serialized acceptance/promotion remains for the supervisor.

Useful receipts: `screen-macro-current-source.diff`,
`screen-macro-current-receipt.json`, and the isolated object/dumps at
`build/tu-context/game-main/research-20260924-peephole-systemic-next-01-screen-macro-current/`.

The general diagnostic rule is to check full-TU emission context when a
predecessor edit adds a peephole scratch choice. The prior global-pointer
guard diverged at peephole2 after downstream CSA equality; the historical
Allegro macro expressions here add no visible scratch choice. A locked
compiler cursor trace still needs a compatible instrumented `cc1`.

Small receipts: `receipt.json` (strict focus and scratch sequence),
`analysis.json` (whole exact set), and the isolated object/dumps at
`build/tu-context/game-main/research-20260924-peephole-systemic-next-01-bitmap-guard/`.

## Historical screen-size macro correction

Original `force_create_profile` tests `gfx_driver` before `create_bitmap` and
again before the first `blit`; on the null path it passes zero dimensions and
continues. Allegro 4.4.1 `gfx.h` lines 304–305 defines `SCREEN_W` and
`SCREEN_H` with those null-to-zero expressions. The maintained source used
direct `gfx_driver->w/h` accesses for both calls. Replacing only those first
two width/height pairs with the historical macros produced a distinct
1,490-byte `force_create_profile` candidate (original 1,538); it remains
`DIFFER`. The first probe preserved all 63 exact functions in its older
retained context. The repeat from current `src/main.c` preserved all 64 exact
functions, including `draw_results`, with no losses. The source diff and
strict receipt are `screen-macro-current-source.diff` and
`screen-macro-current-receipt.json`.

The complete one-definition body `force_create_profile_screen_macros.c` and
`tu-context-spec.json` reproduced that current overlay byte-for-byte. The
serialized TU_CONTEXT check and promotion passed with 64 exact main functions
before and after, then the function tests, diagnostic link, and global audit
passed. This corrects a historically evidenced source behavior and compiler
context; it does not claim `force_create_profile` is a function match.
