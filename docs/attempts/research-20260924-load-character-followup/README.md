# `load_character` source and lifetime follow-up — 2026-09-24

Scope: checked the current focused card and attempt ledger against retained historical-body candidates, original DWARF locations, CFG evidence, and the prior historical-order probe batches. No maintained source, generated state, or recovery data changed.

## Current result

- Focused card `docs/current/functions/main/load_character.json`: DIFFER, 330 historical / 330 candidate bytes, 92 instructions each, first mismatch at +13. The current evidence report records 15 differing instruction bytes (`+13, +16, +24, +41, +53, +59, +67, +138, +178, +185, +202, +206, +248, +254, +258`); the older `load_character-finding.md` says 13, so the newer focused evidence supersedes that count.
- All 18 target relocations and direct call targets agree. Exact types also agree: `filename const char *`, `attrib int`, `param void *`, `name char *`, `buf char[1024]`, and static `count` at `0x4dd330`.
- The six current attempt-ledger records all remain DIFFER at +13. Historical-order controls retain 63/82 exact functions. Do not infer whole-CU equality from that count.

## Source and DWARF facts

- Original `filename` location list, relative to function entry: incoming EBP+8 for offsets `[0,31)`, ESI for `[31,58)`, then EBP+8 for `[58,330)`. Thus the original keeps it in ESI only to pass it to `get_filename`, then repeatedly reads the incoming stack home.
- Original `name` locations: EBX `[25,36)`, EAX `[36,66)`, EBX `[66,87)`, `[91,289)`, and `[293,330)`. `buf` is an inner-block `char[1024]` at EBP-1056. Current source and retained body have matching types/scopes, but candidate keeps `filename` in EBX and `get_filename`'s result in ESI, reversing the initial historical roles. The function then has 13 (now 15 per focused report) register-field differences.
- The retained body `docs/attempts/game-main/bodies/load_character.c` and maintained body share the same source shape: assign `name`, evaluate the ordered combined guard, declare `buf` within the guard, format/check/load/log/copy, then update static `count` on success.

## Adaptive probe decision and unique outcomes

The source-supported hypotheses that match the observed lifetime gap have already been tested under the relevant locked historical/current TU contexts:

1. Declaration order, initialized `name`, function-scope `buf`, and nested guard all collapse to the same output (`docs/attempts/game-main/load_character-finding.md`).
2. Historical/current definition order, prototype mode, and a parameter alias for late logging all deduplicate to effective identity `f896246c764546d6` (`docs/attempts/research-luna-load-character/README.md`).
3. Late filename alias and format-only alias also produce that same identity (`docs/attempts/research-lifetime-load-character-20260923/README.md`).
4. Historical-order context with retained `play` and `draw_frame`, plus a retained earlier `init_game` snapshot, remains the same target outcome and preserves 63 exact functions (`docs/attempts/research-historical-order-load-character-20260923/README.md`).
5. The only concrete remaining context lead is the immediately preceding, nonmatching `init_game` and GCC 4.4.1 peephole2 scratch cursor. Available `init_game` candidates leave the extracted scratch sequence unchanged (`init_game: si,di,ax,dx,cx,bx`; `load_character: di,ax`) and produce the same target bytes. A historically grounded predecessor or an independently justified compiler-state trace is not available (`docs/attempts/research-luna-init-game-context/README.md`).

No new source probe was run: every evidence-backed body/type/lifetime candidate already converges, and the only unresolved discriminant is upstream historical compiler context. More local variants would repeat known outcomes. Keep `load_character` DIFFER pending new evidence for the historical `init_game` body or a trace of the GCC peephole2 cursor.

Artifacts: focused card/evidence under `docs/current/functions/main/load_character.json` and `docs/current/function-evidence/main/load_character.json`; six FAST records in `docs/attempts/game-main/load_character.jsonl`; retained body and prior finding under `docs/attempts/game-main/`; historical-order receipts under `docs/attempts/tu-context/game-main/research-historical-order-load-character-*.json`; compiler dumps and overlays under `build/tu-context/game-main/research-historical-order-load-character-*` and `build/tu-context/game-main/luna-init-context-*`.
