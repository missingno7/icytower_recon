# `view_scores` CFG and frame audit (2026-09-24)

Diagnostic comparison of the combined isolated candidate in
`build/tu-context/game-hisc/luna-view-scores-key-call-and-constants-20260924/`
against the original executable. No maintained source, current card, or ledger
was changed.

## Results

- The original instruction stream decodes to 642 instructions and 93 basic
  block leaders. The combined candidate decodes to 625 instructions and 93
  leaders. This checks block-count shape only; it does not establish identical
  edges or function equality. The candidate GCC `181r.csa` dump reports 94
  RTL blocks including compiler entry/exit bookkeeping, with 135 CFG edges.
- Both binaries use the same maximum outgoing argument area: writes reach
  `esp+0x1c`, or eight 32-bit words (32 bytes). The 16-byte prologue gap is
  therefore not explained by a wider outgoing-call argument area in the
  candidate.
- Original and candidate reserve 92 and 76 bytes respectively. The deepest
  explicit EBP-relative accesses are `-0x3c` in the original and `-0x38` in
  the candidate. Their named-local types and declaration order agree, while
  `targetDark` and `bmpHeight` have no original DWARF locations. Named-local
  widths alone do not account for frame reservation.
- Original loclists show values moving among registers and reused frame slots:
  `i` has five disjoint ranges, `bg` six, `pageY` four, `targetY` three,
  `dark` two, `bmp` six, `yPos` six, and `done` four. This is consistent with
  substantial lifetime reuse across list building, entry animation, and exit
  animation. The candidate 181r live-out sets around these paths include
  persistent `bx`/`si`/`di` values across drawing blocks and several
  `ax`/`dx`/`cx` temporaries around call and animation blocks. The dump is for
  the candidate only; the original executable cannot provide GCC RTL.
- Source evidence for the missing `keypressed()` call and the ESC/ENTER/SPACE
  key addresses was already applied in the isolated combined probe. Its
  direct-call set has no missing historical edge. The combined probe remains
  2,502 bytes against 2,552 bytes, with the prologue allocation still the
  first mismatch.

## Probe decision

No further source-backed variant is justified by the current evidence. The
combined candidate already contains the only identified missing direct call
and the supported key-address corrections; the source order around the two
animation loops matches the recovered line/call evidence. Declaration-order
and control-flow rewrites would be speculative, and introducing dummy reads,
volatile objects, or compiler attributes would not be historical source
evidence. Do not promote this candidate or infer a layout-only match.

## Receipts

- Historical disassembly: `build/view_scores-disassembly.txt`
- Candidate disassembly: `build/tu-context/game-hisc/luna-view-scores-key-call-and-constants-20260924/view_scores-disassembly.txt`
- Candidate locked-GCC RTL and peephole dumps: `hisc.c.181r.csa`,
  `hisc.c.182r.peephole2` in the same build directory
- Candidate DWARF text and object: `dwarf.txt`, `unit.o` in that directory
- Combined isolated-probe receipt: `docs/attempts/tu-context/game-hisc/luna-view-scores-key-call-and-constants-20260924.json`
- Original loclists and named-local pairings: `docs/current/function-evidence/hisc/view_scores.json`
- Fast verifier output was refreshed in `build/fast/game-hisc/view_scores.json`;
  it still reports `DIFFER` (candidate 2,498 bytes; stack reservation 76 vs 92).
