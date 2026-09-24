# `select_profile` scalar lifetime probe

## Question

Does narrowing the lexical lifetime of the loop-only scalar locals make GCC assign `bgbmp` to the historical frame slot? The retained baseline already has the correct 0x16c frame and `%esi` capture for `ctrl`, but writes `bgbmp` at `[ebp-0x128]`; historical code writes it at `[ebp-0x130]`.

## Evidence

The historical function DIE puts `selectedProfile`, `done`, `old_font`, `offset`, `ctrl_wait`, and `bgbmp` under the function scope. `bgbmp` is at `ebp-0x130`; the recorded neighboring slots include `old_font=-0x140`, `selectedProfile=-0x13c`, `done=-0x138`, `offset=-0x134`, and `ctrl_wait=-0x128`. The three local character arrays have narrower lexical blocks and reuse `-0x120` in non-overlapping regions. The retained candidate's first bitmap store is at +62, to `-0x128`, so the +64 mismatch is the displacement field.

Two source-only diagnostic variants narrowed the scope of (a) `kp`, `done`, and `ctrl_wait` to the control loop, and (b) `ctrl_wait` alone to the loop. Both compiled as the full `game-profile` CU with the locked TDM-2 command and were strictly compared. Each still reports all 17 functions and the exact same 11 `FUNCTION_MATCH` neighbors as baseline. Both remain `DIFFER`, 3115 bytes vs 3070, with first mismatch +64. The frame remains 0x16c and `bgbmp` remains at `-0x128`. GCC did change later scalar instruction scheduling for these artificial scopes, so the probe was discriminating; neither scope change affects the allocation at issue. These artificial narrower scopes also disagree with the historical DIE scopes, so they are allocator-response probes rather than source candidates.

The full-TU RTL dump under `build/rtl_dumps/` records GCC's `expand`, `ira`, post-reload, stack, and final passes for the corrected baseline. Its object hash differs from the retained reference artifact because this diagnostic invocation used a differently named source path (debug metadata); code bytes at the early prologue match the retained baseline. The earlier focused report remains the strict comparison evidence.

## Result

No strict candidate. The scalar lifetime/scoping hypothesis is not supported as the cause of the `bgbmp` slot mismatch. No production file, current card, recovery status, or shared ledger was edited. A next useful direction would require source-backed evidence for a differing compiler-visible lifetime or broader compiler context; replaying loop-only scope changes is exhausted.

## Artifacts

- `results.json`: labels, sizes, first mismatch, function counts, exact-neighbor list, object/CU verdicts.
- `loop_scope_all.c`, `loop_scope_ctrlwait.c` and paired `.body.c` files: isolated full-TU probes.
- `build/<label>/comparison.json`, `build-provenance.json`, compiler logs and COFF objects: strict full-CU evidence.
- `build/rtl_dumps/allocator_dumps.c.*`: locked compiler pass dumps from the corrected baseline.
