# `draw_frame` fifth frame-zero height load trace

Scope: isolated research only. No maintained source, generated current state, or recovery ledger was changed. The current focused card is `docs/current/functions/main/draw_frame.json`; the retained complete function is `docs/attempts/game-main/draw_frame-merged.c`. Prior status/pose-independent findings were read before this trace.

## Original predecessor trace

The five accesses are all attributed to historical `main.c:2606` by `evidence/census/line-mappings.json`. The matching disassembly instruction starts and function offsets are:

| Original instruction | Function offset | Incoming path | `p_im` DWARF range |
|---|---:|---|---|
| `0x409a20` | 1924 | positive speed/reset predecessor; height is read before `%esi` is assigned 1 at `0x409a3c` | `%esi` range `0x4099dd–0x409a46` |
| `0x409ba7` | 2315 | status-zero narrow-speed shortcut, leading directly to edge handling | no listed `p_im` location covers the instruction itself; location resumes at `0x409bb5` |
| `0x409cd3` | 2615 | status/pose predecessor after the frame reset; joins at `0x409ceb`/`0x409cf8` | `%esi` range `0x409c9d–0x409d06` |
| `0x409fdb` | 3391 | negative-speed/reset predecessor; `%esi` is set to 1 at `0x409fef` | `%esi` range `0x409fc1–0x409ff4` |
| `0x40aa3f` | 6051 | frame-cap continuation at `0x40aa26`; both `frame <= 3` and reset cases reach it | `%esi` range `0x40aa26–0x40aa58`; `%esi` is set to 1 at `0x40aa4e`, after the height calculation |

At the fifth predecessor the loaded `p_im` value is live in `%esi`; it is overwritten after the `1 - custom.frame[0]->h` sequence. This corrects the earlier tentative reading that the value was not live there. The distinction supported by the assembly is statement ordering: the cap-route height read precedes its final `p_im=1` write. The other two explicit `p_im=1` writes are after their respective height reads at `0x409a3c` and `0x409fef`.

The complete original source-line markers are exactly `0x409a20`, `0x409bad`, `0x409cd9`, `0x409fdb`, and `0x40aa3f`; the middle addresses are line-table markers inside the corresponding load sequences. Original instruction windows are retained in `original-window1.txt` and `original-window2.txt`.

## Isolated ordering probe

A research copy moved the cap-route `customFrame = custom.frame[0]; oy = 1 - customFrame->h;` before `p_im = 1` and kept a separate copy on the other predecessor. This tested whether the original cap-path write/read ordering and predecessor split were lost by the retained body. It was compiled with locked TDM-GCC 4.4.1 (`-O2 -g -mfpmath=387`) in current TU order, with both retained `draw_frame` and retained `play`, using `--no-prototypes`-equivalent source context.

The probe produced `draw_frame` at 8203 bytes, `DIFFER`, first mismatch offset 8 (`0xcc` candidate versus `0xdc` original), and the same four direct `_custom + 0x80` height loads as the retained baseline. Its `draw_frame` instruction bytes compare exactly equal to the retained status-zero-sign baseline, so this is a deduplicated effective outcome, not a new compiler emission. The TU has 63 exact functions in this current-order probe. No candidate is promoted.

The source and build artifacts are `draw-frame-cap-height-before-pim.c`, `run_height_probe.py`, `height-before-pim/`, `height-before-pim.comparison.json`, and `height-before-pim-draw-frame.txt`. Object SHA-256: `ef05fdf2f27c27fff12528d35a37bf95bb1a0b38a5a850a07b53fccd3906ff5e`.

## GCC pass trace — 2026-09-23

The locked GCC 4.4.1 `-O2 -g -mfpmath=387` compile was repeated on the same saved height-before-p_im TU overlay, in isolated output directories. Diagnostic output flags were checked against a no-dump compile by comparing all 82 function instruction projections, the full relocation table, and function statuses. `-fdump-tree-all` and the focused `-fdump-rtl-csa` run produced identical instruction/relocation projections (63 `FUNCTION_MATCH`, 18 `DIFFER`, one `CODEGEN_SIMILAR` in both); they did not alter effective code. Raw COFF identities differ across output directories, so they are not used as code-equivalence evidence.

The pass snapshots localize the collapse more narrowly than the earlier source-order probe:

- The input GIMPLE has four explicit `custom.frame[0]` reads: the two status-zero sign arms, the cap-route arm before `p_im = 1`, and the common non-1 arm.
- `main.c.071t.dom1` and the later optimized GIMPLE duplicate the common read onto the `p_im == 8` path, yielding five frame-zero height-read statements. `main.c.128r.expand` carries five frame-zero pointer-load instructions into RTL expansion; `main.c.179r.dse2` still carries five.
- The first *observed dump boundary* with four is `main.c.181r.csa`: the `main.c:3238` positive status-zero arm load is absent, while the other status-zero arm and both cap/common read sites remain. The dumps bracket the loss between `179r.dse2` and `181r.csa`; they do not prove which unsnapshotted internal step caused it. This means the cap-route read added before `p_im` is not the read being discarded in this probe. No further pass flags were added.

