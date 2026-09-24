# HTTPResponse type-view card audit (2026-09-24)

## Current source and card identity

The maintained `src/fld_adspot.c` is 6,985 bytes with SHA-256
`9116d56f22599dfa2e7eb197a067039f693b858948946530f2dd225cbb1f5016`.
Its declaration at the original location includes
`recovered/HTTPHeader.h` and uses the historical member types:

```c
typedef struct HTTPResponse {
    int iStatusCode;
    unsigned int iNumHeaders;
    HTTPHeader *pHeaders;
    unsigned char *pPayload;
    unsigned int iPayloadSize;
} HTTPResponse;
```

`docs/current/type-views/view_fld_adspot_HTTPResponse.json` records that same
source size and SHA-256, and its `changes[].before` matches the current inline
declaration above. The plan proposes replacing it with
`#include "recovered/HTTPResponse.h"`, which is the known peer-regressing
form. Do not apply that proposed replacement. No maintained source, generated
state, or recovery ledger was changed for this audit.

## Fresh strict whole-CU baseline

Reproduced with locked TDM-2 using:

```powershell
python tools/build.py game-fld-adspot --compiler tdm-2
python tools/experiment.py game-fld-adspot --compiler tdm-2
```

Strict receipt: `build/experiments/tdm-2/game-fld-adspot/O2/comparison.json`.
It reports 11/12 `FUNCTION_MATCH` (11/12 masked), with
`fldads_get_random_ad` still an exact `FUNCTION_MATCH`. The only different
function is `fldads_threadmain`, first mismatch at function offset +46:
candidate byte `0xaf`, historical byte `0xc9`. Whole text contribution,
object, and CU equality remain false. This is a diagnostic strict baseline,
not a match claim for the translation unit.

## Prior causal study and branch decision

The bounded type-form study is
`docs/attempts/research-20260924-httpresponse-type/README.md`. Its recorded
corners include canonical generated-header substitution, three include
placements, inline historical member retyping, inline retyping plus generated
asserts, debug-off builds, and both scheduler flags disabled. It identifies
the inline historical member form as emission-preserving and the generated
header substitution as reordering bytes in `fldads_get_random_ad`. Relevant
receipts are `baseline-comparison.json`, `canonical-comparison.json`,
`variants/inline-members/candidate-delta.json`, and
`schedule-probes/*/delta.json` under that directory.

Conclusion: this type-view branch already has a source-supported candidate in
the maintained source and no additional causal variant is warranted. Reconcile
the stale generated card/planner before any production interface transaction.
Diagnostic type context earns no recovery credit.
