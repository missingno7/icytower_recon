# Small `main.c` layout context review (2026-09-24)

This review covers `check_dir` and `load_new_ad_image` against the accepted
`src/main.c` and the current focused function cards. No maintained source,
generated current state, recovery ledger, or compiler flags were changed.
There is no supported source variant to compile for either function: both are
`FUNCTION_MATCH` / `BODY_MATCH_LAYOUT_BLOCKED`, and both cards set
`body_edit_allowed: false`. Any function-body experiment would violate that
gate. The existing source-order receipts and focused reports already provide
the independent context comparisons; repeating those receipts would not add a
distinct effective-output candidate.

## `check_dir`

- The 103-byte body matches exactly after resolving relocations. Its four
  direct calls and its references to `.rdata` and the `num_chars` BSS symbol
  have no unresolved ownership prerequisites. `for_each_directory` invokes
  it as a callback; the card records no callee-interface blocker.
- Its historical and candidate emission positions are both 74. The immediate
  predecessor is `load_character` in each, but that predecessor is still
  `DIFFER`, so the historical exact prefix has not been reproduced.
- The sole call-layout issue is `check_dir+0x1b` to `log2file`. The retained
  isolated historical-order comparison puts `log2file` at candidate offset
  28352 and `check_dir` at 37812, a 9460-byte gap; the original gap is 9580
  bytes. The interval is 120 bytes shorter, explained by `init_game` being
  122 bytes short with two extra bytes of inter-function padding. Other
  functions in the interval have matching sizes. Thus this is not a CFG,
  callback ABI, or data-owner problem in `check_dir`.
- The earlier historical-order contexts retained 63/82 exact functions and
  the same target placements. The separate local-static probe lost one exact
  peer and did not change the layout cause. No additional variant can be
  justified without a source-evidenced `init_game` layout repair; preserve the
  63-peer exact set.

## `load_new_ad_image`

- The 100-byte body matches exactly. Its CFG is a null check followed by
  logging, optional bitmap destruction, bitmap loading, and pointer
  assignment. Four direct calls resolve; there is no indirect flow or data
  relocation mismatch. Its global pointer declarations agree.
- Historical and candidate position are both 80. The immediate predecessor
  `run_demo` matches exactly, but the prefix is not exact. The only body
  transfer mismatch is the call to `log2file` at offset `0x21`: its resolved
  target is correct, while the relative displacement is -33913 historically
  and -32913 in the candidate. The candidate caller/callee gap is 1000 bytes
  shorter across the intervening TU region. That cannot be changed from this
  protected body.
- The interface card identifies one independent blocker: the return aggregate
  for `fldads_get_random_ad` is 16 bytes in both declarations, but three
  pointer members differ in `const` qualification. This does not alter the
  already-matching call bytes and is not evidence for changing this function.
- The retained historical-order probe preserved the 63 exact functions,
  including `new_game`, `run_demo`, and this function, without moving the
  relative call target enough to resolve the layout. Existing declaration
  multiplicity/order probes were deduplicated to the same 63-peer output.
  Further context testing needs an evidenced change in the intervening emitted
  region and an independent repair of the callee aggregate interface.

## Result

No exact candidate body or probe receipt was produced because no legal,
source-backed body/context variant remains for these protected exact bodies.
The outstanding work belongs to `init_game` interval layout for `check_dir`,
and intervening `main.c` placement plus the `fldads_get_random_ad` interface
for `load_new_ad_image`. Keep both current function claims and all 63 exact
peers intact.
