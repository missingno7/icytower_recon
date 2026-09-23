# `main_menu_callback` rank interface and retained candidate (2026-09-23)

## Interface finding

The caller-side type used by the historical `main_menu_callback` is supported
as `Tprofile *`:

- Original main-CU DWARF identifies global `profile` as `Tprofile *`; the
  generated storage card `docs/current/storage/game-main/138025.json` confirms
  that original and current caller declarations agree.
- At original offsets 1927–1935 (line 5237), the code loads `_profile` and
  stores that pointer unchanged as `get_rank_id`'s sole stack argument.
- At offsets 1979–1987, 2099–2107, 2219–2227, and 2339–2347 (lines 5238–5241),
  each `get_rank` call likewise receives `_profile` unchanged. There is no
  offset adjustment or construction of a `Tprofile_rank` temporary.
- The original profile-CU `get_rank` DIE in
  `docs/current/interfaces/get_rank.json` also records `char *(Tprofile *)`.

The cross-CU interface is still blocked. The same current card reports that
candidate `src/profile.c` declares/defines `get_rank(Tprofile_rank *)`, and
`src/profile.c:297` passes that type into rank-field accesses. `Tprofile_rank`
is 140 bytes while recovered `Tprofile` is 1,360 bytes; the generated card
reports 37 member differences. The `get_rank_id` card has the same conflict.
Pointer width and call ABI therefore do not reconcile the aggregate meaning.
The caller-side `extern char *get_rank(Tprofile *)` used below is supported for
the original main-CU call site, but it does not resolve the callee-side source
or type-topology conflict and must not be treated as a recovered shared
interface.

## Full retained-candidate probe

I compiled the retained full callback (`cursor`, fixed-point head motion,
face-reset ordering, and presentation) in the production-equivalent current
main-TU order with `--no-prototypes`, using the caller-side declaration above
and the required Allegro cursor include. The result is diagnostic only:

- The whole-TU probe compiled successfully; exact matches stayed **63 before /
  63 after**, with no gains, no losses, and no new implicit declarations.
- `main_menu_callback` remains `DIFFER`, 3,775 bytes against 3,741 historical
  bytes. Its direct-call diagnostic reports **zero missing historical direct
  edges**. Ten additional source/candidate edges are listed, nine explained by
  inlining; the remaining builtin-memcpy edge is a compiler builtin. This is
  not a strict function match.
- Effective code for unchanged bodies changed in `my_alert` and
  `do_replay_menu`; the probe reports no exact-function losses. Several raw
  call fields also move with the whole-TU layout. Whole text remains unequal.
- First differing byte is offset 14, the initial `count` reference: the
  candidate relocation resolves to `0x4dd744`, while original bytes refer to
  `0x4dd318`. The next initial storage reference at offset 41 (the `face`
  access) resolves to `0x4dd740` versus historical `0x4dd31c`. After those
  storage fields, the first clear instruction-selection difference is around
  offset 72: historical loads `pFLDAd` into ESI, while the candidate loads it
  into EAX. This is only a register-allocation observation; it does not
  establish the source cause.

No attempt was made to force the data placement or chase the remaining function
size. The probe shows that combining the supported presentation and retained
menu work preserves the exact-neighbor set but does not recover the function.

## Artifacts

- Full retained candidate copy:
  `docs/attempts/research-main-menu-rank-interface-full-20260923/main_menu_callback-full-retained.c`
- Isolated caller-signature/include overlay:
  `docs/attempts/research-main-menu-rank-interface-full-20260923/rank-declaration-caller-type.json`
- Whole-TU receipt:
  `docs/attempts/tu-context/game-main/luna-main-menu-full-retained-current-noproto-20260923.json`
- Object comparison and GCC dumps:
  `build/tu-context/game-main/luna-main-menu-full-retained-current-noproto-20260923/`
- Current interface blocker: `docs/current/interfaces/get_rank.json` and
  `docs/current/interfaces/get_rank_id.json`.
- Original caller evidence: `python tools/function_lines.py game-main
  main_menu_callback --source-view 5236 5241`.

All edits and artifacts for this turn are isolated under this new research
folder or the normal ignored build/probe directories. No maintained source,
current state, or recovery ledger was changed.
