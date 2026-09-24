# Replay selector table and property-literal pool order

Research-only follow-up to the owner-correct lower-key selector candidate. No production source, generated current state, recovery ledger, or original assets were edited.

## get_replay_property string order

Historical relocation targets in docs/current/functions/replay/get_replay_property.json identify the original strings. Candidate section items were decoded from unit.o in the no-prototype isolated probe. The first candidate keeps source case order 2,3,4; the second changes only the independent case order to 2,4,3.

| Function offset | String | Historical .rdata offset | 2,3,4 candidate | 2,4,3 candidate |
|---:|---|---:|---:|---:|
| +0x87 | %s has wrong header version | 0x385 | 0x381 (-4) | 0x381 (-4) |
| +0x367 | Couldn't open %s | 0x34e | 0x34a (-4) | 0x34a (-4) |
| +0x394 | %s:combo=%d | 0x3ea | 0x3da (-16) | 0x3e6 (-4) |
| +0x3b7 | %s has wrong first 3 bytes of header | 0x360 | 0x35c (-4) | 0x35c (-4) |
| +0x3de | %s:score=%d | 0x3d2 | 0x3ce (-4) | 0x3ce (-4) |
| +0x40c | %s:floor=%d | 0x3de | 0x3e6 (+8) | 0x3da (-4) |
| +0x448 | Can't open %s | 0x3c4 | 0x3c0 (-4) | 0x3c0 (-4) |
| +0x46a | Couldn't create a replay object | 0x3a4 | 0x3a0 (-4) | 0x3a0 (-4) |

The historical format-literal order is score, floor, combo. Reordering the source switch's independent cases from 2,3,4 to 2,4,3 reproduces that order in candidate .rdata: score at 0x3ce, floor at 0x3da, combo at 0x3e6. This removes the prior -16 and +8 outliers; all eight references now have the same -4 displacement. Case values, returned fields, and log strings are unchanged.

The remaining four-byte displacement is unresolved. The adjacent candidate item at .rdata+0x347 is the "wb" mode string from save_replay; its historical relocation is 0x4d7cab (.rdata+0x34b), and the following Couldn't open %s relocation is 0x4d7cae (.rdata+0x34e). Candidate has "wb" at +0x347 and Couldn't open %s at +0x34a. This confirms a shared preceding pool displacement, but does not identify the missing/reordered four-byte source item before it. No padding or forced placement is justified.

## Selector table start is separate

The combined owner/key candidate still has the 83-entry compiler-generated table at .rdata+0x1bc..+0x308; original is +0x1b8..+0x304. The table is four bytes late. Its immediate candidate predecessor is the period-terminated file-selector prompt at +0x198..+0x1b9 including NUL, then alignment at +0x1ba..+0x1bb. Original bytes show the warning string immediately before the table, ending at +0x1b5, with NUL/alignment before +0x1b8. The original literal refs order prompt, delete message, warning; candidate order is warning, delete message, itr, prompt. The source-backed period-only prompt repair did not move the table. This local table-boundary issue is independent of the uniformly -4 helper string group.

## Combined overlay result

case-order-source.c is derived from the owner-correct headerrefs-source.c; its only edit is swapping the complete case 3 and case 4 bodies in get_replay_property. The four C/F/N/S selector cases and file-static uppercase REPLAY_HEADER remain present. The fresh --no-prototypes TU probe compiled successfully:

- create_replay: FUNCTION_MATCH, 254/254.
- load_replay: FUNCTION_MATCH, 1136/1136.
- get_replay_property: DIFFER, 1147 bytes, with eight literal relocations displaced by -4.
- Exact total remains 7; the other exact functions are get_sort_method, set_sort_method, hash, destroy_replay, update_file_list, plus the two listed above.
- replay_selector: DIFFER, 2493/2845. The 83-entry table remains four bytes late.

Probe receipt: docs/attempts/tu-context/game-replay/replay-selector-lowkeys-owner-case-order-noprotos-20260924.json.
Comparison: build/tu-context/game-replay/replay-selector-lowkeys-owner-case-order-noprotos-20260924/comparison.json.
Compiled object: build/tu-context/game-replay/replay-selector-lowkeys-owner-case-order-noprotos-20260924/unit.o.

## Boundary

The case-order experiment is diagnostic, not an accepted body change or CU match. It provides a source-backed explanation for the -16/+8 pair, while the common four-byte helper displacement and the separate table-start +4 remain blockers. No additional probe is justified without identifying the historical four-byte predecessor or a source/CFG-backed owner order.
