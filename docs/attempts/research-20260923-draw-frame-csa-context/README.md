# `draw_frame` status-zero and frame-zero load follow-up

Research-only TDM-2 / GCC 4.4.1 `-O2` historical-order TU probes, based on retained `draw_frame-merged.c` and `play-merged.c`. No maintained source, generated current state, recovery ledger, or sibling repo was edited.

## Evidence and read-count interpretation

Original `draw_frame` has five direct reads of `custom.frame[0]` for height (offsets 1924, 2315, 2615, 3391, 6051), plus a separate indexed pose-frame lookup. Candidate COFF references must keep that indexed base separate when comparing counts.

The current source has four explicit frame-zero read statements: two sign arms in status zero, one shared frame-zero/height statement after `p_im` setup, and the cap/common path represented through that shared code. In the retained source overlay, DOM1 duplicates the common height read onto the `p_im==8` path, yielding five RTL pointer loads at `128r.expand` and `179r.dse2`. `181r.csa` is the first saved pass with four: it folds the positive status-zero arm (candidate line 3238) into the common surviving negative arm (line 3244). This is a candidate optimization artifact; it does not identify the missing original speed/reset predecessor.

The original status-zero CFG at 0x409b6c–0x409bb5 performs sign-specific `±0.02` tests, then has one accepted-path reset/read at 0x409ba0/0x409ba7 and computes `oy=1-h` at 0x409bb2. That path proceeds directly into edge handling and bypasses the later `p_im` test. DWARF does not assign a `p_im` location at 0x409ba7; its listed range resumes at 0x409bb5. Thus the positive source arm's read being folded is consistent with the original shared status-zero accepted path. The whole status-zero route is still represented; the single positive-arm RTL load is not a required distinct historical access.

## Source-backed speed-path probes

The original separate positive and negative speed/reset predecessors at 0x409a19–0x409a41 and 0x409fd4–0x409fef each read `custom.frame[0]`, calculate `1-h`, and only then assign `p_im=1`. This differs from the retained C body, which has one combined speed-reset predicate and later common height computation.

1. `draw-frame-speed-path-height-source.c` adds those `oy` computations in explicit `sx>=0` and `sx<0` reset branches while keeping the later common calculation. It compiles to 8204 bytes; candidate still has four direct loads plus the indexed lookup. The later common write makes the branch-local values dead, so this spelling does not restore a read. `new_game`, `run_demo`, and the prior exact set remain unchanged (63/82 exact, no gains or losses).
2. `draw-frame-live-speed-height-source.c` routes the two reset branches around the later common calculation, reflecting the original statement order. This is a distinct effective outcome at 8040 bytes, but it emits only three direct frame-zero references plus the indexed lookup and reduces direct-call count to 104 from 107. It is not a match. `new_game`, `run_demo`, and the prior exact set remain unchanged (63/82 exact, no gains or losses).

The two probe records are `docs/attempts/tu-context/game-main/csa-context-speed-path-height-20260923.json` and `.../csa-context-live-speed-height-20260923.json`; focused objects are under corresponding `build/tu-context/game-main/` directories. Effective-output check: the two probes are distinct from each other (`effective_outcomes.py` hashes `578c4bc394ecbb55` and `2f9ded0dbaf82c9b`).

## Boundary

The original supports separate speed/reset height computations and an independent status-zero accepted path. The current candidate's shared/default `oy` computation erases that source distinction; retaining those computations with a direct branch rewrite either makes them dead (because of the later common write) or changes more topology and loses other observed calls. Existing CFG/DWARF does not yet support a semantically faithful shared-join/source scope that both retains the separate speed-path computations and preserves the rest of the function. The missing physical read is therefore not explained by the status-zero arm eliminated at `181r.csa`; it requires the remaining speed/reset predecessor/source structure. Stop local branch spelling until new line-table, predecessor, or compiler-tree evidence constrains that join.
