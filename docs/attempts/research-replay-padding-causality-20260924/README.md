# Replay post padding TU context probe

This is an isolated compiler experiment on the pre-promotion replay candidate snapshot. It does not describe the currently maintained replay source.

## Matched controls

All four variants start from one retained complete research TU. `replay-no-reserved.c` gives GCC implicit alignment bytes after `parent`; `replay-explicit-reserved.c` inserts `char reserved[2]` at that same point. The body-overlay pair additionally uses the same typed `load_replay` and selected-row `draw_replay_selector` definitions from the dated source files recorded in the probe receipts. The two forms have the same member offsets and object size; only the presence of the named member differs.

| Variant | `replay_selector` strict state | Effective size | CU exact functions |
|---|---:|---:|---:|
| Bare, no reserved member | DIFFER | 2465 | 6/15 |
| Bare, explicit member | DIFFER | 2485 | 6/15 |
| Typed load + selected-row draw, no member | DIFFER | 2485 | 7/15 |
| Typed load + selected-row draw, explicit member | DIFFER | 2485 | 7/15 |

The paired overlay variants have the same effective outcome identity. The bare variants have separate effective outcomes. All four reports remain diagnostic; no replay_selector candidate is a FUNCTION_MATCH.

## Compiler-pass boundary

GCC was compiled with `-fdump-tree-all -fdump-rtl-all` in addition to the locked `-O2 -g -mfpmath=387` command. The flags preserved the complete `.text` section byte-for-byte against each corresponding ordinary probe for all four variants. The raw dumps and diagnostic objects are under `dumps/`; exact input and output hashes are in `manifest.json`.

For the bare pair, replay_selector's generated basic-block counts remain equal through `replay.c.111t.reassoc2`; the first GIMPLE dump with different block counts is `replay.c.112t.vrp2` (GCC's second value-range-propagation pass): 69 blocks without the member and 72 with it. For the body-overlay pair, those counts remain equal through all emitted GIMPLE tree stages. This pins the first observed optimized-control-flow divergence to VRP2 in the bare context and shows that the typed body overlays remove the divergence in the same TU snapshot.

Earlier `original` and SSA dumps differ in generated temporary/SSA identifiers, so this is a pass boundary, not proof that VRP2 is the root cause or that the explicit field changes type identity, alias analysis, or IPA. The exact triggering value/range or tie-break remains unresolved. No inference about the promoted maintained source follows from these earlier candidate files.

## Evidence index

- `padding-research-*.json`: four retained TU receipts and strict results.
- `effective-outcomes.txt`: effective-output grouping and response diagnostics.
- `dumps/<probe>/`: raw pass dumps, diagnostic object, and extracted `.text` section for each source variant.
- `replay-no-reserved.c`, `replay-explicit-reserved.c`: matched retained TU source inputs.
- `manifest.json`: sizes and SHA-256 values for preserved evidence.
