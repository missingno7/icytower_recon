# `load_character_bmp` research handoff

## Strict status

Current maintained source checked with `python tools/check_function.py game-custom load_character_bmp`:
`DIFFER / SOURCE_DIFFER`, 1993 candidate bytes vs 1992 historical bytes, first
mismatch at function offset `+0x86` (historical VA `0x403252`, candidate byte
`f1`, historical byte `e3`). The locked TDM-2 GCC 4.4.1 `-O2 -g
-mfpmath=387` scratch verifier independently returned `DIFFER` for all tested
variants. No candidate reached `FUNCTION_MATCH`; none was promoted.

## Unique outcomes

The batch in `probe.py` compiled the current source plus two independently
specified control-flow hypotheses: share the first open-failure NULL epilogue;
and route every NULL return in this function to one shared epilogue. All three
produced the same 1993-byte target function (same function-text SHA-256), same
first mismatch, and the same function status. Their complete object hashes
differ only because the scratch source/line records differ. Thus the batch has
one unique effective machine-code outcome.

An earlier return-form experiment in `docs/experiments/custom-return-flow-trials.json`
also tested four combinations of returning `bmp` vs `NULL` at the two failed
bitmap loads. Every case retained the same first mismatch at `+0x86`; candidate
sizes ranged from 1965 to 2004 bytes. These historical scratch trials are not
current acceptance evidence.

## Evidence and blocker

The focused current function card records 55 historical branches, 7 indirect
control-flow instructions, 23 relocation mismatches, and 5 unaligned/untyped
literal diagnostics. The first historical `fopen`-failure branch at `+0x84`
targets an interior instruction at `+0x56d`; current source compilation sends
that branch to the shared return epilogue at `+0x77b`. This is consistent with
the recorded `SOURCE_CONTROL_FLOW_SHAPE` classification, but the address alone
does not identify the missing original source construct. There are no listed
ownership or interface prerequisites, and the historical CU's complete source
is unavailable. No exact candidate is supported by this investigation.

## Artifacts

- `probe.py`: reproducible isolated batch; writes only under `build/research-20260924-custom-bmp/` and this attempt directory.
- `results.json`: compiler/toolchain/fixture identities, per-variant strict statuses, first differences, and function-byte deduplication.
- `docs/current/functions/custom/load_character_bmp.json`: current focused DWARF, branch, call, and relocation evidence (read only).
- `docs/experiments/custom-return-flow-trials.json`: earlier null/bmp return-form trials (read only).
