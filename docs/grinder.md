# Cheap grinder workflow

The historical CUs and strict static oracle remain the acceptance boundary. Start with
`python tools/next_frontier.py`: it displays the next CHEAP task and the remaining count from
`docs/current/grinder-queue.json`. Generated current documents supersede prose in
old experiment notes; `src/recovery.json` is the canonical, receipt-checked ledger.
Use `--limit 5` for a small batch or `--all` for explicit supervisor inspection.

## Isolated research lane

The three-attempt limit below applies to an active production body task. Longer
research uses separate candidate files or TU probe overlays under a unique
`docs/attempts/` directory and unique probe labels. It must not edit maintained
`src/`, generated current state, accepted bodies or `src/recovery.json`. Workers
may investigate MEDIUM/SUPERVISOR tasks, types, callers, ABI, compiler passes and
whole-TU context in this lane. Existing `tu_context_probe.py` compiles historical
order with explicit body overlays; its result is diagnostic and cannot be promoted.
When probing the already promoted `main.c`, preserve its declaration context:
`python tools/tu_context_probe.py game-main src/main.c LABEL --order current
--no-prototypes ...`. The maintained file already contains generated forward
declarations. The probe's default `auto` setting appends another block and
changes unchanged function code. A production-equivalent `--no-prototypes`
control was checked against the current report: 62/82 exact, `play` 17,400
bytes, and no unchanged-body code changes. Use `--order historical` or new
prototypes only when that context change is itself the hypothesis being tested.

Continue while a probe yields a new effective output, eliminates a specific
hypothesis, establishes a type/CFG/context fact, or reveals a missing capability.
When multiple source forms collapse to the same output, move to declarations,
interfaces or TU/compiler context rather than spending more cosmetic variants.
`python tools/effective_outcomes.py game-main play --pattern 'LABEL*.json'`
groups saved TU outcomes without debug-byte noise; compare its identities only as
search evidence. `python tools/direct_call_counts.py game-main play` compares
original and compiled direct-call multiplicities, resolving COFF relocation and
same-CU targets; equal counts are diagnostic only. Archive source, compiler output
and negative trials, and hand off
the strict status, unique outcomes, established facts, exact blocker and smallest
artifact paths. Any exact candidate enters the serialized FAST/ACCEPTANCE workflow
with its ordinary production gates; an isolated probe is never a match claim.

1. Select the highest-ranked CHEAP task and read its `candidate_card` only.
2. For a FUNCTION_BODY task, run its `begin_command`. This fresh-verifies the CU and snapshots the permitted
   function body and every maintained source/header/tool. One task may be active.
3. Edit only that function body. The card supplies prototype, parameters, local
   types/encodings/locations, lexical ranges, relevant generated types and field
   offsets, globals/data ownership, calls, line evidence, first difference,
   disassembly windows, compiler flags and applicable codegen rules.
4. Run its `verification_command` (FAST). This compiles just its owning CU with
   TDM-2, checks all CU functions and relocations, and prints target diagnostics.
   Read `build/fast/<target>/<function>.json` for the focused result. Its
   `detailed_evidence` link supplies complete evidence for that function only; the
   primary card keeps the closest mismatch entries and records complete counts.
5. Make at most three evidence-backed experiments on one hypothesis. The FAST
   command enforces this limit within the active session. Failed
   FAST and promotion attempts retain the source body, input identities and
   concrete first mismatch in `docs/attempts/<target>/<function>.jsonl`.
6. When FAST reports FUNCTION_MATCH, run the FAST result's `promotion_command`.
   A remaining CU-layout blocker requires its explicit `--claim BODY_MATCH_LAYOUT_BLOCKED`;
   the generic FUNCTION_MATCH claim is rejected in that case. ACCEPTANCE
   recompiles, checks independent relocations and decoded same-CU targets,
   protects exact neighbors, validates scope and input identities, runs focused
   tests, checks the ordinary game link after source changes, atomically publishes
   the verified ledger and current documents, and runs the global audit.
7. Commit only the task source and generated proof/status changes after acceptance.
   Preserve any pre-existing unrelated working-tree changes. Then read the queue again.

