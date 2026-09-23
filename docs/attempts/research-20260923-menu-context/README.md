# 2026-09-23 menu function context research

Scope: isolated analysis of `draw_menu`, `update_game_menu`, and the menu data output interface. No maintained source, generated current state, ledger, or sibling repository was edited. Historical bytes were read only from the original verifier fixture.

## `update_game_menu`

Current strict state is `DIFFER`, 583 historical bytes vs 582 candidate bytes, first mismatch at function offset 103. The current function card routes it to supervisor as `COMPILER_CONTEXT_DEPENDENCY`; body editing is not permitted by that card. Prior isolated probes already established that (a) changing `bmp` to the historical `BITMAP *` interface does not change emitted code and (b) changing the last parameter to `void **` plus storing `*data = m[pos].data` produces the same target instruction stream as the retained candidate.

Fresh original disassembly at `0x417adc..0x417d24` confirms the call-flow detail behind the mismatch:

- Historical `_is_down` calls occur at offsets `0x8e` (`ctrl`) and `0x1d5` (`&mp->ctrl`). Both are in the branch following the up-navigation check.
- Current candidate `_is_down` calls occur at offsets `0x8e` (`ctrl`), `0x161` (`&mp->ctrl`), and `0x234` (`ctrl`). The third is in the candidate block reached after the up-navigation underflow/wrap path.
- Original line-table addresses put the ordinary down check at source line 154. The candidate-only call is emitted in a duplicated continuation after `pos = num_posts`; it is not a missing declaration or changed parameter type.
- The retained explicit `if (is_down(ctrl)) ... else if (is_down(&mp->ctrl)) ...` overlay still differs and does not resolve the duplicate call. Cosmetic condition rewrites have no demonstrated route to the historical merged CFG.

The historical data output is a pointer store: `m[pos].data` at `Tmenu.data` offset `0x90` is written through the `void **data` parameter at stack offset `0x20`. Maintained source's `(int)m[pos].data` then `*data = ...` emits the same 32-bit store under i386, so fixing that signature/body spelling is an evidence-backed interface correction, not a machine-code match explanation.

## `draw_menu`

Fresh original disassembly confirms the historical prologue reserves `0x16c` bytes and holds `bmp` in `%esi`, `mp` in `%edi`, and `m` in `%ebx`. Current source has a candidate-only `DATAFILE *assets` local inside the `flags & 16` block; its historical function DIE has no `assets` local. The retained candidate with that declaration removed reduces stack allocation to `0x15c`, matching the historical frame size and moving the first mismatch from offset 8 to offset 16. The prior recorded follow-ups found no effective gain from changing equivalent pointer arithmetic or swapping independent `h`/`stepIn` statements. The remaining known problem is register allocation (`mp` is not retained in `%edi` in the current candidate) alongside broad code-layout differences. Do not repeat the removed-local/frame experiment.

No exact candidate was produced. These findings do not establish function, object, CU, or layout equality.

## Artifacts

- `docs/attempts/research-20260923-menu-context/update_game_menu-original-disasm.txt`
- `docs/attempts/research-20260923-menu-context/update_game_menu-candidate-disasm.txt`
- `docs/attempts/research-20260923-menu-context/draw_menu-original-disasm.txt`
- Existing supporting cards: `docs/current/functions/menu/{draw_menu,update_game_menu}.json`, `docs/current/interfaces/update_game_menu.json`, and `docs/current/local-declarations/decl_menu_update_game_menu_data.json`
- Existing retained interface evidence: `docs/attempts/research-luna-menu-interface/update-game-menu-data-parameter.md`
