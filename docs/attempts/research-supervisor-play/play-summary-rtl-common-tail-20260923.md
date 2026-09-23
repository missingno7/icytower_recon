# `play` summary hint calls: RTL common-tail result (2026-09-23)

## Status

`play` remains strict `DIFFER`; this is compiler-mechanism evidence, not a recovered function. The isolated two-arm high-score split is 17,429 bytes and still emits six `new_rand` calls in the final `play` object. The current retained production body is 17,400 bytes and also emits six. No production source or recovery state was changed.

## Decisive evidence

The split source contains two `new_rand() % 45` hint expressions at candidate lines 5525 and 5533 (original lines 4770 and 4775). GCC 4.4.1 `-O2` retains seven calls in `play` through final optimized GIMPLE (`main.c.123t.optimized`) and RTL through `main.c.179r.dse2`. During `main.c.181r.csa`, the call at candidate line 5525 (`call_insn 3699`, the `gotHigh` arm) disappears. The call at line 5533 (`call_insn 3725`) remains, and its destination label 3723 changes from one use in `179r.dse2` to two uses in `181r.csa`. Thus the duplicate non-guest hint suffixes are commoned in RTL after tree optimization; source duplication alone cannot preserve the extra call.

The relevant branches both perform the same sequence on the non-guest path: `new_rand`, `hints[index]`, then `strcpy(summary_scroller_message, ...)`. The high-score arm first writes the “New personal records!” prefix, but that write is overwritten by the shared hint copy on this path. The guest paths remain separate. This is consistent with RTL tail merging, specifically observed at dump stage `181r.csa`; the evidence does not identify a more precise internal subpass name.

Original source-line disassembly further distinguishes the two surviving call
sites. At function offset 16845 (line 4775), `new_rand` is followed by a
divide using `%esi` and falls through to the shared `strcpy` argument setup
at 16867. At offset 16921 (line 4770), the other `new_rand` is followed by a
divide using `%ecx` and jumps to that same setup at 16867. The retained split
candidate has only one final call, using `%ecx`. Thus the original already
shares the copy tail while keeping separate random/divide prefixes with
different register choices. This does not identify the source cause; the next
discriminating question is what live value or TU context makes `%esi` available
on only one historical path. The original windows are reproducible with
`python tools/function_lines.py game-main play --source-view 4740 4790`.

## Probe and artifacts

- Production-equivalent TU probe: `docs/attempts/tu-context/game-main/luna-play-pass-summary-split-repro-20260923.json` (current order, `--no-prototypes`; `play` remains `DIFFER`, 17,429 bytes).
- Isolated source: `build/tu-context/game-main/luna-play-pass-summary-split-repro-20260923/overlay/src/main.c`.
- Tree dumps: `docs/attempts/research-supervisor-play/build/passdump-split/`.
- RTL dumps and object: `docs/attempts/research-supervisor-play/build/rtldump-split/`.
- Final disassembly: `docs/attempts/research-supervisor-play/build/passdump-split/objdump.txt`.

The pass-dump compiles add dump flags only and use the locked TDM GCC 4.4.1 command at `-O2 -g -mfpmath=387`; these reports are diagnostic and are not oracle proof. The source probe preserves the current production declaration context (`--order current --no-prototypes`).

## Remaining blocker

To retain two machine call sites, the historical CFG/source must give the two hint paths a genuine distinction that survives RTL common-tail analysis, or the original caller/TU compiler context must reveal why the historical compile does not merge them. The synthetic source split establishes the optimizer mechanism but does not establish that distinction. Further spelling-only duplication of the same hint suffix is low-information. Next useful evidence is an original-vs-candidate CFG/dataflow comparison around original offsets 16813–16943 and the source/local lifetime or intervening operation that keeps those blocks distinct historically.