Never edit `src/recovery.json`, generated headers or current cards by hand. Never
add compiler switches, volatile qualifiers, inline assembly, binary fallbacks,
guest-address dispatch, or per-function placement to manufacture equality.
Do not change prototypes, shared types or data in a body task. Those require a
separate interface task described below, or supervisor review and the affected
dependency closure for other changes.

`FUNCTION_MATCH` retains the existing exact function proof (independently resolved
relocations and direct targets). `BODY_MATCH_LAYOUT_BLOCKED` is an additional
workflow state: a proven body has displaced same-CU operands in the partial layout,
or an exact prefix and identical final target require different short/near JMP
encodings. A range-relaxed function remains raw DIFFER and does not count as an
exact function. Both workflow states prohibit body edits. CODEGEN_SIMILAR with unresolved data
ownership also prohibits grinder body edits, but **does not** claim proven layout-only
correctness. None of these states is OBJECT_MATCH, CU_MATCH or a playable-game claim.
COMPILER_CONTEXT_DEPENDENCY also prohibits cheap body edits: a peer-definition
probe changed target code without changing its body. It remains SOURCE_DIFFER,
not a layout or exact proof. The card links the observation and supervisor command.

On an unknown failure, stop experimenting and run:

```
python tools/grinder_task.py block <target> <function> --reason "Exact failure and attempted changes"
```

This also works when compilation fails. It captures the failed candidate, marks BLOCKED_SUPERVISOR, restores the task
source byte-for-byte, and excludes the task from cheap selection. Then take the
next CHEAP task. Do not use `--medium` or `refresh_recovery.py --verify-all` as a
cheap-task escape hatch. If no CHEAP task remains, report the supervisor queue.

For an INTERFACE, CANONICAL_TYPE, SOURCE_ORDER, ARRAY_EXTENT, DATA_POINTER, TYPE_VIEW or LOCAL_DECLARATION task, read its small card and run its listed `begin_command`,
`apply_command`, `verification_command`, then `promotion_command`. Apply makes
only the generated source edits; do not manually change the function body.
Canonical type tasks replace exact duplicate member declarations with the generated
header and active layout assertions. TYPE_VIEW handles separately evidenced compatible partial views; member differences
and separate struct-tag users still require supervisor review.
The gate recompiles the actual affected dependency closure, compares every
maintained declaration with the unique DWARF signature, and preserves all exact
function proofs, source bodies, data/BSS/relocations and allocated layout.
Declaration UID changes may renumber compiler static symbols, reorder adjacent
independent immediate writes (register clears, constant register loads and constant
stores to disjoint stack slots), or swap the operands of a compare whose ordering
condition is inverted at the following jump when the flags die there. These narrow
candidate preservation checks never supply FUNCTION_MATCH evidence; the original
comparison still requires exact bytes.
Any other emission change fails. Use `python tools/interface_task.py block <name>
--reason "Exact failure"` to restore and route a failure to the supervisor.
All these task types support `abort` with a reason to restore without blocking.

SOURCE_ORDER moves complete definitions according to unique original DWARF source
lines. Every body remains byte-identical. The gate preserves exact functions,
proved initialized objects and common allocations, and rejects newly implicit
calls. Natural layout may change; no executable-address placement is allowed.
ARRAY_EXTENT replaces only an evidenced builtin array bound. It preserves every
initializer and body, requires unchanged emitted contributions, and accepts only
after the complete original DWARF type and independently resolved initializer match.
Their completion claims are HISTORICAL_SOURCE_ORDER and ARRAY_EXTENT_MATCH;
neither substitutes for a function proof.

DATA_POINTER replaces one explicit symbolic address in a typed initializer. The
card identifies its array/member path and the independently evidenced original
and candidate targets. Acceptance requires complete original type/initializer
ownership, identical raw code, and identical data/layout/relocations outside that
four-byte field. It never writes an original numeric address into source.
WAITING_FOR_OWNER means the symbolic initializer is already correct: repair the
named dependency first and leave this initializer alone. Full ownership is then
re-evaluated automatically. DATA_POINTER_MATCH is a data repair claim, not a
function or CU match.

