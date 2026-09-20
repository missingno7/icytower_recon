# Terminal same-CU branch relaxation

A real `order_fld_adspot` trial exposed a 26-to-23-byte wrapper change.
`fldads_get_local_filename_from_url` has an independently resolved, identical
21-byte prefix. Its final near `JMP` (`e9defeffff`) becomes short `JMP` (`eba9`).
Both target `fldads_get_local_cache_name`. A hypothetical short branch at the
historical site needs displacement -287, outside signed-byte range.

The verifier records raw `DIFFER` and workflow `BODY_MATCH_LAYOUT_BLOCKED`.
It prohibits body edits and generic exact promotion. The layout proof is limited
to this terminal transfer, rechecked against the original PE bytes and decoded
candidate boundaries. Short same-CU conditional transfers are also independently
resolved; unknown targets, ambiguous entries and unsupported encodings fail closed.

The automatic retry still failed correctly: `fldads_load_cache_from_csv` has
an unresolved literal relocation at +88 despite equal 282-byte extents. No exact
neighbor exception covers that mismatch. The worker restored the complete source
and retained the supervisor block. No function or source-order promotion resulted.
See [captured evidence](attempts/terminal-branch-relaxation.json) and the full
[worker history](attempts/mechanical-runs/20260920T202619114253Z.jsonl).

Ten regression tests cover short/near transfers, wrong targets, byte-equal wrong
bindings, ambiguous entries, unsupported encodings, changed prefixes, reversed
relaxation and near-range self-loops. Raw function comparison is never normalized
across instruction widths.
