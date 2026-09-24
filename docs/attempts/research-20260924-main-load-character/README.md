# `load_character` under the current accepted main.c context — 2026-09-24

Research-only. No maintained source, current generated state, recovery ledger, or protected body was edited. Both probes used the locked current TU order, TDM GCC 4.4.1, `--no-prototypes`; the second replaced five collision-family bodies plus `get_string` and `do_replay_menu` with the retained context bodies from the three ACCEPTABLE context recipes.

## Strict result

- `load_character` remains **DIFFER** in both probes: 330 bytes, 92 instructions, first mismatch +13, differing instruction-byte offsets `13,16,24,41,53,59,67,138,178,185,202,206,248,254,258`.
- Both candidate instruction streams have SHA-256 `a5b736f2365c606d70bb0d09e57a794bf9b0c677d52f6a43c7ed7d409a95bd11`: the accepted-context overlay has no effective output change for this target.
- All 18 target relocations resolve equal in both comparisons. Exact extent, matching size, matching relocations, or a shared text projection do not change the strict verdict.
- Each whole-TU result reports 63/82 exact functions, 79/82 historical predecessor identities, no gains/losses, no changed unchanged-body code, and no new implicit declarations. Whole text, OBJECT_MATCH, and CU_MATCH are false. The 63 function matches are the preserved peers; this is not a whole-CU or data/layout match.

## Context decision

The accepted candidates tested were `handle_player_collision_original`, `handle_player_collision_old`, `handle_player_collision_combo`, `handle_player_collision_vector_2`, `handle_player_collision_vector`, `get_string`, and `do_replay_menu`. They are later in current source order than `load_character`, yet regardless of backend ordering they do not change its effective machine output in this compile. This closes the current promoted-neighbor context lead without granting any function proof or validating those differing candidates as functions.

The remaining evidence-backed lead is the immediately preceding nonmatching `init_game`: prior probes identify its GCC 4.4.1 peephole2 scratch cursor as a possible register-choice source, but retained `init_game` variants produced the same target stream and extracted scratch sequence. No historically supported alternate `init_game` body or independent compiler-state trace is available. Stop local spelling variants until such discriminating evidence exists; keep `load_character` DIFFER.

## Probe receipts

- `build/tu-context/game-main/research-20260924-main-load-character-current/comparison.json`
- `build/tu-context/game-main/research-20260924-main-load-character-accepted-context/comparison.json`
- `docs/current/functions/main/load_character.json` and `docs/current/function-evidence/main/load_character.json`
- Historical source/lifetime/CFG summary: `docs/attempts/research-20260924-load-character-followup/README.md`
- Preserved peer context recipes: `docs/attempts/tu-context/transactions/collision_sound_family_20260924-check.json`, `get_string_no_key_wait_20260924-check.json`, and `do_replay_menu_shared_copy_20260924-check.json`

Reproduce with `python tools/tu_context_probe.py game-main src/main.c LABEL --order current --no-prototypes --no-dumps --focus load_character`, adding the seven `--body name=path` entries shown by those recipes for the accepted-context probe.

## Effective-output dedup

`python tools/effective_outcomes.py game-main load_character --pattern 'research-20260924-main-load-character-*.json' --compact --response --baseline research-20260924-main-load-character-current` groups both receipts as one effective outcome, ID `f896246c764546d6`, `DIFFER`, 330 bytes, first +13, exact 63/82, 0/18 unequal relocations, and no gained/lost exact functions. This identity is already present in the prior load-character research, so the recently accepted peer-context overlay adds no new target output class.

## Current-TU pass follow-up (2026-09-24)

To recheck the predecessor hypothesis after the accepted peer-context study, two dump-enabled TU probes were compiled in current order with `--no-prototypes` and identical accepted overlays for the five collision-family bodies, `get_string`, and `do_replay_menu`:

1. maintained `init_game` control: `build/tu-context/game-main/research-20260924-main-load-character-accepted-context-pass-baseline/comparison.json`
2. retained earlier complete `init_game` source snapshot: `build/tu-context/game-main/research-20260924-main-load-character-init-snapshot-pass/comparison.json`

Both compile. Both retain 63/82 exact functions, 79/82 historical predecessor identities, and zero exact-function gains/losses. The retained snapshot leaves `init_game` DIFFER (5676 candidate / 5788 historical bytes). Its changed body causes raw displacement-only changes in `load_character`; `effective_outcomes.py` groups all four saved load-character probe receipts (including the no-dump controls) into one known class, `f896246c764546d6`: DIFFER, size 330, first +13, 0/18 unequal relocations, 63/82 exact. Dump-enabled and no-dump accepted-context receipts also deduplicate, so dump collection did not change the effective target output.

I compared the `load_character` function sections in `main.c.181r.csa` and `main.c.182r.peephole2` for the dump-enabled maintained and retained-predecessor builds. After normalizing only overlay paths, GCC pointer IDs, and compiler-generated `temp.N` names, each 517-line / 533-line target section is identical. This includes the printed target RTL and liveness notes; the current retained predecessor therefore changes neither the target's local condition/liveness guard nor its effective emitted bytes. `compare_passes.py` performs this diagnostic normalization.

## Precise blocker

The available historically grounded `init_game` source snapshot preserves the same extracted prior scratch choices (`si,di,ax,dx,cx,bx`) as maintained `init_game`; its target `load_character` scratch choices remain (`di,ax`). Thus it does not vary the cursor input in the way needed to test the other factor. The target's local RTL/liveness guard also stays the same. The GCC pass dumps record compiler state at named passes but do not emit `peep2_find_free_register`'s static `search_ofs` or its accepted/rejected scratch candidates; the locked toolchain contains compiler binaries and headers, not GCC implementation source or an instrumented build. No source-supported alternative `init_game` body is available that changes prior scratch choices while preserving historical evidence.

A discriminating next probe needs either (a) a historically evidenced `init_game` body that produces a different prior scratch-choice sequence, checked against the unchanged target RTL/liveness guard, or (b) a TDM GCC 4.4.1 instrumented trace/source that records `search_ofs`, the scratch candidate results, and the target guard at each `peep2_find_free_register` call. More source spelling and another ordinary dump-enabled compile cannot resolve this gap. Keep `load_character` DIFFER until one of those evidence sources exists.
