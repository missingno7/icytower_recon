# `extractHTTPResponse` lexical/CFG batch

Diagnostic-only probes compiled with the locked TDM-2 GCC 4.4.1, `-O2`, `-g`, and x87 settings. The candidate translation units and reports are isolated here; maintained sources and recovery state were not edited.

## Results

The manual-parser control emits 924 bytes (`77dea10a…`) and is `DIFFER` at offset 14 (`0xc8` candidate, `0xcc` original); all nine other `game-httpget` functions remain `FUNCTION_MATCH`.

Replacing the first-line manual parser with the evidenced `extractLine` call emits 920 bytes (`40ee0e99…`). The first strict mismatch moves to offset 8: candidate frame allocation is `sub $0x85c,%esp`, versus historical `sub $0x84c,%esp`. The input spills are at the historical `-0x834(%ebp)` and `-0x82c(%ebp)` offsets. Strict TU results are 7/10 matches: the target differs, and the edit also changes `dumpHTTPResponse` at offset 38 and `HTTPFetchInternal` at offset 127. This is a material TU-context side effect for that source shape.

The original `j` scope is a child lexical block under the header-loop scope. Moving `j` into a nested block around the header parse matches that scope evidence, but it emits the exact same 920-byte hash as the helper-call control. Rewriting the evidenced header scan as an unbounded `for` with an explicit bound check also emits the same hash. These are deduplicated outcomes, not separate progress. Both retain the same 7/10 strict result.

A diagnostic `do { ... } while (iResponseBytesCount - i > 0)` header-loop variant emits a distinct 940-byte hash (`83d2bbdd…`), but still differs at offset 8 and retains the helper-call variant's two exact-neighbor losses. No DWARF evidence supports this loop form, so this is a negative CFG probe.

## Pass/lifetime evidence

In the 920-byte helper-call candidate, GCC stores the inlined line-reader output pointer at `-0x84c(%ebp)` (`mov %eax,-0x84c(%ebp)` at function offset `0x5c`, then reloads it at `0x2a9`). The manual-parser control has no reference to that slot and reserves 16 fewer bytes. The helper-call shape therefore creates a live pointer spill below the retained `linebuf`/`slaskbuf` areas; changing `j`'s C lexical scope does not alter this allocation or output. This locates the frame growth in register/spill allocation associated with the inlined helper path, rather than in a wider local type or an unevidenced `j` lifetime.

This evidence does not explain the historical 923-byte parser body or establish a matching source CFG. The next useful investigation is compiler pass/register-lifetime context for the inlined line reader and the changed peer functions, rather than more spelling variants of the same scope or loop.

## Artifacts

- `probe_layout.py` and `probe-results.json`: candidate identities, strict target and TU neighbor summaries.
- `helper_call_control/` and `manual_parser_control/`: candidate source, object, disassembly, strict diagnostic report.
- `j_nested_scope/`, `j_nested_scope_for_forever/`, `j_nested_scope_do_header/`: scope and CFG variants with reports.
- `../README.md`: prior interface, line, and inline-DIE evidence.
