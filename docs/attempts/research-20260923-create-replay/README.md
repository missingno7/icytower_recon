# `create_replay` ownership investigation (2026-09-23)

Research only. No maintained source, generated state, recovery ledger, or production function body was edited; nothing was promoted. The current card is `CODEGEN_SIMILAR`, body edits are disallowed, size 254, six differing bytes at offsets 44–54, and the two references are blocked as unknown `.data` owners.

## Data owner evidence

Current source declares `static char replay_header[] = "ITR140";`: a mutable seven-byte object. The current COFF object gives `_replay_header` as a static `.data` symbol at offset 0, section contribution 7 bytes. The original storage card records `_REPLAY_HEADER` as a file-local/static `const char[6]` in `.rdata`, VA `0x4d7dd0`, initializer `495452313430`.

A no-body-change isolated declaration probe changed only the declaration to `static const char replay_header[6] = "ITR140";`. The resulting object has no `.data` contribution and emits `_replay_header` at `.rdata+0x330` with the six initializer bytes. `create_replay` becomes verifier `FUNCTION_MATCH` at 254 bytes; all six previously exact neighbors remain exact, raising strict function count from 6 to 7. The whole object and CU remain different. The verifier resolves all three focal references using unique-content search, not the historical symbol name; this status alone is not a robust owner proof.

An isolated diagnostic with the exact historical identifier also unchanged body shape was tested by changing the declaration and its one body reference to `REPLAY_HEADER`. It gives stronger DWARF/COFF owner resolution for the header pair at candidate `.rdata+0x330/+0x334`, resolving them to `0x4d7dd0/+4`. It changes one function-body identifier and is diagnostic only, not a repair candidate.

## Remaining ownership conflict

The `Harold` literal reference at function offset 127 is candidate `.rdata+0x99`, while the original operand is `0x4d7a7e`. If the header owner anchors the candidate section base, the header relation implies base `0x4d7aa0`; that same base maps `Harold` to `0x4d7b39`, not `0x4d7a7e`. Candidate header-to-Harold distance is `0x297` (663 bytes), while the historical distance is `0x352` (850 bytes), a 187-byte conflict. A single `.rdata` contribution base cannot satisfy both. The no-body probe's `FUNCTION_MATCH` used independent unique-content matches and did not prove this section-base relationship consistently.

Changing only `const` while leaving the inferred seven-byte array (`static const char replay_header[]`) produces a 246-byte body and a large code mismatch. Moving the historical-name declaration earlier to approximate its original DWARF declaration line leaves `.rdata`/`.text` output and the remaining conflict unchanged. Effective-output hashes deduplicate the no-body six-byte declaration and symbol-renamed diagnostic to identical raw `.text` and `.rdata`; only the internal COFF spelling and resulting owner resolution differ.

## Stop point

A source-supported data declaration explains the original `.data` relocation blocker and produces exact function bytes under content-based target resolution. Independent header-symbol binding reveals a separate same-section address conflict for the `Harold` literal. There is no robust strict candidate until replay CU string ownership and `.rdata` contribution placement are reconciled. Artifacts, full comparisons, and exact probe sources are in this directory; `ownership-and-dedup-analysis.json` records effective hashes and relocation evidence.
