# External peephole2 cursor witness — 2026-09-24

Research only. No verifier compiler, maintained source, current state, or proof output was changed. The script is archived here; diagnostic JSON results live in `build/compiler-research/peephole-cursor/`.

The locked TDM-2 distribution contains `cc1.exe` and headers but no buildable GCC source. `nm.exe` reports no symbols in `cc1.exe`. The local GCC 4.4.1 `recog.c` reference copy says `peep2_find_free_register` keeps a static `search_ofs`, advances it after success, and resets it after failure. The `i386.c` copy gives the visible 32-bit general register order AX, DX, CX, BX, SI, DI. Exact source provenance against locked `cc1.exe` is unproven.

`peephole_cursor_diagnostic.py` reads existing dump-enabled full-TU receipts, checks scratch-dump order against emission order, and reports the cursor immediately **after visible successful choices**. Its focus entry cursor is conditional: RTL diffs omit failed searches, unmaterialized successful calls, and rejection/liveness details. This is a context diagnostic, never a function-equality claim.

Tested on the two retained historical-order `load_character` receipts (baseline and `init_game` snapshot). Both show 59 identical visible predecessor choices. The last is `init_game` BX, placing the cursor at ordinal 4 immediately after that success. The target then visibly chooses DI and AX, yielding post-choice ordinals 6 and 1. A hidden failed search could reset the actual entry cursor, so 4 is not proven at target entry. The target stays DIFFER, 330/330 bytes, first mismatch +13; the receipts retain 63/82 exact peers.

The same baseline reports no visible scratch choice in `handle_player_collision_original`. Its EAX/EDX reversal at +205 has no observed direct persistent-cursor path and needs candidate pass-boundary evidence before calling it peephole2-dependent.

Reproduce without compiling:

```powershell
python docs/attempts/research-20260924-peephole-cursor-diagnostic/peephole_cursor_diagnostic.py docs/attempts/tu-context/game-main/research-historical-order-load-character-baseline-20260923.json docs/attempts/tu-context/game-main/research-historical-order-load-character-init-snapshot-20260923.json --focus load_character --output build/compiler-research/peephole-cursor/load-character-comparison.json
```

An exact locked-compiler trace needs an instrumented compatible `cc1` copy or a symbol/debug map for debugger breakpoints at `peep2_find_free_register`; current dumps cannot reveal `search_ofs`, `live_before`, and rejected registers. The smallest source-side discriminator is a historically supported `init_game` candidate that changes predecessor scratch choices while preserving target CSA. None is currently retained, so no new source compile was justified.

