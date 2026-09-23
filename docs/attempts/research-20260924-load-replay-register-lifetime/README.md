# `load_replay` register-lifetime follow-up

Research-only full translation-unit probes using locked TDM-2 / GCC 4.4.1
`-O2`. No maintained source, generated current state, recovery ledger, or
external repository was edited.

## Control and method

The control is the retained 8/15 owner-aligned replay TU at
`docs/attempts/research-20260924-load-replay-owner-context/property-case-order-source.c`
(SHA-256 `4a0c152a5d0821411e1e713a375fd9b8940db21de4eaacc605a760838212887f`).
The original experiment used `tu_context_probe_owner.py`, a research copy of
the probe with one input-path override (`REPLAY_OWNER_BASE`). The canonical
`tu_context_probe.py` now supports this directly with `--research-base`; a
replay of the typed-handle candidate produced the same strict 9/15 outcome at
`docs/attempts/tu-context/game-replay/load-replay-typed-handle-canonical-base-20260924.json`.
Both use the locked compiler and strict full-CU comparator. The current
`src/replay.c` was not the TU control.

Original DWARF identifies `pf` as `PACKFILE *`, `r_temp` as a 0x8cc-byte
`Treplay` at frame offset -2252, and `r`, `i`, `sum`, and `cs` as function-scope
locals; `load_replay` has no lexical blocks. The Allegro 4.4.1 header declares
`pack_fread(void *, long, PACKFILE *)`, `pack_fclose(PACKFILE *)`, and
`pack_fopen(...) -> PACKFILE *` (`third_party/allegro-4.4.1/include/allegro/file.h`).

The original code at +169 branches from the failed second `pack_fopen` to
cleanup at +1121. The baseline owner TU branches to +1133 because later code is
12 bytes longer. Original instructions and DWARF show that across the two
five-word `ccc` / `jc` read loops, `%ebx` holds `pf`, `%edi` holds the replay
pointer/array cursor, and `%esi` is the four-byte loop offset. The `void *pf`
baseline candidate swaps `%ebx` and `%edi` for those loops, spills/reloads the
replay pointer, and adds 12 bytes. The source loop form that explicitly steps
`i` by four compiled to the same effective output as the baseline.

## Outcomes

| Probe | `pf` declaration | `load_replay` | CU exact functions | Effective result |
|---|---|---:|---:|---|
| `luna-load-replay-owner-baseline-20260924` | `void *` | DIFFER, 1148/1136, first +171 | 8/15 | `305bd4b34ee3d876` |
| `load-replay-byte-cursor-owner-20260924` | `void *`, byte-offset loop spelling | same as baseline | 8/15 | `305bd4b34ee3d876` |
| `load-replay-typed-handle-owner-control-20260924` | `PACKFILE *` | FUNCTION_MATCH, 1136/1136 | 9/15 | `5b41c0b579b0bdae` |

The typed-handle outcome has 39/39 equal text relocations and all three
same-CU transfer targets independently resolve equal. It preserves the control's
eight exact neighbors: `get_sort_method`, `set_sort_method`, `hash`,
`destroy_replay`, `update_file_list`, `create_replay`, `save_replay`, and
`get_replay_property`. The emitted loop register roles now match history, and
the branch target at +171 returns to +1121. This is a strict function result in
an isolated overlay only; the complete CU remains DIFFER (neither OBJECT_MATCH
nor CU_MATCH).

A separately retained historical-root probe is not the control: typing `pf`
against maintained `src/replay.c` yielded 1136 bytes but still DIFFER. The
strict match appears only with the owner-aligned TU context, so the result is a
source-type/context interaction, not evidence that a type edit alone is a
universal recipe.

## Artifacts

- Body source variants: `load-replay-byte-cursor.c`, `load-replay-typed-handle.c`
- Research probe copy: `tu_context_probe_owner.py`
- Probe receipts: `docs/attempts/tu-context/game-replay/load-replay-byte-cursor-owner-20260924.json`, `docs/attempts/tu-context/game-replay/load-replay-typed-handle-owner-control-20260924.json`
- Canonical replay: `python tools/tu_context_probe.py game-replay src/replay.c load-replay-typed-handle-canonical-base-20260924 --research-base docs/attempts/research-20260924-load-replay-owner-context/property-case-order-source.c --body load_replay=docs/attempts/research-20260924-load-replay-register-lifetime/load-replay-typed-handle.c --order current --no-prototypes --focus load_replay --no-dumps`
- Full comparison/object/compiler dumps: `build/tu-context/game-replay/load-replay-byte-cursor-owner-20260924/`, `build/tu-context/game-replay/load-replay-typed-handle-owner-control-20260924/`
- Baseline compiler and strict report: `build/tu-context/game-replay/luna-load-replay-owner-baseline-20260924/`
- Effective outcome grouping: `python tools/effective_outcomes.py game-replay load_replay --pattern '*load-replay*20260924.json' --compact --response`

