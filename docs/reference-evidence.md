# Typed global reference prerequisites

The current generator inspects unresolved, independently named global relocations
at aligned absolute 32-bit MOV instructions. It requires matching non-operand bytes,
consistent raw addends and original operands, and original DWARF paths confirmed by
named COFF roots. It never uses the original operand as an acceptance binding.

`docs/current/reference-status.json` summarizes supported observations; full function
cards contain instructions, typed paths, candidate declaration availability and source
line mappings. Missing observations do not establish correct references.

A matching whole-function instruction skeleton gives SYMBOLIC_REFERENCE_DIFFERENCE.
It is SOURCE_DIFFER, not a layout-only body proof. Unknown declarations or missing
fields require OWNER_DECLARATION_REPAIR. A usable field still needs a separately
guarded SOURCE_REFERENCE_REPAIR. The observation alone does not authorize an edit.
When the whole-function skeleton differs, coincidentally aligned instructions remain
ALIGNED_REFERENCE_OBSERVATION and require ESTABLISH_INSTRUCTION_CORRESPONDENCE.

The real check_characters case selects curr_char at +214 where the historical address
identifies play_char.max. The original object is Tmenu_char_selection, 1,036 bytes;
the maintained declaration was a 4-byte int before the verified migration. The generated historical header already
contains value at +0, max at +4, bmp at +8 and pal at +12. Four other observed operands
in new_game/init_game have different function skeletons and are not source-repair claims.

An isolated probe replaced the scalar declaration with its generated type and adapted
two scalar uses to the proved offset-zero value member. It changed no maintained
source or ledger. Every previously exact function stayed exact; initialized .data and
.rdata remained identical. The only .text change was two register-clear bytes in the
already unresolved line_alert (+345 first mismatch, 0xdb to 0xf6). Those changes agree
with the original clear ordering, leaving its separate field-load ordering mismatch.
This is the previously recorded declaration-context effect, not a new function match.

The GLOBAL_TYPE migration gate is now implemented and has accepted this migration.
It regenerates the exact declaration/access edit recipe, checks the generated header
and full DWARF layout, and independently compiles a declaration-only COMMON witness.
The witness distinguishes the 1,036-byte type from GCC's 1,040-byte allocation.
All other allocated contributions and existing exact proofs must remain preserved.

An exact function's offset-zero access can change only through this generated recipe,
with identical instruction bytes and relocation evidence before and after. A
BODY_MATCH_LAYOUT_BLOCKED function cannot be adapted. The candidate-only independent
register-clear projection never grants historical FUNCTION_MATCH status.

Real acceptance passed fresh compilation, focused negative controls, the ordinary
link check and atomic publication. The unrelated max_speed link blocker remains.
A deliberate out-of-scope .max access was rejected before compilation. The first
COMMON-size check also failed safely; the corrected gate uses compiler evidence,
not a guessed alignment rule. See attempts/global-type-scope-rejection.json,
attempts/global-type-allocation-mismatch.json and
attempts/interfaces/global_type_main_play_char.jsonl. The earlier isolated probe
remains in attempts/global-type-play-char.json with its reproducible script.

The generated `repair_symbolic_assignment` recipe supports one deliberately narrow
source shape: a plain assignment to a uniquely occurring scalar global, mapped to
one exact maintained-source line. The expected field must already exist with the
same scalar type and width. Whole-function instruction correspondence, decoded
boundaries and both named declarations are required. Local shadowing, macro names,
reads, compound assignments, complex lvalues and ambiguous mappings are rejected.
Existing literal recipes can be combined into the same bounded experiment, avoiding
a known-failing literal-only retry. The recipe is regenerated inside the task;
original addresses remain diagnostic and never supply acceptance bindings.

The real check_characters recipe passed one FAST attempt and strict promotion to
BODY_MATCH_LAYOUT_BLOCKED. Its body and independently resolved references now agree;
seven same-CU transfer operands still depend on layout. The body is protected from
further grinder edits. The worker selected the explicit layout-blocked claim rather
than passing it through default exact promotion. Review evidence is preserved in
attempts/game-main/check_characters-supervisor-review.json; the full automated run
is attempts/pattern-runs/20260920T220619035711Z.jsonl.

A post-promotion real admission check attempted the ordinary body-edit command and
was rejected as BODY_MATCH_LAYOUT_BLOCKED. Source and ledger identities stayed
unchanged and no task session was created. Evidence is preserved in
attempts/check-characters-layout-admission.json. The expanded 213-test suite and
global audit passed after these changes.
