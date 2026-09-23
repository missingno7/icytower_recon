# Isolated `main.c` prototype-context probes — 2026-09-23

## Provenance

`src/main.c` has 16 contiguous generated blocks immediately before the function definitions. The first 15 blocks are byte-identical 82-prototype lists in the prior source order (block SHA-256 prefix `d59eeabf12b9`). The 16th is another list in historical DWARF definition order. `29b599f8^` had 15 blocks; `29b599f8` added the final block as part of the accepted `order_main` transaction. `tools/tu_context_task.py` rebuilds a skeleton by removing function islands, then appends a generated declaration block; it does not remove the existing generated block from the skeleton. This explains the latest accumulation. The blocks contain compatible declarations derived from reconstructed signatures; this probe did not establish that their multiplicity or order is historically evidenced.

## Strict outcomes

Every isolated variant compiled and retained **63/82 FUNCTION_MATCH**, with no strict gains or losses against the current verifier baseline. This is not a CU/object match. `play` remains `DIFFER` in every variant. No maintained source or recovery ledger was edited.

| Variant | Generated blocks retained | `play` candidate bytes | New implicit calls | Candidate object SHA-256 |
|---|---:|---:|---|---|
| Production | 15 legacy + 1 historical | 17,400 | none | `7215b4f3dc6ec64879559abf5fdb46033907ba51503342de68617992248f1d59` |
| Legacy only | 15 legacy | 17,497 | none | `afd0968ffa8cd26b2ce2017c0b6826d9c77ff750fc72660708f08f21b6791a29` |
| One historical block | 1 historical | 17,497 | none | `3bbc3b446a5826907b58df5d62bc580fdcd0599ef85b70caee6faf84b15599b2` |
| One legacy block | 1 legacy | 17,497 | none | `1ed35181b55098725cb38a10558ab71559528f437d76dc73b171629404f09448` |
| No generated block | 0 | 17,497 | `do_replay_menu`, `fadeOut` | `5adc54ef777f072ede0ecdb7382393d7731bb03ddb8167f3db8199c1a7009318` |

All non-production block variants show raw code changes in `_mangled_main`, `do_replay_menu`, `load_new_ad_image`, `play`, and `run_demo`; the 15-block variant also changes raw `init_game`. The current effective-code comparator reports no confirmed unchanged-body effective differences, but lists seven emissions unavailable for canonical comparison (`draw_results`, `blit_to_screen`, `get_string`, `init_game`, `main_menu_callback`, `play`, `_mangled_main`). Do not treat those unavailable cases as unchanged. The direct effective-identity pairwise comparison found one-vs-one legacy/historical lists identical across all emitted functions; this supports no observed single-list order effect. The generated list count can still alter outcome identity (`init_game` differs between one and 15 legacy copies).

## Mechanism evidence and limits

For one versus 15 legacy copies, source-level cgraph emission order is identical and all 82 `peephole2` scratch-register sequences are identical. In GCC 4.4.1 `init_game`’s normalized `003t.original` tree dump is identical, but `123t.optimized` changes one independent-initialization order:

- one list: `i = 1; check = 0; replay_path = 0B;`
- 15 lists: `check = 0; i = 1; replay_path = 0B;`

The corresponding `128r.expand` RTL has the same four-line reorder. This is evidence that prototype multiplicity changes compiler state before or during tree optimization for an unchanged body, without changing the observed cgraph emission order or peephole2 scratch trace. It does not yet identify which GCC declaration/UID or tree-pass ordering rule causes the result. `init_game` is in the comparator’s effective-code-unavailable list, so its hash difference is a diagnostic outcome, not an exact codegen claim.

The original `-fdump-rtl-reload` flag is not supported by the locked GCC 4.4.1 (`cc1.exe: unrecognized command line option`); supported pass dumps used here were `-fdump-tree-original`, `-fdump-tree-optimized`, and `-fdump-rtl-expand`.

## Smallest next discriminating step

Recover historical declaration visibility/order evidence for the relevant functions, then compare the compiler’s `DECL_UID`/tree-pass state at the first differing optimized-tree statement. Do not delete production prototypes or search arbitrary counts for a better match set. The experiment does not resolve the `play` mismatch, prove CU equality, or justify modifying exact functions.

## Artifacts

- Full CU/object comparison reports, objects, interfaces and DWARF for count variants: `build/tu-context/game-main/prototype-context-{16-all,15-legacy-only,1-historical-only,1-legacy-only,0-none}-20260923/`.
- Probe receipts: `docs/attempts/tu-context/game-main/prototype-context-*-20260923.json`.
- Full pass dumps for one versus 15 legacy blocks: `build/tu-context/game-main/prototype-pass-{one,fifteen}-20260923/`.
- Pass-dump variants failed twice with unsupported `-fdump-rtl-reload`; those are tooling-flag failures, not compiler/source outcomes.
