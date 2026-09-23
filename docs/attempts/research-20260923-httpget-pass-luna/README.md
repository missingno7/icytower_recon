# `extractHTTPResponse` IRA and translation-unit context research (2026-09-23)

Research only. No maintained source, generated current state, recovery ledger,
accepted body, or neighboring repository was edited. The current card and
focused evidence remain `docs/current/functions/httpget/extractHTTPResponse.json`
and `docs/current/function-evidence/httpget/extractHTTPResponse.json`.

## Existing evidence not repeated

`docs/attempts/research-20260923-httpget-context/README.md` records the corrected
original-backed interface: `extractHTTPResponse` takes `const unsigned char *`
with `regparm(2)`, and `extractLine` takes `const unsigned char *` with unsigned
`last` and `c`. The helper's signature/type spellings were instruction-neutral.
The current generated card is still 924 candidate bytes against 923 historical,
first mismatch offset 14, `DIFFER`, with 9/10 strict CU functions.

The original DWARF records two inlined `extractLine` instances (call lines 97
and 107). Earlier isolated tests already tried the direct first-line helper call,
historical helper argument/local types, a nested `j` scope, an unbounded header
`for` form, and a `do` header-loop form. The nested scope and `for` forms
collapsed to the helper-call result; `do` grew the function to 940 bytes. The
first-line helper-call result previously cost two exact neighbors. Those
experiments and their locations are summarized in
`docs/attempts/research-20260923-httpget-context/lexical_cfg_batch/README.md`.

## Current declaration-context controls

The retained bodies here are complete copies of the current function; the
helper-call variant changes only the first manual line parser to
`i = extractLine(pHTTPData, iResponseBytesCount, linebuf, sizeof(linebuf));`.
Both are full `game-httpget` TU overlays compiled with the locked TDM-2 GCC
4.4.1 command at `-O2`, `-g`, and x87 settings. The default diagnostic dump
flags and no-dump control produce identical `.text` and `.rdata` section bytes
for each overlay; object hashes differ because the isolated paths alter debug
records.

| Overlay | Target status/size | First mismatch | Strict TU functions | Neighbor changes |
|---|---|---:|---:|---|
| `baseline` | DIFFER, 924 B | 14 | 9/10 | none |
| `first-line-helper` | DIFFER, 918 B | 8 | 7/10 | `dumpHTTPResponse` and `HTTPFetchInternal` lose exact status |

The full comparisons are in `build/tu-context/game-httpget/http-pass-luna-<label>-20260923/comparison.json`.
The matching probe receipts are in `docs/attempts/tu-context/game-httpget/`.
The helper-call function bytes hash to `43609dca…`, exactly matching the prior
`lexical_cfg_batch/helper_call_control` strict report; the baseline hash
`77dea10a…` also matches its prior manual-parser control. Thus the current
declaration context collapses to both prior outcomes. The earlier probe runner
reported helper code as 920 bytes, while the strict verifier consistently
measures the same bytes as 918; the discrepancy is a size-reporting convention,
not another compiler outcome. `effective_outcomes.py` also collapses the four
dump/no-dump receipts to two function outcomes, so dump generation adds no
effective code result.

## New pass and lifetime fact

The inline `extractLine` formal `pOutBuffer` has historical DWARF location lists
placing it in `%edx` during both inlined instances. The current helper-call RTL
also assigns its pseudo to `%edx`, but saves an extra copy of the first
`pOutBuffer` value in a four-byte stack spill. That spill first appears in the
`httpget.c.172r.ira` snapshot; it is not present in the preceding
`168r.asmcons` snapshot. The candidate prologue allocation grows from 2124 bytes
(`0x84c`) to 2140 bytes (`0x85c`) in `178r.pro_and_epilogue`. The additional
slot is visible as `insn 366` storing the `linebuf` pointer at frame offset
`-0x84c` in `182r.peephole2` before it is reloaded. This pinpoints the present
16-byte frame delta to register allocation and its resulting spill/layout; the
two saved input argument slots themselves match the historical `-0x834` and
`-0x82c` positions in this helper-call output.

The paired `-fdump-rtl-all` and `-fdump-ipa-cgraph` compiler dumps are under
`build/tu-context/game-httpget/http-pass-luna-rtlall-<label>-20260923/`; their
object `.text`, `.data`, and `.rdata` bytes were compared to the ordinary
diagnostic builds and are identical. This establishes a boundary between the
available RTL snapshots, not a claim that the IRA pass alone caused the spill.

The TU's peephole scratch report also changes at the helper-call boundary:
baseline `extractHTTPResponse` uses `%dx` as its selected scratch, while the
helper-call version records no scratch. Then `dumpHTTPResponse` selects `%cx`
in baseline and `%dx` in the helper-call version. The helper-call overlay loses
that function and `HTTPFetchInternal` (first differences at offsets 38 and
127); the baseline preserves both. This is consistent with the known
translation-unit peephole scratch cursor carrying between emitted functions,
but the current dump snapshots do not establish a single-pass causal proof for
both neighbor changes.

## Stop point and next blocker

The 918-byte helper-call candidate is a retained earlier outcome, not a strict
match. It matches the original helper call shape, yet the inlined output
pointer spill expands the frame and the shifted scratch context regresses two
exact neighbors. Repeating declaration spellings or `j`/header-loop scope forms
would repeat known outcomes. More useful follow-up requires a new source-backed
helper/CFG finding that removes the `pOutBuffer` spill while preserving the two
historical inline instances, or a narrower compiler snapshot around IRA and
the later scratch-cursor change. Until then, retain `DIFFER` and do not promote
either isolated body.
