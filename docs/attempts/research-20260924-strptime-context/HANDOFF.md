# `_strptime` context research handoff

Scope: diagnostic research for `game-strptime/_strptime`. No maintained source,
generated current state, recovery ledger, or external repository was changed.

## Current strict result

The focused card remains `DIFFER`, `STACK_FRAME_LAYOUT`: candidate body 2005 B
against historical 2028 B; entry allocation is 108 B versus 76 B. `first_day`,
`match_string`, and public `strptime` remain `FUNCTION_MATCH`. This research did
not produce a strict candidate.

## New full historical-order probe

`strptime_ctx_full_historical_order` used the locked TDM-2 `-O2` build, historical
DWARF definition order, and no added prototypes. Historical order was:

```text
is_leap_year, match_string, first_day, set_week_number_sun,
set_week_number_mon, set_week_number_mon4, _strptime, strptime
```

The emitted order remained `first_day, match_string, _strptime, strptime`. The
parser was byte-effective-equivalent to the existing control: still 2005 B,
29 direct calls, frame 0x6c, and no exact-function gains or losses. The expanded
six-probe batch deduplicates to one effective output (`cd7ad95100fd447d`). This
rules out complete historical definition order as the missing discriminator in
the current build context.

The previous five context probes are documented in
`docs/attempts/research-strptime-context-20260924/README.md`; they moved the
public wrapper, swapped the exact helper peers, combined those order edits, or
expanded the three week-helper bodies. Those also collapsed to the same output.
Use:

```powershell
python tools/effective_outcomes.py game-strptime _strptime --pattern 'strptime_ctx_*.json' --response --baseline strptime_ctx_control
```

## Narrowed blocker

Historical direct-transfer evidence has 32 calls versus 29 in the candidate.
The historical parser has three direct `_first_day` calls (at offsets 0x460,
0x4da, and 0x559), while the candidate inlines the `set_week_number_*` helpers
and ultimately `first_day`. The historical parser also has an indirect switch
jump and calls `__isctype`; the candidate currently lowers these through
different source/header forms. Historical DWARF independently confirms that
`set_week_number_sun`, `set_week_number_mon`, `set_week_number_mon4`,
`first_day`, and `_strptime` all exist in this CU, with declaration lines
158/175/191/143/209. Their complete historical declaration order was tested
above, but GCC's emitted order and effective parser output did not move.

The 35-byte public wrapper is already an exact ABI witness for the three
register-passed arguments and stack state pointer. `httpGetLastModified` calls
that public wrapper; it does not expose a missing `_strptime` caller-side ABI
change. The current candidate preserves the parser's four-argument
`regparm(3)` declaration and does not add implicit declarations.

The remaining discriminator is therefore the historical parser's exact source
form or a specific optimizer context that preserved three calls to
`first_day` while still expanding the week helpers. The published family
ancestor is not sufficient: its parser has different state and timezone
handling. No source attribute or compiler switch was introduced to force this
shape. The next useful evidence would be the actual historical source snapshot,
or an independently documented historical declaration/interface detail that
changes this inline decision. Avoid more wrapper/helper reordering or cosmetic
rewrites; they are output-deduplicated.

## Artifacts and evidence

- `strptime.c.snapshot` — exact maintained source snapshot used for this probe;
  SHA-256 `eb169b0ef065cd2329fab7f07e9a73b446bbc0a59e0c12f029ec4d64fbce6389`.
- `full-historical-order.receipt.json` — complete probe inputs, identities,
  order, and strict statuses.
- `full-historical-order.comparison.json` — raw function/CU comparison receipt.
- `docs/current/functions/strptime/_strptime.json` — current focused function
  card (not copied or edited).
- `docs/current/function-evidence/strptime/_strptime.json` — original direct
  transfer list and decoded entry/instruction evidence.
- `docs/attempts/research-strptime-context-20260924/README.md` — prior five
  TU probes, output identity, source-family and `tzname` ownership findings.

All comparisons are diagnostic; none establishes `OBJECT_MATCH` or `CU_MATCH`.