TYPE_VIEW uses matching original/candidate pointer-variable evidence to propose
one canonical typedef alias. Named field offsets, types and qualifiers must agree;
only unreferenced byte-array filler can be removed. The gate preserves all bodies
and emitted contributions and requires the complete canonical layout in fresh
DWARF. An alias is not permission to rename fields or alter body expressions.
Unexplained view members remain supervisor tasks with original offset evidence.
Explicit aliases to compiled generated headers normalize interface spelling only
after full layout equality; unrelated equal-sized structs are never merged.
Generated headers import library declarations only when their DWARF types need them.

STATIC_SCOPE moves one unchanged file-static BSS declaration into its recorded
historical function scope. Use only the generated two-span edit through
`interface_task.py`; expressions, types and initializers are immutable. The gate
requires identical raw machine text and allocated contributions, fresh complete
DWARF/COFF ownership, and preserved existing owners. Proven function bodies remain
ineligible. Common-to-static moves and unresolved lexical scopes need a supervisor.
A CODEGEN_SIMILAR body can receive this declaration-only repair; it does not grant
permission to edit its expressions or claim ownership from masked code equality.

`docs/current/storage-status.json` inventories storage evidence across all CUs.
Each function's `storage_declarations` links only its relevant object cards. These
expose missing declarations, scope/type differences and owner failures previously
skipped by name/scope matching. COMMON_DECLARATION_AGREES confirms a declaration,
not common allocation order or object/CU equality. Similar content never silently
binds renamed objects.

LOCAL_DECLARATION uses a unique function-scope local, the compiler's source-file
and line mapping, and its original DWARF type to generate one declaration edit.
Parameters remain interface tasks. Protected bodies, static storage, macros,
multiple declarators, inferred literal-array extents and ambiguous scopes are not
eligible. Initializers and all other source are immutable. Width-changing types
and pointer/array role changes retain evidence for supervisor review.

LOCAL_DECLARATION_MATCH proves the local type only. Acceptance either preserves
emitted contributions or requires the changed target to pass the strict exact
function oracle, while preserving non-code contributions and existing exact
neighbors. A still-different body with changed emission is rejected. Read the
reported function status separately; correcting a declaration does not imply a
FUNCTION_MATCH. Failures retain the candidate and restore through block/abort.

If a process is interrupted during acceptance, run
`python tools/recover_promotion.py`. It refuses a still-running publisher and
restores the previous ledger/current files from the durable journal. The task
source remains available to recheck, retry promotion, or block. Do not delete
publication locks or edit receipts manually.

Supervisor maintenance:

- `python tools/generate_types.py --check` checks DWARF-derived headers/database.
- `python tools/refresh_recovery.py` refreshes derived views from current receipts.
- `python tools/refresh_recovery.py --reanalyze` refreshes changed diagnostic
  logic from source-current byte proofs; it refuses changed verifier/compiler inputs.
- `python tools/refresh_recovery.py --check` checks every generated current view.
- `python tools/refresh_recovery.py --verify-all` freshly verifies all 25 CUs,
  rejects regressions/protected-body edits, and publishes together under a lock.
- `python tools/test_grinder.py` and `python tools/test_interface_tasks.py` run
  the focused negative controls; `tools/test_data_owners.py` checks independent
  object ownership without using tested instruction operands.
- `tools/test_dwarf_locations.py` checks scoped live-variable/signedness attribution;
  `tools/test_compiler_context.py` ensures observations cannot grant match status.
- `tools/test_branch_diagnostics.py` checks the narrowly localized guard route.
  Equal indirect calls elsewhere do not exclude a task when only a few conditional
  opcodes differ and every target/remaining resolved byte agrees. This routing
  evidence never substitutes for exact acceptance.
- `tools/test_stack_diagnostics.py` checks bounded entry-allocation observations;
  STACK_FRAME_LAYOUT is a source-difference category, never a layout-only body proof.
- `tools/test_local_declarations.py` checks compiler-located declaration scope,
  parameter/body protection and the preservation-or-exact acceptance boundary.
- `tools/test_type_views.py` checks partial-view and alias safety; `tools/test_type_headers.py`
  compiles all generated headers and checks isolation from unrelated library declarations.
