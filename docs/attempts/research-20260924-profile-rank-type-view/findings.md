# `set_next_rank_message` source-local historical type view

Date: 2026-09-24

## Question

Can the candidate source retain its 140-byte rank-specific access view while
presenting the historical `Tprofile *` interface to the compiler, without
changing the exact emitted function or other exact profile peers?

## Historical and current evidence

- The focused card `docs/current/functions/profile/set_next_rank_message.json`
  records a strict 431-byte `FUNCTION_MATCH`; this body is protected.
- The interface card `docs/current/interfaces/set_next_rank_message.json`
  blocks on parameter 2: historical DWARF says `Tprofile *` (1360 bytes),
  while candidate prototypes/definition say `Tprofile_rank *` (140 bytes),
  with 37 aggregate-member differences.
- `include/recovered/Tprofile.h` places `best_floor`, `best_combo`,
  `ccc[0]`, and `no_combo_top_floor` at offsets 76, 80, 136, and 88.
  The local `Tprofile_rank` view maps its `score`, `combo`, `ccc`, and
  `no_combo_lost` fields at 76, 80, 88, and 136 respectively. This makes an
  explicit cast suitable for preserving this body’s current accesses; it does
  not make the two aggregate layouts identical.
- The retained `view_profile` typed-signature experiment at
  `docs/attempts/research-20260924-view-profile-interface/README.md` documents
  a source-local prototype technique that preserved all then-exact profile
  functions. The experiment below extends that technique to a distinct local
  field view; it does not reuse or alter the prior result.

## Probes

Both candidates are isolated overlays for the current `src/profile.c` path;
neither edits production source, current cards, recovery state, or tools.

1. `profile_cast_per_access.c` declares both prototypes and the definition as
   `void set_next_rank_message(char *, Tprofile *)`, and casts to
   `Tprofile_rank *` at rank-view accesses.
2. `profile_local_alias.c` has the same historical interface, but creates one
   local `Tprofile_rank *rank_view = (Tprofile_rank *)p` and uses that view.

Commands (respectively):

```text
python tools/tu_context_probe.py game-profile src/profile.c profile_rank_type_cast_access --order current --no-prototypes --focus set_next_rank_message --research-base docs/attempts/research-20260924-profile-rank-type-view/profile_cast_per_access.c --no-dumps
python tools/tu_context_probe.py game-profile src/profile.c profile_rank_type_local_alias --order current --no-prototypes --focus set_next_rank_message --research-base docs/attempts/research-20260924-profile-rank-type-view/profile_local_alias.c --no-dumps
```

The generated `interfaces.aux` for the first probe reports the historical
`extern void set_next_rank_message(char *, Tprofile *)` at both declaration
sites. The local-alias variant uses that same signature.

## Results

- Each full-TU overlay compiled and kept all 11 exact profile functions; none
  of the 11 were lost. The focused target remained a strict 431/431
  `FUNCTION_MATCH` at the same contribution position in both probes.
- The target’s relocation resolutions also remained equal to historical
  values. Both source forms produced the same target instruction-sequence
  hash: `322c7c62bec2c8938f26f8444f618bb10f17174c8d772fa79d8d02b4c64c4ddd`.
  Thus the two candidate forms are one effective emitted-body outcome, not two
  distinct wins.
- The probe is not a whole-CU acceptance result: the CU has 17 historical
  functions, only 11 strict function matches, and whole text, relative layout,
  object, and CU equality all remain false. The comparison inventories 799
  object relocations and no common allocations, but states that original
  relocation records are unavailable and full initialized-data/BSS/DWARF
  equality is not established. No conclusion about `OBJECT_MATCH` or
  `CU_MATCH` follows from this interface probe.

## Conclusion from the initial overlay set

The initial overlays establish only that casts/aliases can preserve emitted
bytes. They change the protected function source island and therefore are
research evidence, not promotable candidates. Their earlier suggested planner
path is withdrawn; do not weaken body protection or treat them as candidate
repairs.

## Follow-up: exact source island constraint

To test whether declarations alone can report the historical interface, I
copied current `src/profile.c` verbatim to
`profile_declaration_only.c` and changed only its two forward declarations
from `Tprofile_rank *` to `Tprofile *`. The definition and function body remain
byte-for-byte source-identical. The current-order same-path TU probe failed at
the unchanged definition:

```text
compile: FAILED
profile.c:302: error: conflicting types for 'set_next_rank_message'
```

This is the expected C type-compatibility barrier: the historical declaration
type and the definition's `Tprofile_rank *` are distinct pointer types, so a
prototype-only edit cannot describe the historical function type while
remaining compatible with the definition. The exact body itself also uses
rank-view-only member names (`score`, `combo`, `no_combo_lost`) that do not
exist on `Tprofile`; making a `Tprofile *` definition type-check would require
changing expressions inside the protected function source island or adding an
artificial field-aliasing construct. Such casts/aliases within the body were
already shown to preserve code bytes, but are explicitly not eligible because
the body is `FUNCTION_MATCH`; synthetic macro/union tricks are excluded.

Therefore no declaration/type repair satisfying the source-island constraint
was found. The blocker is the mismatch between the definition's required
rank-specific source type and the historical nominal parameter type, combined
with the protected body's rank-only field accesses. Leave `TYPE_LAYOUT_BLOCKED`
in place and request a new discriminator only if independent historical
evidence can establish a non-synthetic type identity compatible with both
types. No source, planner, card, or recovery state was changed.
