# Selector-only TU_CONTEXT candidate

The full-source candidate differs from src/replay.c only by four C/F/N/S case arms in replay_selector. No header, REPLAY_HEADER, get_replay_property, or other function body changed. The complete replay_selector definition was extracted verbatim from low-sort-cases-source.c to retained-replay-selector.c. Its only body delta from the maintained definition is those four arms.

Retained body: 10,033 CP1252 bytes, SHA256 763d58f879986a7c4110be8cb7f977bea3368de5fd495136eac40a1164fc8bc2.

Ready spec: selector-only-tu-context-spec.json. It specifies current definition order and prototypes none, so it uses the existing maintained declaration context.

Fresh isolated body probe:

    python tools/tu_context_probe.py game-replay src/replay.c replay-selector-lowkeys-body-20260924 --body replay_selector=docs/attempts/research-20260924-selector-lowkeys-next/retained-replay-selector.c --focus replay_selector --no-prototypes --no-dumps

Receipt: docs/attempts/tu-context/game-replay/replay-selector-lowkeys-body-20260924.json

Strict report: build/tu-context/game-replay/replay-selector-lowkeys-body-20260924/comparison.json

Result: compile OK; all seven pre-existing FUNCTION_MATCH peers preserved with no gains or losses. replay_selector remains DIFFER, 2493/2845 bytes.

The original lower-range CFG and the four key/action mappings are documented in docs/attempts/research-20260923-create-replay/rdata-order/lower-range-cfg.json and the README in this folder.

Transaction planner command for the root owner:

    python tools/tu_context_task.py plan replay_selector_lowkeys_four_cases_20260924 docs/attempts/research-20260924-selector-lowkeys-next/selector-only-tu-context-spec.json

Planning and promotion were not run in this investigation.