- `tools/test_data_tasks.py` checks typed initializer paths, symbolic-only repair,
  owner dependencies, ambiguous targets and preservation outside the allowed field.
- [Compiler-context probes](compiler-context-evidence.md) isolate recurring GCC
  behavior. FAST cards include unique-name builtin type differences and live DWARF
  operand associations; both are diagnostic evidence, not assumed source causes.
- `python tools/test_pipeline.py` freshly builds test CUs and runs the existing
  static-oracle/independence tests. It is a supervisor/global check, not FAST.
- Resolve one recurring blocker class, record evidence and failed alternatives in
  `docs/codegen-rules.json`, add a meaningful regression test, then refresh cards.

Declaration conflicts are in `docs/current/interface-conflicts.json`; these are
conservative comparisons of DWARF with historical GCC `-aux-info` declarations,
including differing partial struct views and unprototyped declarations. Same-named
game aggregates are compared by full layout; missing layout evidence is marked
unavailable. External library types retain spelling checks. Inspect
the reported return/parameter types before changing anything. Nominal aliases can
need supervisor review; do not mechanically merge them based on spelling alone.

The ordinary recovered-game link closed on 2026-09-21 after player.c regained its
historical `max_speed` and `gravity_modifier` data objects; `docs/current/link-status.json`
records the linked result and `--verify-all` refreshes it. A promotion must not add
unresolved symbols or regress the successful link. The linked executable is never
executed by the pipeline; a link is not a function, CU or behavioral claim.

## Mechanical batches and source experiments

`python tools/mechanical_grinder.py --limit 3` runs up to three ranked CHEAP
mechanical tasks. It uses the existing begin/apply/FAST/ACCEPTANCE commands,
regenerates the queue after each outcome, and never edits a function body task.
A failed FAST task is recorded, restored and marked BLOCKED_SUPERVISOR before
continuing. An acceptance or infrastructure failure restores when safe and stops
for review; it is not mislabeled as a source blocker. An unfinished publication
journal stops the worker without restoring files over the transaction.
The run retains command outputs and an outcome history in `docs/attempts/mechanical-runs`.
Review and commit accepted changes after the batch; the worker does not commit.

For body tasks, `instruction_order` identifies small decoded instruction
permutations and candidate line-program locations. INSTRUCTION_ORDER is an
observation, never equality or layout-only proof. `source_patterns` can provide
an adjacent-assignment hypothesis. Begin the named body task, then run its
`application_command` and FAST verifier. The application tool recomputes the
pattern from source-current proof, checks the ledger identity, and refuses edits
outside that function or stacking on an already edited body. Three FAST attempts
remain the limit. The normal strict promotion gate is unchanged.

Register-clear permutations can depend on declaration UID changes elsewhere in
the CU. Read attached context rules before spending source trials. The retained
`line_alert` experiment fixed the field-load ordering, but reversing its zero
assignments did not repair the remaining clears. That task was restored and
blocked for supervisor review; no function-match claim was made.

The focused verifier also reports `tail_jump_layout`. A 2/5-byte terminal JMP
change is a layout blocker only when its complete prefix, independently resolved
target and range constraint are proved. Do not lengthen code, add padding, alter
flags, or edit a protected body to force the encoding. Source-order acceptance may
preserve this explicit layout proof while the raw function status remains DIFFER.


Generated body experiments can run with `python tools/pattern_grinder.py --limit 3`.
This selects only CHEAP function cards with exactly one generated pattern. It uses
fixed tool arguments, recomputes the edit from current receipts, changes only the
named body, runs one FAST attempt and then strict promotion. A failed FAST is
recorded, restored and blocked; acceptance or infrastructure failures stop the run.
An unfinished publication journal stops cleanup so recovery can restore state first.
The worker does not invent source edits or commit changes.

`LITERAL_CONTENT_DIFFERENCE` is a source diagnosis, not a layout blocker. Matching
instruction shapes can still reference the wrong filename format, file mode or
logging text. Cards show original and candidate payloads only when the operand
instruction is aligned and its non-relocation bytes agree. String repairs require
an explicit uniquely identified source token; repeated tokens additionally require
compiler line evidence. Empty, macro-generated, concatenated, ambiguous or conflicting
strings do not receive automatic repairs. Equal payloads remain
`CONTENT_EQUAL_OWNER_UNPROVEN` until the existing independent resolver proves ownership.
The original instruction operand is never used as a relocation acceptance binding.

