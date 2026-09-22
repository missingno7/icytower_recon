# dumpHTTPResponse: recovered to one register, blocked only by extractHTTPResponse

`dumpHTTPResponse` (0x405e2c, 99 bytes) was the only MISSING implementation in the project.
The candidate body is `docs/attempts/game-httpget/bodies/dumpHTTPResponse.c`.

## Evidence for the body

Line table (`tools/function_lines.py game-httpget dumpHTTPResponse --lines`):
48 prologue, 49 `fprintf`, 50 loop guard + back edge, 51 `fprintf`, 53 epilogue.
The back edge is `cmp %ebx,0x4(%esi); ja`, an unsigned compare, because `iNumHeaders` is
`unsigned int` and the usual arithmetic conversions make the `int i` comparison unsigned.
The element address is `shl $0x3` + `pHeaders` (`HTTPHeader` is 8 bytes: `pHeader` @0,
`pValue` @4). DWARF block 80170 (0x405e51..0x405e87) owns `i`, so it is declared in a brace
block rather than at function scope.

## Result

Overlay `docs/attempts/tu-context/game-httpget/dump-after-gse.json` (definition placed
directly after `getSocketError` in source, which puts it at its historical emission position
between `extractHTTPResponse` and `getSocketError`):

* candidate size 99 == historical size 99, 37 instructions == 37 instructions;
* every instruction identical except **one register**: the loop guard is
  `mov 0x4(%esi),%ecx; test %ecx,%ecx` historically and `...,%edx; test %edx,%edx` for us;
* no losses, no new implicit declarations (the unit needs `#include <stdio.h>`).

## Why the register differs, and what unblocks it

The register comes from `peep2_find_free_register`'s file-static rotating cursor, so it is
decided by how many peephole scratches earlier functions in the emission order consumed.
Measured consumption in our build: `httpGetLastModified` 0, `destroyHTTPResponse` **ax**,
`SplitURL` 0, `extractHTTPResponse` 0, then `dumpHTTPResponse` **dx** (the next register after
ax in the allocation order).

Historically `dumpHTTPResponse` gets **cx**, one step further, so exactly one more scratch was
consumed between `destroyHTTPResponse` and it. `SplitURL` is FUNCTION_MATCH and consumes none,
so the missing consumer is `extractHTTPResponse` — and the original's `extractHTTPResponse`
does contain the corresponding peephole at offset 70:

    O 70 mov -0x82c(%ebp),%edx ; 76 test %edx,%edx ; 78 jle ...

with precisely the predicted register `dx`. Our `extractHTTPResponse` (DIFFER, 918 vs 923
bytes) emits a different preheader there and allocates no scratch.

A control experiment (`dump-scratch-probe`) inserted an artificial one-scratch consumer ahead
of everything: it took `dx`, `destroyHTTPResponse` moved ax -> cx and `dumpHTTPResponse` moved
dx -> bx, confirming the cursor is a plain global rotation advanced one step per consumer.

**Conclusion.** The body is source-correct; the single residual byte difference is a neighbour
artifact of the unrecovered, ownership-AMBIGUOUS `extractHTTPResponse`. It is therefore not
promoted (the gate requires FUNCTION_MATCH, and `body_edit_allowed` is false for this card).
Recovering the `extractHTTPResponse` preheader at historical line ~76 — where the original
hoists an `iDataLeft` test before the scan loop — should make `dumpHTTPResponse` exact with no
further change to it.
