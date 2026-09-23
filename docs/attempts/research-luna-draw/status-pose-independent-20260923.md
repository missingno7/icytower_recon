# Isolated draw_frame status/pose CFG research

## Scope and baseline

This was a read-only audit of maintained sources and generated state followed by two historical-order overlay probes. The retained source was `docs/attempts/game-main/draw_frame-merged.c`; its whole-TU baseline includes the retained `play-merged.c`. No file under `src/`, the recovery ledger, or generated current state was changed. The parent task supplied the fresh project baseline: 204 strict exact functions after `--verify-all` and a clean audit.

Current focused card: `docs/current/functions/main/draw_frame.json` (`DIFFER`, production candidate 985/8518; current card is about production source, not the retained 8 KB research body). Relevant current task queues still route `draw_frame` as `SOURCE_INCOMPLETE` with unresolved relocation ownership.

## Question and evidence

The retained draw candidate already incorporated the traced status-zero sign route, strict `(-0.01, 0.01)` pose band, exclusive edge paths, and default `custom.frame[0]` selection. Earlier probes had tested the status-zero join, positive/negative speed spelling, and cap-skip continuations. The original EXE has five direct frame-zero height reads (`custom.frame[0]->h`) at `0x409a20`, `0x409ba7`, `0x409cd3`, `0x409fdb`, and `0x40aa3f`; the indexed pose-frame lookup is separate. The retained candidate emits four direct frame-zero height reads.

One new CFG hypothesis was that the candidate's `else if` chain merged status 3 and status 2 earlier than the historical CFG. Original code has separate status 3 and status 2 compare blocks (`0x4099b7`/`0x4099ba` and `0x409c77` onward). A research-only copy changed these into three independent `if` statements, preserving each observed `sy` condition and `p_im` result. A second candidate combined that structure with explicit positive and negative `0.2` speed arms.

## Outcomes

| Probe | `draw_frame` | Frame-zero height reads | Whole-TU result | Compiled object SHA-256 |
| --- | ---: | ---: | --- | --- |
| Retained status-zero-sign candidate | 8203/8518 | 4 | 62 exact; no losses; `new_game` and `run_demo` exact | `df87219118e5ad5823a59a776b3d813965c44d7309ce2cc6fd1748bb3946c899` |
| Independent status tests | 8137/8518 | 4 | 60 exact; loses `show_instructions`, `stopGameMusic`; `new_game` and `run_demo` remain exact | `16602cac216899030d66f0b704b208cd817614a2b3477c2f574fa0c114091bab` |
| Independent status plus signed speed arms | 8151/8518 | 4 | Same 60 exact and same two losses; `new_game` and `run_demo` remain exact | `be1423c7c8a934d75d71150d37a18022e3cddbebf255944a0830a14c60eec817` |

Although the source keeps status 3 and 2 as independent tests, GCC 4.4.1 directs both generated comparisons to one shared target in the overlay object. The independent tests therefore do not recover a fifth load. Adding the signed speed split changes the object again but leaves the same four-load effective family. Earlier retained signed-speed and frame-cap-skip probes also each emit four reads; their records are `takeover-draw-signed-speed-trial-20260923.json` and `takeover-draw-frame-cap-skip-trial-20260923.json`.

`python tools/effective_outcomes.py game-main draw_frame --pattern "*draw*json"` grouped 23 retained draw-related TU probes into 21 effective code/relocation outcomes. Both new candidates are distinct outcomes (`103448c59d6254b4` and `866c48da170830a6`), not duplicate spellings of a seen emission. Existing exact effective repeats include the status-zero pose retained/trial pair and the status-zero sign retained/trial pair. This confirms the new probes gained compiler-output information even though neither gained a strict match or fifth load.

These are diagnostic `DIFFER` results only. The independent-status trial's losses are whole-TU context side effects, not evidence that either unrelated body needs repair. Neither candidate is suitable for promotion.

## Remaining blocker

The local status and speed spelling hypotheses have converged: independent status tests, separate signed speed arms, and the prior status-zero/cap variants do not produce the fifth frame-zero height read. A remaining candidate mechanism is loss of an original predecessor distinction: the independent-if probe's generated graph rejoins the status 3 and status 2 comparisons. The exact original-to-candidate path correspondence for the missing fifth read remains unresolved. The next useful step is a predecessor/liveness trace for all five original loads and four candidate loads, especially the reaching `p_im` values at status 1 and status 0 exits. That must establish a source CFG distinction before another body experiment. Do not add duplicate statements solely to raise the load count.

## Artifacts

- `draw_frame-status-independent.c` — first isolated candidate.
- `draw_frame-status-speed-product.c` — independent-status plus signed-speed candidate.
- `docs/attempts/tu-context/game-main/luna-draw-status-independent-20260923.json` — object identity, function sizes/statuses, and whole-TU outcomes.
- `docs/attempts/tu-context/game-main/luna-draw-status-speed-product-20260923.json` — second probe receipt.
- `build/tu-context/game-main/luna-draw-status-independent-20260923/unit.o` and `build/tu-context/game-main/luna-draw-status-speed-product-20260923/unit.o` — compiler outputs used for the four-load checks.
