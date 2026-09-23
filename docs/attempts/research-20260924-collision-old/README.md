# `_old` IRA and lifetime follow-up — 2026-09-24

Scope: replay the locked GCC 4.4.1 IRA diagnostic against the retained `handle_player_collision_old` body in an isolated current-order TU. No maintained source, generated state, or recovery data changed.

## Result and deduplication

- Control receipt: `docs/attempts/tu-context/game-main/collision-old-ira-baseline-20260924.json`; target remains DIFFER, 910/894 bytes, candidate frame `0x4c` vs original `0x3c`. The 63 exact functions are preserved; `new_game` and `run_demo` remain exact.
- IRA flags are diagnostic-only: target instruction bytes match the no-dump control. Dump: `build/tu-context/game-main/collision-old-ira-20260924/main.c.172r.ira`; object hash `3220174a554b4ae910a73ab9010fae1952765a0e80907d5ac687c756d52bb07b`.
- A source-backed cached-`x,y` probe (`collision-old-cached-xy.c`) reused the already computed converted coordinates for direction comparisons. It emits the same target instruction bytes as the retained-body control and is deduplicated. Receipt: `docs/attempts/tu-context/game-main/collision-old-cached-xy-20260924.json`; 63 exact neighbors remain, including `new_game` and `run_demo`.

## Declaration, RTL, and live-range facts

- Historical DWARF locates `dX` in EDI only at function offsets `[56,107)`, `[333,338)`, `[472,490)`. The initial range ends well before the first `is_solid` call at +142. Historical `lastX` uses ECX around midpoint-x and `lastY` is mostly EBX; `dY` and `midX` have stack homes, while `midY` uses ESI over broad call/sweep ranges. Details and CFG are in `docs/attempts/research-20260923-collision-old/README.md`.
- In candidate RTL, `lastX` is fixed to EDI and `lastY` to EBX at entry. After converting x, GCC subtracts it from a copy of `lastX` in CX. The absolute-value branches write the result to the compiler frame home `-60(%ebp)` (`-0x3c`) at insns 325/326 before the branch join; midpoint-x later reloads it at insn 328. This memory home is already present in IRA input RTL, so calling it an IRA spill is inaccurate.
- IRA names the value `dX.1668`, pseudo r66 / allocno a53. Its ranges are `[320..321]` and `[329..355]` before compression, `[118..119]` and `[124..131]` after. It is short-lived across those split regions, not one pseudo live from entry through the later midpoint calculation. Its interference list is r79 (`lastY`), r76/r75 (live player/field values), r58 (`dY`), r78 (`lastX`), r85 and r77; no hard-register conflict is reported. The frame slot therefore originates before IRA's allocation decision, and these diagnostics do not identify a simple hard-register shortage as the cause.
- Original disassembly directly keeps the initial delta in EDI through its sign correction and midpoint preparation; original `lastX` is in ECX. This is consistent with a source/tree/RTL difference in how the delta's lifetime/home is represented, rather than evidence that a cosmetic local rename can redirect allocation.
- Collision-family note independently records the neighboring `_vector_2` signature: original loads `lastY` into EDI early while candidate delays it. That is useful family context but does not establish a shared cause for `_old`'s `dX` home (`docs/attempts/research-luna-collisions/collision-family-findings.md`).

## Disposition

No concrete predecessor-context or declaration-level perturbation is supported by these observations. The coordinate-reuse hypothesis is byte-identical, and no additional source or register-spelling probe is warranted. Keep `_old` DIFFER; blocker is the pre-IRA frame-home construction for `dX` without source/declaration evidence explaining why original GCC kept the first lifetime in EDI. Artifacts include `collision-old-cached-xy.c`, both receipts, and the IRA dump above.
