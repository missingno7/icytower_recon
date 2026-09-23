# Map/floor isolated research — 2026-09-23

## Scope and proof state

Research lane only. No maintained source, current generated state, or `src/recovery.json` was edited. `src/map.c` SHA-256 remained `247f243c3f6c5a7bc94eb1af8ec46c7750d893ccc40c3d4b363e8246c601a75a`; `src/recovery.json` SHA-256 at close: `bbb6b0b341bae6eae45268585fa493465c14e9ae0980d3950c48794cffd3a8e7`.

`getFloorData` is already `FUNCTION_MATCH` at 107/107 bytes in the current focused card and strict historical-order TU probe. Its C and relocation evidence is exact; it is protected. B009 is stale relative to current generated state: it names the old `getFloorData` mismatch, and its proposed next experiment is now satisfied. `add_floor` remains `DIFFER`, 608/608 bytes, first mismatch offset 297: historical `mov 0x8c(%eax),%esi; test %esi,%esi`, candidate uses `%edi`. No exact result was found.

## Evidence kept distinct

The historical-order baseline reports five functions, four strict function matches (`reset_map`, `is_solid`, `get_level`, `getFloorData`), and `add_floor` `DIFFER`. Whole `.text` is not equal; `OBJECT_MATCH` and `CU_MATCH` are false. The candidate object contains nine `.text` relocations and 60 relocations across sections; no unresolved text relocations. The `.data` 20-byte `floor_size_modifiers` contribution and `.rdata` 8-byte contribution compare equal. `.bss` is empty and no common allocations are present. These object/data facts do not change the function verdict.

Current declarations/evidence establish `get_demo(void)` returns the reconstructed `Treplay *`; `floor_shrink` is signed `int` at offset 140 in `Treplay`, and its field load is 32-bit on both sides. `add_floor` has only historical locals `i`, `width`, and nested `max_w`; no extra local or caller/interface fix is evidenced. Historical definition order is `reset_map`, `add_floor`, `is_solid`, `get_level`, `getFloorData`.

## Probe trajectory

1. `luna-map-baseline-20260923`: historical-order whole-TU probe. `add_floor` 608/608, first mismatch offset 297 (`%edi` vs `%esi`); all four other functions remain strict matches.
2. `luna-map-invert-floor-shrink-20260923`: inverted the `floor_shrink` condition and exchanged the semantic branches. GCC then emitted the historical `%esi` load/test at offsets 296/302, but selected a different branch target/layout; first mismatch moved to offset 306 and `add_floor` grew to 613 bytes. This is a materially new output. It establishes that GCC's register choice is sensitive to this guard's CFG/block layout. It is not proof that the source matches historical CFG.
3. `luna-map-explicit-fallthrough-20260923`: used an explicit guard/goto with shrink path falling through and the random-width path at a label. GCC canonicalized it to the ordinary candidate output: 608 bytes and the original mismatch at offset 297 (`%edi`). This rules out that label/goto spelling as a lever.
4. `luna-map-add-floor-last-context-20260923`: reordered definitions in the isolated overlay so `add_floor` is emitted first by the cgraph. The `add_floor` function bytes stayed identical to baseline (608 bytes, offset 297 mismatch); the four existing exact functions remained exact. This makes simple prior-definition/emission-order state an unlikely explanation for this register choice in the tested TU.

All probes used `tools/tu_context_probe.py` with TDM-2 `-O2`, historical `map.c` body overlays, and unique labels. The exact sources, `.o` files, full comparison receipts, and GCC cgraph dumps are archived in this directory by label.

## Stop point and next useful experiment

The local condition/CFG search produced one new effective object (the 613-byte inverted-branch form), then the explicit-control-flow form collapsed to the known output. Definition emission order did not change the target function. No source-only spelling family is currently justified. The remaining blocker is the historical allocator/block-layout coupling at the `floor_shrink` guard: reproducing the `%esi` choice with the original branch target/layout has not been achieved. Next useful work is to compare the historical and candidate RTL/register-allocation dumps around this guard, or to obtain additional original source/declaration evidence that changes the same CFG without inventing locals. Do not promote the inverted trial; it remains `DIFFER`.