Typed global-reference prerequisites are in [reference-status.json](current/reference-status.json) and the function card. SOURCE_DIFFER may require an owner declaration repair before any body edit. Partial-function address observations do not establish source correspondence. See [reference evidence](reference-evidence.md); the isolated play_char migration has not modified maintained source or bypassed protected-body gates.

Global declaration migrations use generated `GLOBAL_TYPE` tasks through
`interface_task.py`. Apply only the listed recipe: generated aggregate declaration,
header, and proved offset-zero scalar access adaptations. FAST verifies the complete
layout and a separate locked-compiler COMMON allocation witness. Promotion preserves
all existing exact proofs; layout-protected bodies are ineligible. Completion of a
type task does not claim original BSS placement or a new function match.

FAST commands use exit 10 only for a completed verification that rejects the
candidate. Exit 0 means the stated FAST gate passed. Other nonzero exits, including
compiler/input failures and argparse errors, are infrastructure or unknown failures.
Workers restore and stop on those failures; they do not add a source blocker.
Apply/admission/acceptance failures also stop, regardless of exit code. An unfinished
publication journal still prevents automatic cleanup. See `tools/test_task_outcomes.py`
and the worker failure-injection tests for the boundary checks.

For function FAST, success is based on the generated proof state: FUNCTION_MATCH or
BODY_MATCH_LAYOUT_BLOCKED. A raw DIFFER can still have the separately proven narrow
terminal-jump layout state. The explicit promotion claim and body protection remain
unchanged; exit 0 never upgrades layout-blocked evidence to exact function bytes.
Real exit-code validation is in `docs/attempts/fast-exit-contract.json`.

Mechanical FAST and acceptance now write `contribution-difference.json` beside each
fresh CU report. Rejected FAST output and attempt history link it. It identifies
changed allocated sections, normalized relocation/symbol/common metadata, changed
functions, their proof statuses, first byte differences and small disassembly
windows. A bounded instruction permutation is labeled only as an observation;
no dependency or memory-observability proof is implied and the gate is unchanged.

`interface_scope` distinguishes local declaration/type blockers from conflicts in
other CUs. Remote conflicts remain in the global report and the function card, but
do not block a body whose own compiled declarations and checked game layouts agree.
Unknown CU ownership, ambiguous historical signatures and unavailable local evidence
remain blockers. Owning-CU evidence uses the compiled CU, not the header filename.

`source_pattern_prerequisites` lists unresolved relocations not repaired by the
available recipe. A literal or assignment recipe with such prerequisites routes to
SUPERVISOR rather than spending an automatic attempt on a known incomplete repair.
This does not assert that equal literal content proves ownership or layout-only body
correctness. The normal strict promotion gates remain unchanged.


Relocation mismatch interpretation: `comparison_context` distinguishes a decoded
`ALIGNED_OPERAND` from an `UNALIGNED_BYTE_WINDOW` or `ALIGNED_FIELD_UNTYPED`.
When `original_value_is_operand` is false, the raw `original_value` is only the
four bytes at the candidate field offset; instruction-length changes can make it
span opcodes or unrelated operands. Do not interpret it as a pointer, displacement
or ownership conflict. Inspect the supplied instruction pair first. Even an
aligned operand is diagnostic evidence only, never an independent target binding.


Interface layouts omitted by optimized DWARF are collected automatically in a
separate owning-CU debug-retention build (`-fno-eliminate-unused-debug-types`).
Its receipt must preserve the primary source/dependency and toolchain identities,
raw non-debug sections, symbols and relocations. Only missing interface typedef
layouts are supplemented; existing or ambiguous primary definitions take
precedence. Cards label supplemental layouts `EMISSION_PRESERVING_DEBUG_PROBE`.
The primary historical flags, function proof, locals, globals and source-edit
permissions remain unchanged. Missing or conflicting evidence still blocks work.


