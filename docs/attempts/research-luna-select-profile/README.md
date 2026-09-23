# `select_profile` CFG and lifetime probes

This isolated research batch starts from the prior typed late-header full-TU overlay, then changes only the complete `select_profile` definition. Each candidate compiled with the locked TDM GCC 4.4.1 TDM-2 command (`-O2 -g -mfpmath=387`). Maintained source, cards, recovery state, and the shared production ledger were not edited.

## Evidence from the oracle

- The original dispatcher subtracts scan code `0x3b`, bounds it against `0x1a`, and jumps through a switch table at `0x41b009`. The typed baseline uses an `if`/`else if` chain.
- Original create-profile flow draws the `"...and press enter."` text, an outer rectangle, and an inner fill before `get_string`; these three calls are absent from the typed baseline.
- After the loop, the original formats `Now using profile '%s'` and calls `my_alert`; the typed baseline omits this path.
- DWARF assigns `buff[256]`, `new_name[32]`, and post-loop `buf[128]` to the same frame-relative location, `DW_OP_fbreg -288`. Their lexical scopes do not overlap. The current candidate instead has one function-scope `input[256]`.

## Probe outcomes

- `switch_dispatch`: converts the existing key chain to the proven switch. It stays `DIFFER` at 2706/3070 bytes, first mismatch +12. This explains an 8-byte code-size change, not the 372-byte baseline gap.
- `missing_ui_paths`: adds the three prompt draws and post-loop notice, retaining function-scope `input[256]`. It grows to 2991/3070 bytes (79 bytes short), but its frame grows from the oracle’s `0x16c` to `0x1ec`; first mismatch moves to +8 at the frame allocation.
- `scoped_buffers_ui_paths`: adds the same paths and gives deletion, creation, and post-loop text their separate scoped buffers. GCC reuses their storage and returns to the oracle-sized `0x16c` frame. The function remains `DIFFER` at 2991/3070 bytes, first mismatch +12: candidate loads the font global at +12 while the oracle stores `ctrl` to `ESI` at +9.

All three full-TU reports preserve exactly the same 11 `FUNCTION_MATCH` neighbors. No exact gains or losses. Each reports all 17 functions, initialized data, common/BSS symbols, and relocations. No probe establishes a function, CU, or object match.

The missing UI paths and original buffer lifetimes explain most of the byte-count gap and the frame-sensitive mismatch. The residual +12 register choice and 79-byte code gap remain unresolved; matching the switch shape alone does not resolve them.

## Artifacts

- `batch-results.json`: compact strict results, effective identities, and exact neighbor set.
- `batch-summary.json`: detailed full-TU outputs.
- `run_batch.py`: reproducible batch runner.
- `overlay/profile-typed-late-header-typed.c`: typed starting body; `overlay/select_profile-retained.c`: pre-existing candidate inspected, not used because it has stale `page_size=16` and extra offset edits.
- `overlay/*.body.c` and `overlay/*.c`: three body and full-TU variants.
- `build/historical-select_profile.asm`: oracle disassembly, including the switch dispatch and missing paths.
- `build/*/comparison.json`, `build/*/build-provenance.json`, compiler logs, `.o`, `.d`, and `interfaces.aux`: strict CU evidence and build provenance.


