# Replay selector interface research

Research-only overlays for the current `draw_replay_selector` interface prerequisite. No maintained source, generated current state, recovery ledger, accepted body, or oracle was changed.

## Current interface evidence

- Current task: `docs/current/interfaces/draw_replay_selector.json`, `TYPE_LAYOUT_CONFLICT` / `TYPE_LAYOUT_BLOCKED`.
- Historical and candidate function signatures agree: `void draw_replay_selector(BITMAP *, Treplay *, Treplay_post *, int, int, int, int, int)`. Both `draw_replay_selector` and `replay_selector` use the same i386 C ABI pointer/int slots; `replay_selector` has two in-CU calls to the draw helper.
- Historical DWARF (`evidence/census/dwarf-dies.jsonl`, struct DIE 221319) records an unnamed 24-byte structure with fields: `full_path` (`char *`, offset 0), `directory` (`char`, offset 4), `parent` (`char`, offset 5), `version` (`int`, offset 8), `score` (`int`, offset 12), `floor` (`int`, offset 16), `combo` (`int`, offset 20). Bytes 6–7 are implicit alignment padding. There is no `reserved` member.
- Maintained `src/replay.c` instead declares a tagged structure and inserts `char reserved[2]` at offset 6. This yields the same size and offsets but a different complete DWARF type. The generated `include/recovered/Treplay_post.h` has the seven historical members and is structurally correct.
- The same local typedef governs the global `itr_file_list[1024]`, `update_file_list`, `my_strcmp`, `draw_replay_selector`, and `replay_selector`; removal of the explicit field leaves element stride 24 and common allocation `_itr_file_list` size 24,576 bytes.

## Isolated compiler experiments

All overlays used locked TDM-GCC 4.4.1 TDM-2 at `-O2 -g -mfpmath=387 -DALLEGRO_STATICLINK`, the same include roots as `game-replay`, and were compared against the original replay CU. Artifacts retain copied candidate sources, objects, dependency/auxiliary files and full comparison JSON.

| Overlay | Type declaration change | `.text` bytes / SHA-256 | Key result |
|---|---|---|---|
| `with-reserved` | Copied current declaration | 10,700 / `a5f7d730fdc6251991a09db64b8a0af748083e631d7aac729d9d3c9a18ee8c37` | Control; 6/15 `FUNCTION_MATCH` |
| `no-reserved` | Remove only `char reserved[2]`, retain tag | 10,680 / `a1e3e978055b3a785613fdc65eecc5678623bde55a0cc02cebe404405fa5b0bf` | `draw_replay_selector` bytes unchanged vs control; `replay_selector` shrinks 20 bytes; 6/15 exact |
| `anonymous` | Remove the field and structure tag | 10,680 / same as `no-reserved` | Same effective `.text` and per-function instruction bytes as `no-reserved` |
| `anonymous-stddef` | Add `<stddef.h>` to the anonymous/no-field form | 10,680 / same as `no-reserved` | Header inclusion alone has no observed code effect |
| `header` | Replace local type with generated `Treplay_post.h` | 10,700 / same as control | Correct complete type, but reverts code to control output |
| `inline-header` | Inline the generated header contents at the type site | 10,700 / same as control | Same result without an include boundary |
| `one-assert` | Anonymous/no-field type plus one generated-style size assertion typedef | 10,700 / same as control | One extra typedef declaration is sufficient to reproduce control `.text` |
| `extra-typedef` | Anonymous/no-field type plus one unrelated `typedef char unrelated_decl` | 10,700 / same as control | An unrelated typedef also reproduces control `.text` |

This is a concrete GCC/TU declaration-context effect: the correct anonymous type alone changes full `.text` and the caller `replay_selector` by 20 bytes even though every field offset and array stride stays the same; an added type-only declaration restores the control bytes. It does **not** establish which historical compiler state caused the original result. The generated header's assertion typedefs therefore have measurable compiler impact in this CU, despite emitting no runtime code.

## Strict proof and ownership boundaries

- `draw_replay_selector` remains `DIFFER` in every overlay; no strict function win emerged. Its candidate function instruction bytes are identical across the control and no-field forms.
- All variants retain the same six strict functions, with no exact-function loss or gain. `replay_selector` remains `DIFFER` in both structural-type forms.
- The two `_draw_replay_selector` caller relocations remain present. Functional relocation target/type multiplicities are unchanged; relocation offsets move with the 20-byte caller shrink. The two fewer records in the anonymous/header variants are `.debug_str` relocations only.
- Common allocations are unchanged: `_sort_method` and `_num_itr_files` 16 bytes each, `_itr_file_list` 24,576 bytes. `.data` raw bytes stay 8 bytes with SHA-256 `83e3a14327e284be14bd9a308b7a7b032e4a424ad1b5471f2944256592ce57d4`.
- `.rdata` remains 832 bytes, but its raw hash changes between declaration variants (for example control `4d6daf214b5f7ee3063096069aa335367642ca6bd0d46dc968a147afd777faa8` vs no-field `02cd769a90e4da9c3f4b411c9b63c19f3d1bd4815265cf91a7a06b2c1cfa0d48`). Its relocation multiplicities remain equal. This is not an object or CU match.
- Every full comparison reports `object_match=false` and `cu_match=false`. `.text` equality alone is not accepted as object equality.

## Stop point

The local structural hypothesis is resolved: the two-byte member is invented padding; the generated header is layout-accurate. Further spelling variants have converged or toggled only the already observed declaration-context output. The remaining issue is how to express/use this corrected historical type while preserving or reproducing the required GCC 4.4.1 whole-CU context; it is not a missing `draw_replay_selector` prototype or caller ABI mismatch. No candidate is ready for production promotion from this isolated lane.

## Artifacts

- `outcome-summary.json`: compact statuses, section hashes, relocations and allocation summaries.
- `with-reserved.c`, `no-reserved.c`, `anonymous-no-reserved.c`, `anonymous-stddef.c`, `header.c`, `inline-header-content.c`, `anonymous-one-assert.c`, `anonymous-extra-typedef.c`: isolated source variants.
- Matching `.o`, `.d`, `.aux`, `*-comparison.json` files: raw compilation products and complete CU comparisons.
- `anonymous.dwarf.txt`: DWARF dump for the no-field anonymous declaration.