Typed caller interfaces can also be mechanical: a unique historical signature
may replace a CU-local void-pointer placeholder or implicit/empty caller prototype
with a single pointer to a generated historical type. The plan supplies canonical
header visibility before the declaration. Definitions, return-type changes,
variadic/nondefault calling conventions, shared-header edits, existing type
conflicts and unsupported pointer forms stay with the supervisor. FAST/ACCEPTANCE
require every maintained declaration to agree, complete historical aggregate
layout checks, and the existing whole-CU contribution-preservation gate. A generated
recipe is permission for a bounded experiment, not proof that it will pass.


For a source mismatch, `instruction_alignment` provides at most three short
sequence-diff groups with separate original/candidate offsets and omitted counts.
This helps when an early instruction-length change shifts many later byte offsets.
Resolved relocation values and decoded transfer destinations supply comparison
keys; unresolved fields stay distinct. Repeated sequences can align ambiguously,
and a zero-group result is not equality or semantic proof. Use the strict FAST
status and ownership diagnostics for acceptance, never sequence alignment.


Compiler trial memory appears as `compiler_trials`, including negative results.
Read its freshness state before repeating an omission/type/flag probe. A peer-only
trial can change instruction bytes or the function extent; both are recorded, even
when resolved-byte comparison is unavailable. That observation restricts body
grinding but does not prove the cause is source, padding or branch layout. A
zero-change trial excludes only that experiment at the recorded input snapshot.
Unresolvable baseline bytes never count as a confirmed current baseline merely
because both saved and fresh resolution are unavailable.


Acceptance test groups run through `tools/acceptance_tests.py` in one fresh Python
process per promotion, retaining the existing function/interface test inventories.
This shares DWARF/type caches only within that run; it does not reuse a previous
pass. The receipt in `build/acceptance/tests/<group>.json` records module identities,
counts, skips, failures and elapsed time. Failed/empty imports, incomplete test
execution or changed selected test files reject acceptance. A prior receipt is
removed before preflight so an interrupted/failed run cannot leave stale success.
Fresh compilation, scope checks, link checks and global audit remain separate.


Interface admission rebuilds declarations and historical signatures from verified
CU receipts and locked DWARF; generated conflict cards are navigation data, not
authority for source edits. Before application and verification, the interface
plan must regenerate identically using saved baseline source whose bytes match
the ledger receipts. Changing a saved prototype, source snapshot or edit plan
cannot redefine the task. Unknown mechanical task kinds are rejected.


Codegen rules in a card distinguish CURRENT_SYMPTOM_EVIDENCE from
HISTORICAL_EXAMPLE_ONLY. Current hints require observed function features or
diagnostics and a matching recorded compiler scope. Only current hints affect
queue priority. Neither label proves a source cause, permits a body edit, or
changes acceptance; follow the task scope and verifier evidence.


Batch stage logs and summaries live beside the event history under
`docs/attempts/<mechanical|pattern>-runs/<run-id>/`. The event `log` paths
point to complete stdout, stderr and return codes, including rejected attempts.
They survive build cleanup; commit this run directory with its history and the
accepted source/proof changes. For older build-only runs, preserve available
outputs with an archive manifest instead of rewriting the historical events.


For stack-frame differences, `frame_layout.local_inventory` distinguishes unique
name pairs, original-only and candidate-only debug declarations, and ambiguous
shadowed names. FAST prints counts; the compact card prioritizes exceptions and
links full details. A missing debug declaration does not prove missing source,
and type sizes are not a stack-allocation total. Use the recorded locations and
separate width evidence before proposing a bounded change.


Compact cards show at most eight grouped calls and globals nearest the first
mismatch. `evidence_counts` records raw references, total groups and omitted
groups. Unknown positions sort last. Use `detailed_evidence` for complete lists
before making changes involving a dependency outside the displayed window.


Body-task queue rows include `routing_reason`. Cards add `routing_evidence`
with observed sizes, mismatch/call counts and the base eligibility checks. These
explain selection; they do not authorize overriding final difficulty. Bounded
recipes, interface/owner prerequisites and recorded supervisor blocks take
precedence. The actual recorded block reason is retained in the queue.


