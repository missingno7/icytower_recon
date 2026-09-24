# `add_floor` scratch cursor versus local eligibility — 2026-09-24

Read-only comparison of the retained `mapfloor-pass-baseline-20260924-agent` and `mapfloor-pass-invert-20260924-agent` TDM-2 `-O2` dumps. No maintained source or compiler files were changed.

The receipts show identical preceding peephole scratch choices in both complete TUs: `reset_map` none, `is_solid` SI, `get_level` none, and `getFloorData` BX. Both variants use the same function emission order and predecessor. The baseline guard then selects DI; the inverted guard selects SI. Given GCC's documented successful-choice cursor advancement, the prior TU cursor explanation is not supported by these observed prefixes.

At the guard in `.181r.csa`, both variants reach the same `get_demo` call and signed `SI` memory compare at `floor_shrink` offset `0x8c`. The compare operands are otherwise the same, but the next branch differs: baseline uses `eq` to label 129 and inversion uses `ne` to label 79. In `.182r.peephole2`, the compare has been materialized into DI for baseline and SI for inversion. This supports the local CFG/liveness eligibility set as the discriminator between these two candidate outputs.

The dumps do not include peephole2's internal `live_before` set, rejected-register list, search cursor value, or final constraint-class trace. Therefore this is a comparative inference, not a proven register rejection cause. Obtaining those exact values requires an instrumented diagnostic compiler, which was out of scope; stop here. Neither output is a match (`add_floor` is respectively 608/608 at +297 and 613/608 at +306), and the inversion remains unsuitable for promotion.
