# `main_menu_callback` presentation reconstruction (2026-09-23)

## Result

The current production callback still has an explicitly marked placeholder
welcome section. Original source-line mappings, disassembly, and `.rdata`
references support replacing only that section with the version and welcome / rank
presentation retained in `docs/attempts/game-main/main_menu_callback-rank-candidate.c`.

I made that replacement in an isolated copy of the current production function
and compiled it in current definition order with `--no-prototypes`. The whole-TU
probe compiled cleanly and retained 63 exact functions with no losses. The
target remains `DIFFER`; this recovers a historically evidenced source block,
not the full function.

## Historical facts supporting the block

From `python tools/function_lines.py game-main main_menu_callback --source-view 5225 5253`:

- Original lines 5231–5232 each call `textprintf_ex` with literal format
  `v%s %s` and literal version `1.5.1`. Their coordinates are `(5,3)` and
  `(4,2)`; their `makecol` arguments are `(100,21,20)` and `(162,90,51)`.
  The suffix is ` FUN MODE` when `debug` is set and the empty string otherwise.
- The `stricmp(profile->handle, "guest")` test branches to guest text. The
  non-guest branch calls `get_rank_id(profile)`, chooses between
  `Your rank is %s.` and an empty suffix, and formats `Welcome, %%s! %s` into
  the historical `welcomeMessage` local at `fbreg -544`.
- The non-guest path calls `get_rank(profile)` and
  `textprintf_right_ex` four times at `(638,3)`, `(637,3)`, `(637,2)`, and
  `(636,2)`, with the observed shadow/highlight colors. The guest path copies
  the literal `Welcome to Icy Tower! Start a profile in the profile menu.`
  (0x3b bytes including NUL) and draws it at those same four positions.
- All original `get_rank_id`, `get_rank`, `sprintf`, `strcpy`,
  `textprintf_ex`, and `textprintf_right_ex` call sites are represented in the
  isolated replacement. No data is inferred from a candidate-only string.

## Isolated artifacts and probe

- Presentation-only function overlay:
  `docs/attempts/research-main-menu-presentation-20260923/main_menu_callback-presentation-only.c`
- Compile-only `get_rank` declaration overlay:
  `docs/attempts/research-main-menu-presentation-20260923/rank-declaration.json`
- Whole-TU receipt:
  `docs/attempts/tu-context/game-main/luna-main-menu-presentation-current-noproto-20260923.json`
- Full strict object/function comparison and object:
  `build/tu-context/game-main/luna-main-menu-presentation-current-noproto-20260923/comparison.json`
  and `unit.o` (with `dwarf.txt`, interface output, and GCC pass dumps nearby).
- Exact probe: `python tools/tu_context_probe.py game-main src/main.c
  luna-main-menu-presentation-current-noproto-20260923 --order current
  --no-prototypes --body main_menu_callback=docs/attempts/research-main-menu-presentation-20260923/main_menu_callback-presentation-only.c
  --declarations docs/attempts/research-main-menu-presentation-20260923/rank-declaration.json
  --focus main_menu_callback`.

Observed probe result: 63 exact functions before and after; no gains, no losses,
no new implicit declarations. `main_menu_callback` remains `DIFFER`, with 3,387
candidate bytes versus 3,741 historical bytes. Its direct-edge diagnostic
reports the historical `LoadCursorA` edge missing because this presentation-only
overlay intentionally leaves the unrelated cursor code untouched. No function
was accepted based on size or masked equality.

## Limits / remaining evidence work

The added `get_rank(Tprofile *)` declaration is only an isolated compile input;
the existing note `docs/attempts/game-main/main-menu-rank-20260923.md` records
that `profile.c` defines `get_rank(Tprofile_rank *)`. This probe does not resolve
that interface/type topology. The current card also retains unresolved `.rdata`
relocation ownership and broad body differences, so the supported presentation
block is not enough for strict function equality. I did not combine the retained
cursor, fixed-point head motion, or face-reset changes into this probe.

No maintained `src/`, generated current state, or recovery ledger was edited.
