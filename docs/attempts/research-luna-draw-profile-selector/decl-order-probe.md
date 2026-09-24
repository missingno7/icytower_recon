# Selector frame and declaration order probe

This diagnostic probe tests whether restoring the historical top-level local
declaration order changes selector register/stack allocation. It uses the
typed row-local, direct `BITMAP` candidate as its base, TDM GCC 4.4.1 TDM-2,
`-O2 -g -mfpmath=387`, and a full-TU strict comparison. It writes only to the
isolated attempt directory.

## Evidence

The original function is `0x418cd4..0x4191c8` (1268 bytes). Its main loop
lexical block spans `0x418fb2..0x419057` and `0x419060..0x419154`. The nested
`icon`/`selected` declarations are scoped to that loop; the nested `rectfill`
inline is `0x418fe2..0x418ff1` and `0x41910f..0x41913e`. The candidate already
has these row-local declarations.

The original `selected` DWARF location is EBP-0x44, the same slot used by the
prologue to save `current_profile`. This is evidence that GCC reuses storage
across non-overlapping lifetimes. Direct `BITMAP` fields and row-local
declarations were already separately tested in `README.md`.

Both original and candidate `textprintf_ex` calls write varargs through
ESP+0x28. In the original inline bitmap dispatch path, code also spills a
dispatch pointer at EBP-0x8c across argument setup; the candidate keeps its
corresponding value in a register. This is a concrete allocator difference,
but does not alone account for the entire 32-byte frame delta.

## Outcome

Changing top-level local declaration order to match the original DWARF DIE
order left the selector prologue at `sub $0x9c,%esp`, versus original
`sub $0xbc,%esp`. The selector remains 1281/1268 bytes with first mismatch at
+8. `select_profile` remains 2698/3070 bytes with first mismatch at +12.
All 11 exact profile neighbors remain `FUNCTION_MATCH`.

This rejects declaration order as a sufficient cause. It does not identify the
remaining source/CFG or allocator cause. No maintained sources, cards, queue,
or recovery ledger were changed.

## Reproduction

```powershell
python docs/attempts/research-luna-draw-profile-selector/decl-order-probe.py
```

The isolated source, object, compiler logs, provenance and full comparison are
under `build/historical_top_level_decl_order/`.