A canonical-type card may be `WAITING_FOR_CANONICAL_DEPENDENCY`: its generated
header includes another type still declared locally in an affected CU. Complete
the linked prerequisite task first. Queue refresh removes the dependency once
its duplicate declaration is gone; do not try the parent early or merge typedefs
manually. Transitive dependencies are included.


Compiler trial summaries include `diagnostic_original_comparison`. Even when a
trial reports FUNCTION_MATCH, `acceptance_input` is false: scratch compiler flags
and objects cannot promote production source. Production status comes from the
locked normal build. Use trial results to guide a supervisor investigation.


Compiler probes retain numbered RTL pass identities, including repeated names
such as dce. Trial memory links a compact `*-rtl.json` comparison with at most
three changed-pass excerpts. Only exact scratch paths and compiler heap
declaration addresses are normalized. Alias sets, register IDs, labels and
source lines remain visible. First textual divergence is not necessarily the
pass causing the machine-code mismatch; missing passes are explicit.


Trial memory keeps the newest result for each experiment name across current and
archived probe records. Each displayed trial has its own `baseline_state` and
evidence path; archived rows include the JSONL line number. The top-level state
only describes the latest probe. At most three distinct trials are shown, with
omission counts and an archive link for the rest. Do not treat archived no-change
results as proof about a changed source/toolchain baseline.


`ownership_prerequisites` lists independently unresolved data/literal relocations
that a body task cannot currently close. These tasks route to SUPERVISOR even
when the instruction mismatch is small. Resolve the owner evidence first. An
existing generated literal/symbolic recipe may cover its own operand; unrelated
missing bindings still block. Missing ownership is not proof of a correct body
or a layout-only state.


`callee_interface_scope` assesses known direct-callee interface conflicts in the
caller CU. A resolved call address does not establish that its return/parameter
types are historical. Blocking entries link to interface cards and show local
declarations and layout issues. Complete that prerequisite before body grinding.
Remote-only conflicts do not block a locally proven interface, and unknown
indirect targets are not guessed. Compact cards show up to eight observations;
complete target evidence retains all of them.

Queue rows include direct interface prerequisites and the bodies depending on a
repair. CHEAP repairs planned in the affected caller CU receive a capped priority
bonus. This does not lower body difficulty or promise that the repair removes all
blockers. Follow the refreshed queue after promotion. The complete edge list is
in `docs/current/task-dependencies.json`; bounded queue entries record omitted
counts. Remote-only conflicts and protected bodies do not create these edges.

TYPE_VIEW cards record `view_completeness`. A `COMPLETE_LAYOUT` view has exactly the
historical shape (size, member names, offsets, types), so the generated alias is a pure
renaming and by-value locals, struct copies, array members and sizeof uses are admitted.
A `PARTIAL_LAYOUT` view removes filler and keeps the pointer-only restriction. Pointer
members spelled through a proven explicit compiled alias (`alias_normalized_members`) compare
as their canonical pointee. Same-name declarations defer to CANONICAL_TYPE only when their
member tokens equal the generated header. A required canonical dependency that is only
forward-declared locally (`typedef struct T T;`) blocks the view unless the owning CU's own
historical DWARF defines T completely; then `forward_declaration_repairs` adds one generated
include edit. Vendored upstream CUs are never canonicalization targets. None of this bypasses
the unchanged-emission or complete-layout acceptance checks.

A TYPE_VIEW card with `repair_mode: POINTER_MEMBER_ONLY` preserves the local struct
and repairs the DWARF-evidenced `void *` members in place. Each repair records its
`pointee_evidence`: a generated historical header for a game type, or the owning CU's own
historical library typedef layout (for example FONT, BITMAP, DATAFILE) that the compiled
CU reproduces exactly. The debug-retention probe now also requests those member pointee
names so an unused library type has layout evidence. Use its generated commands; success
is `DWARF_MEMBER_MATCH`, not whole-struct canonicalization or a function match.
The same unchanged-emission and complete-layout acceptance checks apply.

Typed caller repairs additionally cover a `void *` return placeholder becoming the
historical single game pointer, multi-level pointer placeholders (`void **` to `T **`),
and an implicit call whose historical return is void or a game pointer when every
spelled call discards its value. Definitions, named non-placeholder types and used
implicit results still route to the supervisor.

