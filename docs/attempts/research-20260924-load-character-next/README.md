# `load_character` current-order follow-up — 2026-09-24

Isolated source/TU probes only. Maintained `src/`, generated current state, `src/recovery.json`, and accepted bodies were not edited. Both probes use locked TDM-2, `-O2`, current source order, no probe-added prototypes, and the same retained TU baseline.

## Results

| Probe | Hypothesis | Candidate | Strict result | Effective output |
|---|---|---:|---|---|
| `luna-load-character-next-bmp-positive-success-20260924` | Express BMP load success as positive branch with failure in `else`, matching success-first source/line possibility | 315 B | DIFFER; 63/82 exact functions, 0 peer losses | `fd91fe0e9414981e` |
| `luna-load-character-next-exists-early-return-20260924` | Replace `if (exists(buf)) { ... }` with `if (!exists(buf)) return 0; ...` | 330 B | DIFFER; 63/82 exact functions, 0 peer losses | `f896246c764546d6`, same as established baseline class |

The existence-guard form collapses to the known register permutation: 15 differing offsets, first +13, all 18 relocations equal. Positive BMP-success nesting creates a distinct and substantially shorter stream; it does not approach equality. Neither changed code in unchanged-body neighbors or gained/lost exact functions.

## Evidence and blocker

The focused card/DWARF establish the exact declared types and scopes: `filename const char *`, `attrib int`, `param void *`, function-scope `name char *`, inner-block `buf char[1024]`, and a function-static `int count`. These agree with the retained body, so type coercion variants lack historical evidence. Earlier declaration-order, initialized-pointer, buffer-scope, nested-guard, and filename-alias probes already dedupe to baseline output. The two new CFG probes therefore test the remaining source-supported branch/guard possibilities without repeating those forms.

The candidate still allocates `filename`/`name` roles oppositely to the original. Existing pass studies show current and retained `init_game` snapshots produce the same target RTL/liveness and scratch sequence; GCC dumps do not expose the peephole2 search cursor state. A historically grounded `init_game` body or instrumented GCC 4.4.1 cursor trace is required to discriminate that context hypothesis. Keep the function DIFFER pending such evidence.

## Artifacts

- `prepare.py`, `run_probes.py`
- `baseline-body.c`, `bmp-positive-success.c`, `exists-early-return.c`
- `summary.json`
- Per-probe strict comparisons and pass dumps under `build/game-main/`; receipts under `receipts/`.
