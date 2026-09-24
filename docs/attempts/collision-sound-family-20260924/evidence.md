# Collision sound family data-reference study (2026-09-24)

Scope: `src/main.c` functions `handle_player_collision_original`, `_old`, `_combo`, `_vector_2`, `_vector`. No maintained source, current cards, recovery ledger, or queue was edited.

## Historical reference proof

The PE's DWARF global table places `combo_sound` at `0x4dd280` and `sounds` at `0x4dd2e0`. Each original collision sound argument loads the absolute dword at `0x4dd300`, which is `sounds + 8 * sizeof(SAMPLE *)` (`sounds[8]`), not `combo_sound[0]`. This was checked from the original EXE's symbol-specific disassembly:

| Function | Historical sound load(s) |
| --- | --- |
| original | `0x407f9c: mov 0x4dd300` |
| old | `0x408200`, `0x408330: mov 0x4dd300` |
| combo | `0x408724`, `0x408850: mov 0x4dd300` |
| vector_2 | `0x408bb4: mov 0x4dd300` |
| vector | `0x40902c`, `0x409088: mov 0x4dd300` |

The current source has seven `combo_sound[0]` sound arguments in these five functions (source lines 3764, 3833, 3866, 3911, 3972, 4022, 4072); the first six are spaced forms and the final one is compact. `evidence/census/globals.json` records the original global addresses above. This is a direct historical address/type derivation, not a behavioral inference.

## Isolated probe

Created retained source `all_sound_refs_to_sounds8.c` by changing only those seven collision-family expressions to `sounds[8]`.

- SHA-256: `d9b4acd9d1545f7ad1719255c11ff2b1e9da63d115077c28c62db68344a88e37`
- Unique TU probe: `python tools/tu_context_probe.py game-main src/main.c collision_sound_family_all_sounds8_20260924 --order current --no-prototypes --no-dumps --research-base docs/attempts/collision-sound-family-20260924/all_sound_refs_to_sounds8.c`
- Result: compile OK; 63/82 FUNCTION_MATCH before and after; no gains or losses; all five collision functions remain DIFFER. The comparison identifies all seven `_sounds` relocations with addend 32, resolving to `0x4dd300`. Raw instruction bytes are unchanged; effective resolved code changes in only these five bodies. No output variants were duplicated.
- Retained full comparator: `build/tu-context/game-main/collision_sound_family_all_sounds8_20260924/comparison.json`.

## Transaction recommendation

Safe source-backed correction candidate: apply `combo_sound[0]` -> `sounds[8]` at all seven historical collision-family call sites in one serialized `game-main` TU source transaction. This repairs the pointer owner/addend evidenced by the original absolute references. It does not establish FUNCTION_MATCH: the five functions still differ substantially for independent body/codegen reasons (candidate sizes original/old/combo/vector_2/vector = 449/961/1381/1057/1021 bytes vs historical 456/894/1390/1086/1071). Therefore retain every current DIFFER verdict, and do not treat this study as promotion evidence.


## Gate-ready transaction preparation (not planned/applied)

A `tu_context_task.py`-compatible research spec is at `transaction-spec.json`. It names `game-main` / `src/main.c`, `order: current`, `prototypes: none`, all five retained body paths, and the source-backed evidence above. It intentionally has not been passed to the production planner, and no production task was begun or applied.

Each retained file is one complete definition extracted from `all_sound_refs_to_sounds8.c`. A mechanical comparison against its maintained `src/main.c` definition verified exact equality after replacing only `combo_sound[0]` with `sounds[8]`; the edit counts across original/old/combo/vector_2/vector are 1/2/2/1/1, seven total. `retained-body-manifest.json` records the line, byte size, retained SHA-256, and maintained-body SHA-256 for each function, plus the probe/spec hashes. Transaction-spec SHA-256: `7a82c24ca3220af7bfa1bba36b9832a5065b56bf1adb67fa2860ca34912f1257`.
