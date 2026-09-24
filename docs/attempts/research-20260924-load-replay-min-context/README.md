# Replay selector context beam for `load_replay`

Date: 2026-09-24. Research-only canonical `tu_context_probe.py` full-TU overlays
using locked TDM-2 / GCC 4.4.1 `-O2`. No maintained source, recovery ledger,
generated current state, or sibling repository was edited.

## Storage evidence and separate branches

The authoritative historical storage row is uppercase global `REPLAY_HEADER`,
`const char[6]`, size 6, `.rdata`, initial bytes `495452313430` (`ITR140`). The
maintained lower-case `replay_header`, `char[7]`, `.data` is an unpaired
candidate; it does not match that original declaration or object placement.

Keep the two load branches separate:

- **Maintained-base 7/15 branch:** retains the maintained global declaration and
  literal header comparison. Its only target edit is the DWARF-backed local
  `PACKFILE *pf`; a retained draw context is required for the strict target
  result. Probe `load-replay-typed-literal-draw-owner-current-20260924` is 7/15
  exact, with no losses. Its six maintained exact functions are preserved.
- **Owner-aligned 9/15 branch:** uses the retained owner TU's lower-case
  `static const char replay_header[6]` content plus its selector/property
  context. Canonical probe `load-replay-const-owner-exact-neighbors-current-20260924`
  is 9/15 exact. This is a distinct research control; it neither corrects the
  uppercase storage symbol nor authorizes changing the maintained exact
  `get_replay_property` body. The 9/15 result is not a safe promotion path.

Both branches have strict `load_replay` function results only. The whole replay
CU remains `DIFFER`, not `OBJECT_MATCH` or `CU_MATCH`.

## Draw source and DWARF facts

The owner draw body extracted at
`draw-replay-selector-owner-context.c` differs from maintained
`draw_replay_selector` by two executable statements (comments aside):

```c
if (i == selection) {
    show_directory = post->directory;
    selected_version = post->version;
}
```

Original DWARF locates `show_directory` at EBP-1108 (`-0x454`) and
`selected_version` at EBP-1104 (`-0x450`). Original instructions initialize
those slots at `0x41c267` and `0x41c271`; the selected-row path reads
`post->version` at `0x41c4cb`, stores it at `0x41c4ce`, and stores the row's
`post->directory` value at `0x41c4d4`. The retained maintained-source variant
with these two assignments emits the same draw function output as the owner
body and is the minimal demonstrated context that makes load strict.

Other declaration and lifetime facts:

- DWARF says `view_percentage` and `view_offset` are `double`; maintained source
  declares both `float`.
- DWARF places `name char[1024]` and `rbuf char[129]` in separate lexical blocks,
  both at fbreg -1056. Maintained source uses one function-scope `rbuf` for list
  rows and later warning text.
- DWARF gives `curr_filename` type `char *` and location EBP-1096. Original
  instructions store the `get_filename` result to EBP-1096 before copying it.

## Retained draw probes

Every row below preserves the six maintained exact functions. Target load status
is included to show which draw forms preserve the 7/15 strict branch.

| Probe / source change | Draw candidate | Frame | Calls / relocation entries | Load / exact set |
|---|---:|---:|---:|---|
| Typed-literal control, maintained draw | 2751/3726 | `0x11c` | 38 / 82 | DIFFER / 6 exact |
| Add selected-row assignments | 3007/3726 | `0x11c` | 39 / 87 | FUNCTION_MATCH / 7 exact |
| Double declarations only | 2755/3726 | `0x11c` | 38 / 82 | DIFFER / 6 exact |
| Doubles plus selected-row assignments | 3011/3726 | `0x11c` | 39 / 87 | FUNCTION_MATCH / 7 exact |
| Split `name[1024]` and warning `rbuf[129]` scopes plus selected assignments | 3007/3726 | `0x48c` | 39 / 87 | FUNCTION_MATCH / 7 exact |
| Split buffers, doubles, and selected assignments | 3011/3726 | `0x48c` | 39 / 87 | FUNCTION_MATCH / 7 exact |

Original draw frame allocation is `0x49c` (1180 bytes). The split-buffer
candidate reserves `0x48c` (1164 bytes), closing 880 bytes of the 896-byte
gap in the maintained frame. It remains `DIFFER`, with first mismatch at
prologue offset +8. Its draw effective output is a distinct class
`4cf2d8b39b8d3d7e`, with 2830 byte differences and 86/87 equal relocation
entries; the selected-assignment-only body is `4d39629633c75ab0` with 2814
byte differences and 86/87 equal relocation entries. So the frame moved closer,
while total byte differences increased by 16.

Changing only one float to the DWARF double type also preserves strict load and
all six neighbors, but draw remains `DIFFER`: `view_offset` alone yields 2849
byte differences; `view_percentage` alone yields 2870. Both doubles yield 2850.
These are distinct effective classes and are not acceptance proofs. Moving
`is_dir` into the row block and assigning the retained `curr_filename` local
produced no new effective draw output when combined with split buffers/doubles.

The split-buffer single-double probes remain distinct effective outcomes:
`view_offset` alone has 2849 draw byte differences; `view_percentage` alone has
2870; both together have 2850. Each is 3011/3726 bytes, uses frame `0x48c`, and
preserves the strict load match and all six maintained exact neighbors. The
`curr_filename` assignment and row-scoped `is_dir` probes deduplicate into
existing classes. No remaining local-lifetime variation tested so far changes
the load result or closes the draw code/relocation gap.

The 7/15 load match therefore survives several DWARF-backed draw steps, with
all maintained exact functions preserved. Draw itself is still 3007/3726 or
3011/3726, and the best observed stack frame is still 16 bytes short of the
original. At this research stage, no strict draw match or promotion path had
been established. The
remaining instruction and relocation differences require further source
recovery; adding unsupported padding or guessing extra locals would not be
historically supported.

The subsequent `replay_load_draw_historical_20260924` TU transaction used the
historically ordered selected-row calls and DWARF buffer scopes, passed the
strict acceptance gate, and promoted `load_replay` as the seventh exact replay
function. Its retained source, receipt, and unresolved draw-frame result are
documented in `../research-20260924-draw-selector-residual/README.md`.

## Artifacts

- Maintained-base target body: `load-replay-typed-literal.c`
- Minimal draw body: `draw-replay-selector-selected-locals.c`
- DWARF lifetime variant: `draw-selector-dwarf-buffers-selected.c`
- Separate double/lifetime variants: `draw-selector-dwarf-buffers-selected-double.c`,
  `draw-selector-dwarf-buffers-selected-view-offset-double.c`,
  `draw-selector-dwarf-buffers-selected-view-percentage-double.c`
- Additional `curr_filename` and `is_dir` scope probes are retained beside those
  variants; their receipts are `load-replay-min-draw-dwarf-buffer-currfilename-20260924.json`,
  `load-replay-min-draw-dwarf-buffer-double-currfilename-20260924.json`, and
  `load-replay-min-draw-dwarf-buffer-double-loop-isdir-20260924.json`.
- Maintained-base strict receipt: `../tu-context/game-replay/load-replay-typed-literal-draw-owner-current-20260924.json`
- Buffer-lifetime receipt: `../tu-context/game-replay/load-replay-min-draw-dwarf-buffers-selected-20260924.json`
- Reports: `../../../build/tu-context/game-replay/`
- Effective grouping: `python tools/effective_outcomes.py game-replay draw_replay_selector --pattern '*20260924.json' --compact --response`
