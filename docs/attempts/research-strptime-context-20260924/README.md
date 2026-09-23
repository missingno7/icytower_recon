# `_strptime` source and import investigation

This is isolated research for `game-strptime/_strptime`; it does not change
maintained source, the recovery ledger, or generated current state.

## Full-TU probes

All successful probes used locked TDM-2 GCC at `-O2`, `--no-prototypes`, and
left the three exact peers unchanged. Their receipts are under
`docs/attempts/tu-context/game-strptime/`:

| Label | Isolated change | Receipt |
| --- | --- | --- |
| `strptime_ctx_control` | Current definition order; unchanged `_strptime` body | `strptime_ctx_control.json` |
| `strptime_ctx_wrapper_last` | Move public wrapper after parser | `strptime_ctx_wrapper_last.json` |
| `strptime_ctx_peers_swapped` | Swap `first_day` and `match_string` definitions | `strptime_ctx_peers_swapped.json` |
| `strptime_ctx_wrapper_last_peers_swapped` | Combine those two order changes | `strptime_ctx_wrapper_last_peers_swapped.json` |
| `strptime_ctx_inline_week_helpers` | Expand the three existing `set_week_number_*` helper bodies into `_strptime` | `strptime_ctx_inline_week_helpers.json` |

Each probe kept `first_day` (20 B), `match_string` (103 B), and `strptime`
(35 B) at `FUNCTION_MATCH`. `_strptime` remained `DIFFER`, 2005 B candidate
against 2028 B historical, with its first mismatch at offset 8. Effective
output deduplication grouped all five labels as one output, identity
`cd7ad95100fd447d`:

```powershell
python tools/effective_outcomes.py game-strptime _strptime --pattern 'strptime_ctx_*.json' --response --baseline strptime_ctx_control
```

The helper expansion compiled to the same output. GCC still inlined
`first_day`; it did not restore the three direct `_first_day` calls observed in
the original parser. Historical evidence records 33 transfers: 32 direct calls
and one indirect switch jump. Direct call counts include `_strtol` 15,
`_match_string` 5, `__isctype` 3, `_first_day` 3, `_strcmp` 2, and one each to
`_strptime`, `_strncpy`, `__tzset`, and `___chkstk`. The current candidate has
29 call entries and no `_first_day` call. This makes the helper-call/inlining
shape a concrete difference, but the direct-form probe shows that expanding the
week helpers alone does not explain it.

The probe artifacts in this directory include `_strptime.body.c`,
`_strptime.inline_week_helpers.body.c`, and the order JSON files. Earlier
attempts to move `_strptime` before its static week-helper definitions failed
to compile because the diagnostic overlay had no forward declarations; those
failures are retained under `build/tu-context/game-strptime/` and are not
evidence about historical output.

## Upstream and compiler evidence

`docs/strptime-recovery.md` identifies MapServer rel-5-6-6 commit
`d0da3829d7e189e3d49c231e687cbb4ee8671fa9` as the closest concrete source
lineage, but documents differences that rule it out as the exact parser. The
local `third_party/README.md` says the exact `strptime.c` and `timecompat.c`
revisions remain unresolved. There is no separate local vendor copy of
`strptime.c`; `src/strptime.c` is the reconstructed candidate. The Newlib,
Heimdal, and FreeBSD links in the recovery map are research references, not
locally pinned source snapshots.

The missing discriminator is the actual historical
`F:\projects\icytower\trunk\source\strptime.c` snapshot, including
the `first_day` declaration/attributes and week-number source form. If that
does not account for the retained calls, the exact historical compiler command
and MinGW header set are also needed. Current experiments use locked TDM-2 at
`-O2`; project evidence points to TDM-GCC 4.4.1-tdm-1/SJLJ historically.

## `tzname` import ownership evidence

The focused `_strptime` card records candidate COFF symbol `__imp__tzname` at
function offset 875 as `UNRESOLVED_RELOCATION_OWNER`. Existing evidence shows:

- Original DWARF declares external `_tzname` from the historical MinGW
  `time.h`, line 141.
- The original PE import table contains `msvcrt.dll::_tzname` (hint 474).
- Locked TDM-2 `time.h` declares the old-name `tzname`; the candidate object
  refers to `__imp__tzname`, and locked `libmoldname.a` has that import symbol.
- `tzname_import_probe.c`, compiled and linked with locked GCC, produces an
  executable whose import table lists `msvcrt.dll::_tzname`.

The last item is a small alias-resolution probe, not a change to the current
function card. The checker currently retains the unresolved owner state; this
README records supporting evidence for the supervisor's independent review.
The isolated source and executable are `tzname_import_probe.c` and
`build/tu-context/game-strptime/tzname_import_probe.exe`.