The focused `-fdump-rtl-csa` object is 212,255 bytes, SHA-256 `5d9244ef3b874218d85380dce1fb6a848f1d1d5f336427fe7a5d2251f2dcd46f`; its `draw_frame` remains `DIFFER`, 8,203 versus 8,518 bytes, first mismatch offset 8 (`0xcc` candidate / `0xdc` original). The focused TU still has 63 strict matches. The no-dump and full-tree-dump objects are `passes-baseline/unit.o` (`6fa831c843148b493880ccf878981a71b10c738b6b7358a2cbed2ed5ff5674f0`) and `passes-tree-all/unit.o` (`ec36684bc176fa9cbe926c7d2cf7c90f1ed7130f25ddaf4f2252f331f55cf97a`).

Smallest evidence paths: `passes-csa/main.c.181r.csa`, `passes-tree-all/main.c.071t.dom1`, `passes-tree-all/main.c.126t.final_cleanup`, `passes-tree-rtl-all/main.c.128r.expand`, `passes-tree-rtl-all/main.c.179r.dse2`, and `passes-tree-rtl-all/main.c.181r.csa`. The baseline comparison, dump comparison, and focused receipt are `passes-baseline/comparison.json`, `passes-tree-all/comparison.json`, and `passes-csa/comparison.json`; `run_pass_dump_probe.py`, `run_csa_probe.py`, and `analyze_pass_dumps.py` retain the reproducible commands/analysis. The `main.c` card says `draw_frame` has the historical `line_alert` predecessor at the correct emission position and that predecessor is exact, but the historical prefix is not exact (`frontier: false`); broader TU predecessor/lifetime context therefore remains possible and unproven.

### Status-zero CFG/liveness check

The removed candidate access is the first positive status-zero arm at overlay line 3238, not the cap-route access. In `179r.dse2`, both status-zero arms have their own `frame = 0`, `custom.frame[0]` load, `oy = 1 - h`, and jump to the same edge-sprite continuation (`insn 700` at line 3238 and `insn 717` at line 3244). At `181r.csa`, the positive block no longer has those data instructions: BB85's unconditional jump (`insn 2829`) targets label 2828 immediately before BB87's surviving line-3244 `frame = 0` and height load (`insn 717`). The accepted/fallthrough edge from the positive guard now enters that shared reset/height sequence, then continues to the same edge-sprite target. The dump does not establish which internal step between the two snapshots performed this factoring.

The original status-zero CFG supplies no evidence for a distinct positive-arm read or a branch-specific live value: the sign/threshold tests route through the common test at `0x409b96`; the accepted status-zero path has one frame reset at `0x409ba0`, one `custom.frame[0]` base load at `0x409ba7`, then computes `1 - h` at `0x409bb2` before the common edge handling. The `p_im` DWARF range does not cover `0x409ba7`; it resumes at `0x409bb5`, so its value/liveness at that read is not established by the retained debug evidence. This is consistent with a common original read and does not identify a candidate source distinction that would keep duplicated positive/negative reads separate.

Preserve the identity map when discussing the gap: original `draw_frame` has five reads at `0x409a20`, `0x409ba7`, `0x409cd3`, `0x409fdb`, and `0x40aa3f`; the candidate before the observed loss has five reads because GIMPLE duplicates the common non-1 read onto `p_im == 8`, while source lines 3238, 3244, 3267 (cap route), and 3274 (common route) are explicit. After the boundary, line 3238 is the lost read; line 3244, line 3267, and line 3274 plus its optimized duplicate remain. Therefore the earlier handoff below that named the original cap-route read as the *currently lost* access was wrong; the cap route is a distinct fifth original predecessor, but it survives this probe.

## Handoff

The current pass probe's lost access is candidate positive status-zero line 3238; the cap-route read at line 3267 survives. The older ordering-probe hypothesis about the fifth original read remains separately tied to `0x40aa3f`, but does not explain this four-load outcome. Original assembly shows the status-zero branches sharing one accepted-path read at `0x409ba7`, and candidate positive/negative arms have no evidenced distinct side effect, continuation, or live value that would prevent the optimizer from sharing the height calculation. No discriminating source batch is justified. Further progress requires missing historical source/CFG or debug evidence for an arm-specific state distinction (especially `p_im` liveness around `0x409ba7`) or a pass snapshot inside the `179r.dse2`–`181r.csa` interval; do not add cosmetic duplication.
