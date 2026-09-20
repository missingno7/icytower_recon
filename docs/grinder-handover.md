# Reconstruction grinder handover

Start with `python tools/next_frontier.py`, then open the first CHEAP task card.
[The short workflow](grinder.md) gives the commands for each task kind. Do not read
historical experiment prose until a card points to a specific relevant experiment.

The production line now provides:

- A generic canonical DWARF type database, 35 generated game typedef headers,
  member/size assertions, bounded duplicate-struct migrations, and separately checked
  partial-view aliases. Generated headers import only required declaration owners.
- Cards for all 253 inventoried functions, with compact diagnostics and complete
  function-only evidence, locals/scopes/types, calls, data owners and compiler rules.
- Persistent fine-grained classifications, protected proven bodies and a ranked
  CHEAP/MEDIUM/SUPERVISOR queue. The cheap default excludes supervisor work.
- FAST owning-CU checks and scope-enforced sessions with three attempts. Failed
  compiles and candidates survive blocking; the original task source is restored.
- Fresh exact promotion with independent relocations/decoded direct targets,
  source/toolchain identities, exact-neighbor protection, focused tests, ordinary
  link regression checks, ledger receipts and global audit.
- Serialized publication with exception rollback and a durable crash-recovery
  journal. Manual success claims contradicting a receipt fail the audit.
- Complete static-storage declaration census and a scope-repair gate with raw code
  preservation. Missing/scope/type/initializer evidence appears on target cards.
- Real GCC depfile fingerprints, separate proof/diagnostic invalidation, canonical
  main.c identity, interface conflict cards and mechanical declaration repair.

Real validation covers draw_scroller, add_floor, create_profile, main.c helpers,
layout protection, false-promotion rejection and exact re-certification. Additional
accepted examples are HTTPFetchInternal qualifiers, create_post's void prototype,
new_rand's missing prototype and shared Tmenu_slider canonicalization. The named
object resolver established startGameMusic and datafile_callback_slow ownership
without body edits; wrong targets and corrupted initializers remain rejected.
Further accepted production-line examples restore scroller's DWARF definition
order, repair rankFloors's 16-to-12 array extent, and canonicalize Tmenu in two CUs.
Every affected body and existing exact function proof survived acceptance.
Relocation-aware initializer proof now establishes jcLabels, comboNames, version_str,
hisc_names and ten menu owners. The DATA_POINTER workflow independently identified
ctrl_menu[4].data as options.jump_hold, applied that single symbolic expression, and
proved ctrl_menu, opt_menu and main_menu through their initializer dependencies.
The complete accepted attempt is retained under docs/attempts/interfaces/.

No object/CU/executable match follows from these function or interface claims.
No runtime replay is used. The ordinary game link still reports max_speed.

The generated queue now includes declaration, canonical-type, compatible partial-view,
definition-order and array-extent work. Use its live counts instead of historical
milestone totals. No unresolved body is currently classified CHEAP: bounded probes
demonstrated cross-function compiler sensitivity in the last two apparent easy
cases. They now have explicit supervisor evidence instead of repeated body guesses.
Readiness is not yet majority-body automation. Mechanical declaration/data work
supplies the inexpensive queue. Large control-flow
mismatches, partial profile type views, unresolved initializer graphs and ambiguous
anonymous data still need supervisor interventions. Keep lowering those recurring
costs; do not relabel them CHEAP merely to improve counts. Current counts are in
[the generated queue](current/grinder-queue.json).

The first command prints one task by default. FAST now annotates nearby instructions
with live DWARF register/stack associations and reports original/candidate builtin
declaration differences. GCC context findings and failed alternatives are captured
in [compiler-context evidence](compiler-context-evidence.md), with focused RTL probes.
These diagnostics do not weaken original-byte acceptance.

A localized guard task also completed the full body-edit loop: fadeIn changed
one wait condition using two decoded branch differences and passed in one FAST
attempt. Its resolved body is exact; the same-CU call displacement remains explicitly
BODY_MATCH_LAYOUT_BLOCKED. The strict gate now rejects a generic FUNCTION_MATCH
claim for such a body and requires the layout claim printed by FAST. The successful
example and original mismatch are retained in docs/attempts/localized-guard-example.json.


Two TYPE_VIEW examples passed acceptance: Tprofile_extra and Tprofile_create now
alias the generated Tprofile. Every body and emitted contribution survived; the
full-size example also preserved sizeof behavior. The ambiguous rank view was
refused with source and ledger unchanged. Six compatible view tasks remain in the
current queue; the card supplies relevant members and links full type evidence.

The first migration exposed unnecessary Allegro/stdio imports in every generated
header. That failed compile was retained, source restored, and dependency generation
fixed from DWARF declaration owners. All 35 headers compile together, builtin-only
Tprofile compiles with partial library interfaces, and all 25 CUs were re-verified.

Interface reports distinguish compatible explicit aliases from same-name layout
conflicts. create_profile still has a real cross-CU Tprofile discrepancy in main.c;
matching declaration spelling no longer hides it. Game aggregate layouts are checked
fully. External library types still use declaration-spelling checks, and missing
layout evidence is labeled unavailable rather than a proved mismatch.


Local declaration evidence now includes compiler source files/lines, storage sizes
and parameter-versus-local roles. LOCAL_DECLARATION permits a single evidenced
function-scope builtin declaration edit. Acceptance preserves emission or requires
a strict exact target-function proof; a declaration match is never presented as a
function match. The real scroller_step const repair passed with unchanged code and
main_menu_callback still SOURCE_DIFFER. Parameter and protected-body observations
redirect to existing tasks rather than duplicating queue work.

STACK_FRAME_LAYOUT now distinguishes observed entry-allocation mismatches from
register selection. Eighteen real functions had this first difference. Their cards
include unique-name local-width evidence and an explicit limit: allocation alone
does not prove which local, spill, outgoing argument or lifetime caused it. See
[stack-frame evidence](stack-frame-evidence.md). Width changes and inferred literal
array extents remain bounded supervisor evidence, not blind padding edits.

Storage-scope validation is documented in [storage-scope-evidence.md](storage-scope-evidence.md):
one declaration repair passed strict acceptance; a second was rejected for BSS
reordering, preserved as evidence and restored automatically.

Generated mechanical work can run without per-task model reasoning using
`python tools/mechanical_grinder.py --limit 3`. The same scope, proof, rollback
and publication gates apply. Body cards now include decoded instruction-order
windows, maintained-source line mappings, and bounded source experiments where
available. Unknown or context-sensitive remnants still route to a supervisor.

The mechanical worker accepted historical source-order tasks for game_data and hisc. Its fld_adspot trial was restored and blocked; a narrow terminal-JMP layout proof now distinguishes the wrapper from the still-unresolved CSV-reader literal. See [branch relaxation evidence](branch-relaxation-evidence.md).
