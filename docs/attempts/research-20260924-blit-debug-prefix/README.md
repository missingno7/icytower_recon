# blit_to_screen debug-prefix investigation

Isolated research only. The accepted function-static `blit_mode` owner remains present. No maintained source, current card, or recovery ledger was changed. The baseline and all successful probes retain 64 exact functions with no gains/losses; `blit_to_screen` remains DIFFER at 1239/1415 bytes.

## Evidence and result

Original source/CFG evidence is `instruction-evidence.txt`, cross-checked against `docs/current/function-evidence/main/blit_to_screen.json` and `python tools/function_lines.py game-main blit_to_screen --source-view 2267 2283`. The first residue at +0x13 is the debug guard displacement (`74 7b` historical target +0x8f; `74 7f` candidate target +0x93). Candidate final key guard at +0x8d branches near to +0x144 (`0f 85 b1 00 00 00`); historical final key guard branches short to +0x100 (`75 71`). The candidate's longer final branch accounts for the four-byte later join shift.

Three one-factor variants were compiled with locked `tdm-2`, historical TU order, no generated prototypes, and accepted current source/body context. Bracing the final `if` and spelling it as `key[62] != 0` both emitted the same 314-instruction stream as baseline. The symbolic-key variant replaced numeric keys 56..62 with `KEY_F2..KEY_F8`; it changed the key-load operands and resolved all seven early `_key` relocations to the original raw instruction values. The locked Allegro header defines `KEY_F2..KEY_F8` as indices 48..54, while current source uses 56..62. The symbolic variant changes only `blit_to_screen`, retains all 64 exact functions and the accepted BSS owner, and leaves the +0x13 branch residue and 1239/1415 body mismatch.

The current card's `ALIGNED_FIELD_UNTYPED` classification means the raw original field alone is diagnostic. The historical source-symbol evidence and locked header enum independently support the corrected indices. This closes the early `_key` mismatch hypothesis; the remaining debug-guard displacement requires investigation of the farther mode-6 block layout, outside this prefix-only experiment.

## Artifacts

- `source-variants.json`, `accepted-source-variants.json`: body/source inputs and hashes.
- `probe-summary.json`: compiler/object/overlay hashes, peer counts, focal instruction hashes and early relocation fields.
- `instruction-evidence.txt`: compact branch and relocation evidence.
- `receipts/`: fresh whole-TU probe receipts.
- `*.log`: complete probe output, including the first rejected invocation using an obsolete body snapshot (failed before compilation because it lacked the now-accepted local `blit_mode`).

## Serialized strict acceptance

The source-backed symbolic-key body was promoted through
tu_context_task.py as blit_debug_keys_20260924. Its current-order whole-TU
check returned ACCEPTABLE with 64 exact functions before and after, zero
gains/losses and 81 byte-preserved definition islands. Promotion passed
156 function acceptance tests, the diagnostic link, and the global audit.
The generated state still marks blit_to_screen DIFFER with first mismatch
+0x13; no new function bytes were credited. The transaction is
docs/attempts/tu-context/transactions/blit_debug_keys_20260924.json.
