# `view_scores` source and frame evidence (2026-09-24)

## Findings

The current `view_scores` card reports `DIFFER`, 2,498 bytes versus 2,552
historically, with the first mismatch at function offset 8: stack reservation
is `0x4c` in the candidate and `0x5c` in the original. DWARF pairs all 16
named locals with the same types; the declaration order in `src/hisc.c`
matches the historical root-scope order. The card's exact emission predecessor
is `draw_table` in both builds, and that predecessor is exact, so this is not
a same-CU predecessor mismatch.

Two concrete source differences are directly supported by the original
line/call and instruction evidence:

- Original `hisc.c:286` contains a direct `keypressed` call immediately after
  `blit_to_screen`; its return is discarded before `cycle_count` is loaded at
  offset 2191. The current body had omitted this call.
- Original offsets 791–836 read `key[KEY_ESC]`, `key[KEY_ENTER]`, and
  `key[KEY_SPACE]` twice for the exit/arming tests. The current source used
  `KEY_F1`, `KEY_ENTER`, and `KEY_K` in those two tests. Its earlier
  `KEY_K` input-drain check is retained because the original line 183 also
  reads that key.

The original source-line evidence is reproducible with
`python tools/function_lines.py game-hisc view_scores --source-view 240 300`
and `--calls-by-line`. After both supported corrections, the probe's
`historical_callees` and source-call surface have no missing direct edge; the
three extra source names (`clear_to_color`, `draw_sprite`, `rectfill`) are
inlined and are absent from historical direct calls. The remaining function
is still `DIFFER` at 2,502 bytes, 50 bytes short, with the original 16-byte
stack-reservation mismatch. These source fixes do not establish exactness.

## Isolated full-TU probes

All probes use locked GCC through `tu_context_probe.py`, current definition
order, and `--no-prototypes`. Each retained all ten exact functions in the
11-function CU, with no gains or losses and no unchanged-body effective code
changes.

| Probe | Evidence-backed change | `view_scores` | Effective identity |
| --- | --- | ---: | --- |
| `luna-view-scores-keypressed-call-20260924` | Add original line-286 call | DIFFER, 2,502 B | `e855c7d10fcac56f` |
| `luna-view-scores-key-constants-20260924` | Correct only the two exit tests | DIFFER, 2,498 B | `2edfc1fc9f4c1548` |
| `luna-view-scores-key-call-and-constants-20260924` | Both changes | DIFFER, 2,502 B | `564aec13f68e2bca` |

Body sources:

- `view-scores-keypressed-call.c`
- `view-scores-key-constants.c`
- `view-scores-key-call-and-constants.c`

Receipts are under `docs/attempts/tu-context/game-hisc/` with the matching
probe labels. The combined diagnostic object, `comparison.json`, DWARF, and
RTL dumps are under `build/tu-context/game-hisc/luna-view-scores-key-call-and-constants-20260924/`.

## Remaining evidence boundary

The supported omissions repair the original direct-call set and key-byte
addresses, but leave the same prologue mismatch. Loclists show that several
locals move between registers and stack homes over disjoint ranges; the
original has DWARF-unlocated `targetDark` and `bmpHeight`, so named-local
widths alone do not account for the 16-byte reservation. No speculative
declaration reshuffle was tested. The next useful step is an original versus
combined-candidate live-range/RTL comparison around the drawing and animation
loops, or new source evidence for the remaining control-flow/codegen
difference. No maintained source, current card, or recovery ledger was edited.
