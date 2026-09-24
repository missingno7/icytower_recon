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

This initial blank-line result was not a valid line-position control; the corrected experiment and outcome are recorded below. It does not establish which include/type/compiler
effect reordered the x87 pair. No source or recovery status was promoted.
The next decision is to stop line-padding variants and seek a targeted
compiler-pass or preprocessed-declaration comparison only if it can explain
the +41 instruction ordering and preserve the exact neighbor.

## Correction to line-position control (before new compilation)

The original position-preserved.c input kept its lines, but
tools/tu_context_probe.py layout() collapses runs of three or more blank
lines. The actual compiled overlay moved fldads_get_random_ad from line 181
to line 175. Therefore the previous 11-to-10 result does not rule out line
displacement as a cause; the preceding conclusion is superseded.

prepare.py now also emits position-comments.c: six comment-only lines replace
the six removed typedef lines. Comments carry no C tokens, and the layout
normalizer does not collapse them. Before compiling, compare the actual
baseline and candidate overlay line numbers. If equal and the exact neighbor
returns, line position is supported. If equal and it still regresses, line
position alone is ruled out. A failed line-position check invalidates this
control and must not be interpreted as compiler evidence.

## RTL divergence probe prediction (before compilation)

The true position-preserving comment control kept the compiled
fldads_get_random_ad definition at line 181 in both overlays. It still
produced the same effective output as the collapsed-blank-line include:
10/12 exact functions, the one exact neighbor lost, four bytes reordered at
+41..+44. Thus line displacement alone is ruled out.

A fresh diagnostic compile will add only -fdump-tree-optimized and
-fdump-rtl-all to both exact compiled overlays. First verify that these flags
leave every function instruction stream, relocation tuple, and strict status
unchanged. If they do, compare the optimized tree and successive RTL dumps
for fldads_get_random_ad. An optimized-tree difference puts the mechanism at
or before tree optimization; identical optimized tree with a later RTL
difference narrows it to RTL/code emission. If the flags alter output, stop:
the pass dumps cannot support a causal inference.

## Tree-pass discrimination (before compilation)

The optimized-tree dump already swaps the two independent initializations in
fldads_get_random_ad: baseline has i = 0 before fCumulativeProbability = 0.0,
and canonical-include context has the reverse. RTL csa and peephole2 retain
that order. Compile both authentic overlays with -fdump-tree-all added solely
for diagnosis; verify all effective function/relocation outcomes are unchanged.
Then find the first tree pass whose normalized focal statements differ. If the
first GIMPLE dump differs, the declaration/front-end context created the order.
If an intermediate pass first differs, that pass is the next causal target.
This test does not make either source variant historically acceptable.


## Final bounded result and next decision

The comment-padded input and the baseline both place
fldads_get_random_ad at line 181 in the actual compiled overlays. The
comment-padded canonical include still loses only that exact function:
11/12 -> 10/12, 192-byte extent unchanged, first mismatch +41.
It has the same effective instruction SHA-256
947830cc4c84143de8b5b8a2d7ebb1848f5c416d6554226bdfa7e53b32cbe4f6
as the collapsed-blank-line candidate; baseline is
36d6f67019448b1a4ab8dc607f6cde15caa8ecb320b7024a56c04d72e2c8f648.
The only differing instruction region is the order of xor eax,eax and fldz
at +41..+44. This valid control rules out line displacement as the sole
cause. The research input identities are in identities.json; the strict
receipt is
docs/attempts/tu-context/game-fld-adspot/research-20260924-http-response-position-comments.json.

The diagnostic flags (-fdump-tree-all and -fdump-rtl-all) left every
function's instruction stream, relocation tuples and strict status equal
to the corresponding no-dump compile. The locked compiler emitted 90 common
tree pass dumps and 55 RTL dumps in each cohort; full dumps remain under the
two build/tu-context/game-fld-adspot/*-all-tree-passes directories.
At 004t.gimple, both bodies put the float initialization before the integer
initialization. The first tracked PHI-order split is at 023t.ssa:
baseline fCumulativeProbability then i, canonical include i then
fCumulativeProbability. By 123t.optimized, the baseline executes i = 0
before fCumulativeProbability = 0.0, while the include executes the reverse.
The 181r.csa and 182r.peephole2 dumps retain this ordering. This identifies
a declaration-context -> SSA PHI order -> instruction order trajectory; it
does not prove that the header is the historical declaration location or
identify the first compiler-internal cause before SSA. The compact pass
trajectory is tree-init-order.json; extraction and comparison scripts are
retained here.

Next decision: keep the current exact type-view source. The canonical include
still regresses fldads_get_random_ad under the native strict gate, and no
historically supported compensating context is known. More line padding or
cosmetic source spellings are closed. This is a diagnostic result, not a
recovery speedup or function-match credit.
