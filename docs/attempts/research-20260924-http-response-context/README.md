# HTTPResponse line-position control

The native canonical include check was rejected: protected fldads_get_random_ad
changed only by swapping xor %eax,%eax and fldz at +41..+44. Its body was
unchanged, and the native abort restored the source.

Before compiling, predict: a canonical include padded with six blank lines
preserves every later token line. If the protected function is exact again,
line displacement caused the rejection. If the same swap remains, declaration
or include context matters beyond line position. Either result is diagnostic,
and any production change still requires native strict acceptance.

## Result

The exact-source baseline (SHA-256 9116d56f...) compiled 11/12 strict exact functions;
fldads_get_random_ad remained FUNCTION_MATCH at 192/192 bytes. The
position-preserved canonical-include overlay (SHA-256 9aa16b48...) compiled
10/12: only that protected function was lost, becoming DIFFER at the same
192-byte extent. Its source body was unchanged. Both used current definition
order, no generated prototypes, and locked TDM-2 GCC 4.4.1 at -O2 with
-fno-toplevel-reorder. The receipts are
docs/attempts/tu-context/game-fld-adspot/research-20260924-http-response-baseline.json
and
docs/attempts/tu-context/game-fld-adspot/research-20260924-http-response-position-preserved.json.
The exact overlay hashes are in identities.json; the native rejection's
instruction-level diagnostic is retained under
docs/attempts/interface-diagnostics/view_fld_adspot_HTTPResponse/.

This control rules out the six-line displacement as the sole cause of the
protected peer regression. It does not establish which include/type/compiler
effect reordered the x87 pair. No source or recovery status was promoted.
The next decision is to stop line-padding variants and seek a targeted
compiler-pass or preprocessed-declaration comparison only if it can explain
the +41 instruction ordering and preserve the exact neighbor.