For supervisor investigation of an interface/branch interaction, use e.g.
`python tools/compound_probe.py game-fld-adspot fldads_threadmain --interface log2file --invert-if shouldDownloadAds`.
This runs only isolated diagnostic variants. Read the card's `compound_trials`
first to avoid repeating a current negative experiment. Its results never bypass
body/interface admission or qualify as promotion input.

Ordinary link acceptance automatically reuses verified unchanged objects. Fresh
preprocessing checks include resolution and dependency contents before reuse, and
inputs are checked again after linking. This does not cache the owning-CU FAST or
strict function comparison. Link reports expose COMPILED/REUSED per object; neither
state establishes historical function equality.

For supervisor interventions, read docs/current/supervisor-queue.json. It ranks
shared recorded interface prerequisites by distinct affected callers, then groups
remaining observations by CU and mismatch class. Counts are not promises of
unlocked tasks. Read the repair card and retained evidence before experimenting;
encode the validated lesson, refresh the queue, and return to CHEAP work. The
layout-protected count is reported separately and does not authorize body edits.

POINTEE_TYPE tasks permit only their generated declaration and compiler-typed
member-token edits. Use interface_task.py's listed commands; do not rename member
names globally. Promotion verifies the complete parent and pointee types and
retains all existing contribution and exact-function gates. CANONICAL_POINTEE_MATCH
is a type migration result, not FUNCTION_MATCH.

A supervisor may investigate a context-dependent canonical/type-view block with
`python tools/type_context_probe.py <target> <task>`. After surrounding declarations
change, `python tools/reconsider_type.py <task>` fresh-probes every affected CU and
requires raw contribution preservation before atomically reopening the task. It
retains the old failure and does not promote anything. Resume the ordinary worker
only after the task is CHEAP again; do not manually erase blocker records.


## Historical emission order

Function cards carry `emission_order`: the function's historical and candidate
predecessors in emission order, whether every earlier historical function already
matches in order (`frontier`), and a bounded priority adjustment. GCC 4.4.1 carries
register-choice state between consecutively compiled functions, so a mismatch whose
predecessor differs from history may be a neighbor artifact and receives a penalty; a
frontier function receives a bonus. Neither value proves or masks any byte.

`python tools/emission_order.py <target> <source>` compiles one isolated variant per
out-of-order definition, moving it after its historical predecessor, and retains the
outcomes in `docs/attempts/order-moves/<target>.json`. `move_<stem>_<function>` SOURCE_ORDER
tasks are generated only for moves whose retained trial gained exact functions with no
regression, and only while the source and compiled object identities still match the
trial. Every promotion invalidates the remaining trials; rerun the probe to regenerate
them. The whole-file historical reorder stays a supervisor task while neighbors differ,
because each function's bytes depend on the functions compiled before it.


## Read-only literal pools

`python tools/pool_literals.py <target>...` is a supervisor diagnosis. Uniquely located
candidate literals give the pool base for the run around them; a candidate string whose
historical counterpart at that address differs is proposed as a repair only when the
following literals re-synchronize under the implied length delta (or the next unique
anchor confirms it), the historical text starts at a literal boundary and the texts are
similar. Proposals with a unique source token are applied by the supervisor and checked by
fresh 25-CU verification; a literal inside an exact body is not edited through this path.
Evidence is retained under `docs/attempts/pool-literals/`. The verifier also resolves a
non-unique literal between two agreeing unique anchors when its bytes recur at the derived
address (`read-only pool run` resolution); this never consults the tested operand.

An INTERFACE repair whose historical signature is unique may change emitted code in
functions that are not exact, but only toward history: each changed function must reach
its historical size, move closer to it, or differ in fewer bytes at equal size; non-code
sections, non-text relocations, symbols outside .text, common allocations and proven data
owners must be unchanged, and exact functions remain protected by the regression check.
The receipt records `emission_changes` with state HISTORICAL_DECLARATION_EMISSION_CHANGED.
Type and view tasks keep the strict unchanged-emission gate. The preservation projection
now canonicalizes any dependency-respecting reordering of straight-line register,
immediate and EBP/ESP-slot moves (including lea) and operand-swapped compare/jump pairs.
