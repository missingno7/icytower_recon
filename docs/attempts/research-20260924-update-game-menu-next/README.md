# `update_game_menu` next-context probe (2026-09-24)

## Scope and strict state

Isolated supervisor research only. Read the current focused card and detailed evidence, both retained FAST body-attempt rows, interface ledger, prior interface/context/family studies, disassembly, RTL context reports, and retained TU receipts before this batch. No maintained source, tools, generated current files, or recovery ledger was changed. Historical executable is used as verifier only.

Current source/body is the accepted historical interface (`BITMAP *`, `void **`); its body hash is `9404056900fb2de60266dc528e3faef33031ea8604f737732dbda2b4353d393b`. The focused card remains `DIFFER / SOURCE_DIFFER`, `COMPILER_CONTEXT_DEPENDENCY`, `body_edit_allowed: false`. Baseline: 582 candidate bytes / 583 historical; first mismatch `+0x67` (`0x39` vs `0xb1`), 379 differing bytes; 7/10 exact CU functions. This is not a function/layout/object/CU match.

## Historical CFG / DWARF facts

- Original function: `0x417adc`, size 583. DWARF source rows place the controller path at line 147 / `+0x5c`, `ctrl` guard at `+0x63`, up check at `+0x71`, and down check at source line 154 (`is_down(ctrl)` call `+0x8e`). The fallback `is_down(&mp->ctrl)` call is at `+0x1d5`.
- Historical and candidate entry/prologue, menu scan, `draw_menu` call, and initial `ctrl` test agree through the first differing branch. At `+0x65`, historical `je` targets `+0x21c`; candidate targets `+0x1a4`. Other early branch destinations diverge too (`+0x78`: historical `+0x1f4`, candidate `+0x17c`). This is a CFG/body-shape divergence, not a branch relocation/layout-only mismatch.
- Both sides have 14 direct calls overall, but their call topology differs. Historical has two `is_down` calls (`ctrl` at `+0x8e`, `&mp->ctrl` at `+0x1d5`) and three `is_right`; candidate has three `is_down` (third `ctrl` at `+0x235`) and two `is_right`. Historical locals are `num_posts`, `old_pos`, `pos`, `return_value` (all `int`); parameters include `BITMAP *bmp`, `void **data`. Current signatures now agree. `Tmenu.data` is pointer-sized at offset `0x90`; pointer-store/interface probes had no target code effect.
- Prior evidence: omitting `draw_menu` or `build_menu_string` changes only target bytes 97 and 100, retaining 582 bytes and worsening the strict mismatch from 379 to 381; omitting `reset_menu` changes no target bytes. RTL first changed at expand for the peer omission, but this does not identify a historical cause. Typed/untyped `view_profile`, source-order swap, and historical-interface parameter variants all deduplicate with the maintained 582-byte output. Explicit `is_down` `if/else if` also deduplicated. The retained draw-menu body context replay caused no effective update-body change after call resolution.

## Bounded compiler-context batch

Because the retained peer-omission experiment proves context sensitivity, tested only two causal compiler hypotheses with a copied diagnostic probe script and locked TDM-2: disabling peephole2 (the recorded cursor-dependent scratch mechanism) and disabling unit-at-a-time (the TU/cgraph expansion model). The copied driver and all outputs are isolated here / under `build/tu-context/game-menu/research-20260924-update-game-menu-next/`.

| Variant | Target effective output | Strict target | Exact CU functions | Outcome |
|---|---|---|---:|---|
| `-O2` baseline | 582 bytes, SHA-256 `71fba24f3aada86f3eef8e0e91ed4a1bbb96b3c2c6db40caa30b9dc6b9d1adfd` | DIFFER, 379 bytes | 7/10 | Existing outcome; no gains/losses |
| `-fno-unit-at-a-time` | Same 582-byte effective target output as baseline (0 changed resolved bytes) | DIFFER, 379 bytes | 5/10 | Target hypothesis eliminated; `key_to_str` becomes CODEGEN_SIMILAR and `build_menu_string` DIFFER, so reject CU outcome |
| `-fno-peephole2` | Unique 590-byte output, SHA-256 `8b41731b04e298d894b7db4133c88a1a300bb4c73f9062f39903d7e71d0e4b67` | DIFFER, 555 bytes | 4/10 | Worse; `set_slider_value`, `set_selection_value`, `build_menu_string` lose exactness |

Baseline and `-fno-unit-at-a-time` are deduplicated for the target only; they are not equivalent whole-CU outputs. `-fno-peephole2` is a second unique target output and loses additional exact peers. Neither switch improves the target or gives a usable CU state. Historical normal `-O2` remains the best observed retained outcome.

## Blocker / next discriminator

The compiler-mode batch is exhausted. The unexplained mismatch is the extra candidate `is_down(ctrl)` continuation and resulting historical/candidate CFG difference; current interface, local types, and source-order variations are already eliminated. A future useful step needs source-backed evidence for the historical merge shape or recovered historical `draw_menu` compiler context. Do not edit this protected body or try further cosmetic boolean/flag variants without new historical evidence. Strict handoff: target remains `DIFFER`; exact peers remain the seven baseline menu functions; no match claim.

Artifacts: `compiler_probe_isolated.py`, `compiler-context.json`, `update_game_menu-rtl.json`; object inputs and retained RTL snapshots are in the corresponding unique build directory. The JSON records exact locked commands, identities, resolved candidate bytes, strict target comparisons, and pass-boundary diagnostics.
