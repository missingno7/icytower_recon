# HTTPResponse aggregate blocker research (2026-09-24)

## Historical layout

DWARF contains two historical `HTTPResponse` definitions (CUs 39790 and 71812,
from `httpget.h`), both size 20:

| Member | Offset | Historical type |
| --- | ---: | --- |
| `iStatusCode` | 0 | `int` |
| `iNumHeaders` | 4 | `unsigned int` |
| `pHeaders` | 8 | `HTTPHeader *` |
| `pPayload` | 12 | `unsigned char *` |
| `iPayloadSize` | 16 | `unsigned int` |

`HTTPHeader` is size 8: `char *pHeader` at 0 and `char *pValue` at 4.
`include/recovered/HTTPResponse.h` and `HTTPHeader.h` already match those
layouts. The conflicting declaration is the private `HTTPResponse` definition
in `src/fld_adspot.c`, which currently has signed `int` sizes and a `void *`
header pointer.

## Isolated source trials

- `fld_adspot-baseline.c` is an unchanged copy of the maintained source.
- `fld_adspot-canonical.c` changes only the duplicate declaration to
  `#include "recovered/HTTPResponse.h"`.
- Both were compiled with locked TDM-2, `-O2 -fno-toplevel-reorder`, and compared
to the original executable. The baseline copy has zero candidate delta against
  `docs/current/reports/game-fld-adspot.json`.
- The canonical candidate fixes the member-type mismatch. It preserves every
  function byte stream except `fldads_get_random_ad`, which was previously an
  exact `FUNCTION_MATCH`. That function remains 192 bytes but changes four
  bytes at offset +0x29: `xor %eax,%eax; fldz` becomes `fldz; xor %eax,%eax`.
  The change is an instruction permutation and still fails exact matching.
  `fldads_update_local_adimg` stays exact; `fldads_threadmain` remains at its
  pre-existing `DIFFER` status.

## Decision

Keep the HTTPGet, HTTPHead, and destroyHTTPResponse aggregate conflicts blocked.
The canonical header is sound, but applying it in `fld_adspot.c` currently
costs an exact peer. No gate change or type cast is justified by this evidence.
A later source/context repair must restore the `fldads_get_random_ad` bytes
before the interface task can be promoted.

Evidence: `baseline-comparison.json`, `canonical-comparison.json`,
`baseline-path-delta.json`, and `baseline-delta.json`. Compilation records are
under `baseline/` and `canonical/`.

## Follow-up source-form batch

The reliable emission-preserving spelling is an inline full definition at the
original declaration point, with the existing historical dependency order:

```c
#include "recovered/HTTPHeader.h"

typedef struct HTTPResponse {
    int iStatusCode;
    unsigned int iNumHeaders;
    HTTPHeader *pHeaders;
    unsigned char *pPayload;
    unsigned int iPayloadSize;
} HTTPResponse;
```

The four include variants and corrected inline variant are under `variants/`.
The three `HTTPResponse.h` include placements (after `FLDAdSpot.h`, before it,
and after the system headers) all produced the same one-function permutation;
the corrected inline form had zero function or non-debug contribution delta.
Adding the generated header's static-assert typedef declarations to the inline
form reproduced the permutation too. Turning debug generation off did not
remove the include-form difference. Disabling both instruction schedulers did
not remove it either. This points to front-end/TU declaration context before
machine scheduling rather than debug-only metadata; the TDM-2 dump flags used
here did not provide a useful first-pass dump (only an empty `159r.combine`
summary was emitted), so the exact earliest pass remains unknown. Related
artifacts: `variants/*/candidate-delta.json`, `schedule-probes/*/delta.json`,
and `no-debug/*/`.

## Production-safe acceptance route/spec

No current command/card can apply this exact inline member-type correction.
The existing `view_fld_adspot_HTTPResponse` type-view planner's canonical-header
change is the known regressing form, and the interface tasks are blocked before
prototype repair while the candidate aggregate remains wrong. Do not promote
that canonical-header replacement.

A safe task should update the existing type-view edit plan to retype the three
members in place at the original declaration site, inserting only the
`HTTPHeader.h` include immediately before the struct. It must retain the tested
source shape above and not add generated static-assert typedefs to this CU.
Then run the existing fresh owning-CU strict path for `game-fld-adspot` and
require: (1) all 12 candidate function byte streams/statuses unchanged from the
current accepted report, including exact `fldads_get_random_ad`; (2) complete
`.text`, initialized data, common/BSS, symbol, and relocation preservation;
(3) the candidate `HTTPResponse` layout fully equals the historical graph; and
(4) refreshed HTTPGet/HTTPHead/destroyHTTPResponse interface cards no longer
report aggregate conflicts. Only after that should each interface's remaining
prototype differences be handled by its own interface task. The current type
view tool does not emit this edit plan, so this is a required planner/tool
extension before production application; no source/current/recovery files were
changed in this investigation.

After the `type_views.py` planner supports this source-local member-retyping
plan and regenerates its receipt-derived card, the existing transaction commands
are:

```powershell
python tools/interface_task.py begin view_fld_adspot_HTTPResponse
python tools/interface_task.py apply view_fld_adspot_HTTPResponse
python tools/interface_task.py check view_fld_adspot_HTTPResponse
python tools/interface_task.py promote view_fld_adspot_HTTPResponse
```

The `check`/`promote` calls must build and compare the full owning CU through the
existing strict interface path. The edited plan must be emitted by the planner;
these commands are not safe with today's card because it still plans the
regressing generated-header replacement. After promotion refreshes conflicts,
run the same begin/apply/check/promote transaction separately for any newly
unblocked `HTTPGet`, `HTTPHead`, and `destroyHTTPResponse` tasks. Their remaining
prototype edits must come from the historical interface receipts, not from this
aggregate experiment.
