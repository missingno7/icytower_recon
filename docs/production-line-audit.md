# Production-line audit

This work improves bounded recovery infrastructure; it does not change the
historical reconstruction oracle or consume the remaining function queue.

## Findings and implemented controls

| Observed problem | Concrete evidence | Control |
| --- | --- | --- |
| Only Tplayer emitted, with members hardcoded in Python | old `tools/generate_types.py` | Generic type graph, structural canonicalization, 35 generated game typedefs, size and every member-offset assertion |
| Field corrections repeated | commits `d0c314b`, `8352202`, `4b1b6c1` | Header generation from member/type DIEs; conflicting definitions fail; Tprofile layout is 1360 bytes |
| Exact claims corrected more than once | `8b34088`, `4bcb2ae`, `6dfcf2e` | Fresh promotion gate, receipt-bound statuses, source/tool identities, protected-neighbor checks, negative tests |
| Layout labels manually revised | `956b85c`, `021a1a3`, `da45b5b`, `189d67f` | Persistent mechanical workflow state distinct from conservative mismatch hypotheses |
| Small size deltas called padding without proof | old classifier used absolute size delta <=4 | Removed; no padding claim from size alone |
| Operand bytes could be scanned as call opcodes | original raw E8/E9 scan in `experiment.py` | Identified objdump instruction boundaries and verified target identity |
| Object ownership silently skipped names whose scope differed | `localFilename` was file-static in source, function-static in original DWARF | Complete storage census; declaration-only scope task accepted with identical emitted contributions and fresh ownership, yielding strict `FUNCTION_MATCH` |
| Instruction permutations appeared as register selection or unknown | `line_alert`, `create_profile`, checksum loop | Bounded decoded permutation windows and candidate source-line mapping; guarded source experiments; no equality after permutation in acceptance |
| Mechanical tasks required repeated model command orchestration | Separate begin/apply/check/promote steps for every generated declaration task | Bounded sequential worker delegates to existing gates, preserves failures and stops on acceptance/infrastructure faults |
| Whole-source signedness regex reused for every function | old `audit_signedness.py` | DWARF parameter/local encodings, function body casts/shifts, aligned original/candidate instruction pairs; counts remain hypotheses |
| All maintained headers invalidated every CU | old `compile_target` rglob | GCC depfile closure, pre/post compile fingerprints, included maintained/upstream files only |
| Source identity encoded partial status | SOURCE_ALIASES and game-main-partial | Canonical src/main.c and game-main throughout active tooling; historical reports remain unchanged |
| Stale tests trusted old function counts | map expected 3 matches and 592-byte add_floor; callback assumed exact | Fresh fixtures, current concrete expectations; static negative controls retained |
| Old synthetic custom audio cluster no longer closes | expanded main CU collides with probe and references many game CUs | Custom integration uses ordinary 25-CU recovered-game topology; no fallback added |
| Stored library plan did not match cached archive | Allegro plan now enumerates 116 CUs | Fresh archive rebuild and identity checks |
| Expensive rediscovery and oversized context | repeated scroller operand-order trials; profile induction and branch probes in experiment notes | Focused cards, rules with evidence/confidence, generated queue, source-scope enforcement, retained failed candidates |

All 25 original source identities are retained. No unknown source implementation
was invented. No original executable bytes are fed to compilation. Original data
bytes shown in cards are verifier evidence only.

## Proof and classification boundaries

Raw function proof statuses remain FUNCTION_MATCH / CODEGEN_SIMILAR / DIFFER /
MISSING for compatibility. The ledger additionally persists `workflow` and fine
difference dimensions. Body layout proof requires exact resolved bytes and
independently verified decoded same-CU transfers. Unknown section ownership is
always a supervisor issue, even when masked instruction bytes agree.

Difference classes are conservative diagnostics, not semantic equivalence claims.
A current card records classification confidence, first mismatch and raw evidence.
Instruction-count differences alone never assert a variable's signedness caused a
mismatch. The graph supplies the variable encoding and location evidence separately.

The atomic publication gate locks readers, tests prospective evidence, snapshots
authoritative files, replaces the ledger, regenerates current documents and audits.
An exception restores every previous authoritative byte before releasing the lock.
A flushed journal also survives process termination. `recover_promotion.py`
refuses a live owner, validates the complete journal scope, and restores the previous
publication before releasing the stale lock. This is serialized publication with
rollback, not a security boundary against rewriting both verifier and receipts.

## Deliberate limits

- There are substantially fewer immediately CHEAP tasks than unresolved functions.
  Large control-flow mismatches and ambiguous static ownership are not relabeled
  cheap to inflate readiness. The supervisor loop still needs to lower those costs.
- Generated shared Tplayer, Tfloor, Tmap, Tcontrol, Tgamepad and Tscroller definitions
  are consumed by maintained headers. Overlapping profile views remain visible as
  interface conflicts until a scoped migration can preserve historical codegen.
- Candidate declaration comparison is deliberately conservative about typedef
  spelling; it reports all maintained compiler declarations rather than guessing
  compatibility between overlapping partial views.
- No layout-only proof is granted for unresolved anonymous literals, static data
  or BSS owners. Their ownership cards distinguish missing evidence from body work.
- FAST builds only one CU. ACCEPTANCE rejects exact-neighbor regression and checks
  global receipts. Mechanical declaration tasks compile their actual dependency
  closure; other header/data changes still require supervisor review.
- Runtime replay is not used as an acceptance oracle. Whole object, debug/CU,
  resource and executable reconstruction remain separate work.

Pre-existing dirty experiment reports and `docs/blockers.json` were preserved.
New failed experiments are retained under `docs/attempts/`; old research and
experiment prose remain historical evidence, not current instructions.


## Real workflow validation

`docs/current/validation.json` records FAST results for draw_scroller, add_floor,
create_profile and play_jump_sound, rejection of a body-edit task on the proven
layout-blocked play_jump_sound, rejection of a false draw_scroller promotion,
getFloorData exact re-certification and explicit play_jump_sound layout promotion.
All 35 generated headers compile together with the historical compiler.

The focused negative controls cover false claims, scope escapes, dependency
freshness, unsafe clear reorderings, compiler failures and killed publication.
The 26-test historical pipeline passed, including actual wrong-target and
initializer corruption controls for the named-object resolver.
The latter freshly compiles its test CUs and checks ordinary game linking without
opening verifier assets. The unresolved max_speed link frontier remains explicit.

An actual CHEAP task session tried three bounded calc_replay_checksum_131 variants.
None matched. The blocker tool retained the trials, restored the source's exact
original hash and excluded the task. Replaying the first failed body in a build-only
copy confirmed that its only mismatches moved from the backedge to offsets 134-138
in the peeled first iteration. That lesson is now in the codegen rule database.
This demonstrated safe failure handling; it did not recover another function.

Readiness remains incomplete: the remaining inexpensive queue is small. Larger
source tasks, uncertain literal/static ownership and conflicting partial type
views still need supervisor work before a cheap model can sustain a long run.


## Interface production line

Three real tasks passed separate INTERFACE_MATCH acceptance: HTTPFetchInternal
const parameters, create_post's void prototype, and new_rand's missing prototype.
They used generated declaration edits and affected-CU checks. No additional game
function byte recovery is claimed. create_post also preserved exact functions while
recording a decoded independent XOR-clear reorder in unresolved line_alert and
compiler-generated static UID suffix changes; all other code, data and allocation
contributions remained equal. A failed stricter trial remains in the attempt log.

After these examples, 22 mechanical interface tasks and two body tasks remain
CHEAP; 32 body tasks are MEDIUM. Unknown data ownership and harder source mismatches
remain supervisor work. This extends the useful cheap queue without pretending
that the majority of unresolved function bodies are already routine.

Proof identities are separate from diagnostic identities: changing rules/card
classification can reanalyze current immutable byte receipts without recompilation.
A verifier/toolchain/source/dependency change still requires fresh affected proofs.
Body sessions enforce three FAST attempts; compiler errors are retained and the
block/abort path restores original source bytes even when compilation fails.


## Object ownership and canonical types

Named objects can now supply independent relocation targets even when the entire
partial-CU data section has conflicting base candidates. Acceptance requires a
unique historical CU/scope/name, identical full DWARF type signature and size,
unambiguous COFF ownership, matching linkage/storage and complete initialized bytes
(or BSS zero initialization). Objects containing relocations and ambiguous lexical
block statics remain blocked. startGameMusic and datafile_callback_slow demonstrate
this recurring blocker being resolved without body edits. These are independently
resolved function proofs; section/object/CU equality is not inferred.

The canonical-type queue finds exact duplicate member-token declarations and
proposes replacing only those typedefs with generated headers. Differing member
types/order and separately used struct tags prevent automatic merging. The same
source-scope and emitted-contribution gate covers the affected CUs. Full ownership
evidence is available in docs/current/objects; function cards link complete
target-only evidence and summarize repeated references and nearest mismatches.

The README's old milestone counts and status prose were archived intact in
docs/history/readme-recovery-baseline.md so a grinder reaches generated live state
without reconciling an obsolete narrative.

## Compiler context, definition order and initialized data

Live DWARF location interpretation now associates variables with the actual nearby
register/stack operands, respecting half-open location ranges and lexical scope.
Unsupported expressions remain unknown. Signedness cards also compare uniquely
named builtin declarations in original and candidate DWARF; aliases and shadowed
locals are not mechanically equated. These are diagnostic associations, not proof
of a source cause or behavioral equivalence.

Isolated compiler probes showed that changing an earlier definition can change
HTTPFetchInternal or draw_scroller machine bytes without changing the target body.
GCC 4.4.1 retains scratch-register search state across successful peephole2 searches.
The last two apparently cheap body tasks are now supervisor work, with persisted
evidence and failed alternatives rather than more blind expression rewrites.
See [compiler-context evidence](compiler-context-evidence.md).

The SOURCE_ORDER production line restores unique original DWARF declaration order,
preserves every body, rejects newly implicit calls and protects exact functions/data.
The real scroller task recovered natural historical function offsets but left its
six register mismatches. No text/CU match is claimed. ARRAY_EXTENT tasks isolate
simple builtin-array bounds, retain all explicit initializers, and require original
type/initializer proof plus unchanged emitted contributions. rankFloors's 16-to-12
repair passed full acceptance. It corrects source evidence without claiming a new
function match.

Named object ownership can now resolve initializer relocations from independent
symbols, existing owners or unique literal content, then compare every initialized
byte. Unsupported, overlapping, boundary-crossing or unresolved relocations reject
the owner. A fixed point permits acyclic proven owner dependencies; no original
initializer pointer or tested instruction operand is supplied to the resolver.
Real mutation tests reject wrong addends, corrupt literals and unsupported types.
Canonical Tmenu passed the existing two-CU gate and exposed seven proven menu
objects; ctrl_menu, opt_menu and main_menu remain rejected for concrete data reasons.

Current inexpensive work comprises 41 declaration/type/order/array tasks. There
are 32 MEDIUM body tasks, and no open CHEAP body task after evidence-based routing
and the completed fadeIn example below.
This is a larger sustainable mechanical queue, not a claim that most remaining
body reconstruction is already routine. Current counts are generated in the queue.

## A complete bounded body task

The old indirect-call heuristic unnecessarily excluded fadeIn even though only
two conditional opcodes differed. A new diagnostic requires identical decoded
boundaries, equal branch targets, fully resolved relocations/transfers, unchanged
remaining bytes and nearby TEST/CMP flag producers. It exposed the signed positive
versus nonzero guard difference. The task opened through the normal CHEAP gate,
changed only the wait condition, passed FAST once, and preserved every exact neighbor
through acceptance. Its remaining same-CU displacement is BODY_MATCH_LAYOUT_BLOCKED.
No opcode is masked for matching. Promotion now requires an explicit layout claim
for this state instead of accepting a generic FUNCTION_MATCH claim.

BEGIN evidence is archived before each new body edit. The fadeIn pre-repair baseline
was separately extracted from the retained earlier Tmenu acceptance report; its
body hash was checked against that report. The record distinguishes historical
diagnostics from fresh proof and retains both guard instructions and source bodies.

The test suite no longer requires draw_scroller, add_floor or log2file to remain
unrecovered, and permits the max_speed link frontier to close. Existing exact
functions and wrong-code/target/padding rejection controls remain mandatory.
The timer O1 negative-control object is freshly compiled rather than borrowed
from an old cache. Historical integration-layout evidence is checked as an archive,
without requiring an ignored historical build artifact to exist in a new checkout.


## Typed initializer repairs and dependency routing

The pipeline now retains hash-bound candidate data snapshots and compact global
DWARF layouts. It reports differences as array/member paths, maps original pointer
values to unique DWARF/COFF symbols, and independently describes candidate relocation
targets. These are source diagnostics; original numeric pointer values are never
used as a relocation-resolution or matching shortcut.

DATA_POINTER tasks permit one explicit symbolic address replacement. They reject
ambiguous target paths, unsupported relocations and wider source edits. Acceptance
requires unchanged raw text and all other allocated data/layout/relocations plus
a fresh complete type/initializer ownership proof. The field exclusion is used
only for candidate-to-candidate edit preservation, never original matching.

The real ctrl_menu task replaced &rejump with &options.jump_hold. All 47 existing
main.c function proofs survived; ctrl_menu, opt_menu and main_menu now have complete
independent initializer proofs. The latter two already named the correct objects
and were classified WAITING_FOR_OWNER instead of receiving incorrect source edits.
The earlier failed-owner evidence and generated plan remain in the BEGIN attempt.
Eleven additional tests cover typed paths, ambiguous symbols, forbidden source
forms, field/relocation boundaries, corrupt snapshots and missing owner proof.

Workflow validation now accepts future recovery of its example functions instead
of requiring them to remain unresolved. Persistent negative controls still reject
false claims, wrong target addresses, changed initialized bytes and scope escapes.


## Compatible partial views and declaration layout checks

TYPE_VIEW derives intended canonical types from unique original/candidate named
pointer-variable correspondences. It checks every retained member offset, size,
type and qualifier, allows only unreferenced byte-array filler, refuses ambiguous
tags/by-value uses, and exposes unresolved member offsets without inventing names.
The generated edit replaces only the typedef with a canonical header and alias.
Fresh acceptance requires full canonical DWARF layout and unchanged body source and
allocated contributions. The existing narrow independent-clear projection remains
candidate preservation only; original function matching is unchanged.

Tprofile_extra and Tprofile_create completed this loop. The latter tests a full-size
view with sizeof uses. An actual attempt to begin the rank view was rejected without
changing source or ledger. Plans, failed compiles and acceptance records are retained
under docs/attempts/interfaces and docs/attempts/type-view-validation.jsonl.

The first extra-view compile revealed that every generated header imported Allegro
and stdio regardless of its fields. The aborted attempt retained the exact errors.
Header dependencies now follow named external DWARF declaration owners and generated
game-type dependencies. Unsupported owners are blocked. All 35 headers compile
together; isolated Tprofile also compiles beside partial library interfaces. A fresh
25-CU pass preserved every existing function proof after these shared header changes.

Explicit aliases normalize interface spelling only through compiled, included
canonical headers and complete equal layouts. Tags, callbacks and anonymous C type
syntax are not blindly rewritten. A real same-name counterexample then showed that
main.c and profile.c used incompatible Tprofile definitions even though both
create_profile declarations appeared to agree. Game aggregate layouts now participate
in conflict reporting: header signedness and missing/different members are explicit.
Missing layouts are separately unavailable. External library aggregate comparison
still relies on declaration spelling and locked header inputs; it is not represented
as universal full type identity proof.

Twenty added tests cover view compatibility, qualifiers, filler accesses, ambiguous
correspondences, explicit alias boundaries, same-name member conflicts, unavailable
layouts, header isolation and historical compilation. The production line still
needs broader preparation of unresolved function bodies; these changes reduce the
reasoning and hidden prerequisites around shared structures without relabeling hard
body work as cheap.


## Compiler-located local declarations and stack frames

The previous variable-type report did not distinguish parameters from locals or
point to the candidate compiler's declaration file/line. Candidate evidence now
retains those facts, byte sizes, function-scope ownership and constant values.
Local declaration cards correlate unique builtin names and preserve the exact
initializer and surrounding source. Parameters redirect to interface work; static
storage, protected bodies, ambiguous scopes, macros and inferred array bounds are
not eligible. Source arrays with inferred bounds may be missing initializer content,
so changing their declared size is explicitly refused.

LOCAL_DECLARATION acceptance proves the fresh original local type and either
preserves emitted contributions or requires the exact function oracle for changed
code, preserving non-code contributions and existing exact neighbors. It cannot
publish changed unresolved code as a declaration-only success. The real
main_menu_callback scroller_step repair passed with EMISSION_PRESERVED; its body
remains SOURCE_DIFFER with the same concrete first mismatch. The accepted source
and result are retained in docs/attempts/interfaces/decl_main_main_menu_callback_scroller_step.jsonl.

Eighteen first mismatches previously labeled register/instruction selection are
constant SUB ESP entry allocations. STACK_FRAME_LAYOUT now records that observation
separately. It includes independently observed local-width differences without
claiming they account for the full frame. No calls/branches or late adjustments are
crossed by the bounded entry scan. The known-rule database and FAST output direct
attention to local widths, spills and outgoing arguments before register guessing.
This classification never grants BODY_MATCH_LAYOUT_BLOCKED or masks stack bytes.

Nine local-declaration tests and five stack-diagnostic tests cover the new boundaries,
including rejecting emitted changes while the target remains DIFFER and requiring
the strict function oracle when changed code is accepted. The exact-code branch
uses the existing oracle; the live declaration example exercised preserved emission.

The mechanical worker accepted historical source-order tasks for game_data and hisc. Its fld_adspot trial was restored and blocked; a narrow terminal-JMP layout proof now distinguishes the wrapper from the still-unresolved CSV-reader literal. See [branch relaxation evidence](branch-relaxation-evidence.md).


Literal classification audit: aligned operand diagnostics exposed wrong filename,
file-mode and logging payloads previously grouped with relocation layout. Generated
repairs promoted add_profile, fldads_dump_local_cache and delete_profile. The new
pattern worker automatically restored and blocked check_characters after the
literal repair exposed a distinct named-global mismatch. No masked equality or
original operand value was admitted as an independent relocation proof.
Publication failure during this validation also exposed unnecessary writes of every
current document. Byte-identical outputs are now untouched; changed files and rollback
use atomic replacement. Failure-injection tests preserve old bytes on write/replace
errors. See literal-content-evidence.md and docs/attempts/pattern-runs/.

Global-reference audit: check_characters has a wrong scalar reference plus a missing aggregate declaration, not merely literal placement. Generated diagnostics now separate supported whole-skeleton reference conflicts from four weaker aligned observations. The isolated 4-to-1,036-byte play_char type probe preserved existing exact functions and exposed only the known line_alert clear-order effect. That isolated probe was followed by the implemented GLOBAL_TYPE gate: the migration passed strict acceptance, the generated line_alert repair then reached exact match, and check_characters reached BODY_MATCH_LAYOUT_BLOCKED through the guarded assignment/literal recipe. The seven remaining same-CU transfer operands remain explicit layout work.


## Unattended interface batch and source-status cleanup

The mechanical worker completed three consecutive generated interface tasks for
`fldads_get_local_cache_name`, `fldads_get_local_filename_from_url` and
`fldads_update_local_adimg`. Each passed its fresh FAST and ACCEPTANCE gates;
the stage logs are indexed by
`docs/attempts/mechanical-runs/20260920T232314104868Z.jsonl`. These are declaration
repairs, not three newly recovered function bodies.

Reconstruction banners in profile, replay, hisc, menu and strptime retained stale
per-function recovery claims. They now retain historical inventory evidence and
point to the canonical ledger/current cards. Source line counts and executable
source were preserved. Fresh locked compilation of every configured CU passed
non-regression checks; the five changed files also preserved every non-debug
section byte, symbol/relocation contribution and function byte/status. The
comparison results are in `docs/attempts/source-banner-cleanup.json`.


## Unused interface type evidence

Historical GCC omits unused typedef layouts from ordinary optimized DWARF. This
created repeated supervisor tasks for declarations in control.h included by hisc,
menu and replay. A separate owning-CU build with
`-fno-eliminate-unused-debug-types` now supplements only missing interface typedefs.
Its dependency/configuration/toolchain identities and raw non-debug section, symbol
and relocation fingerprints must equal the primary build. Existing primary types
are never replaced; ambiguous supplemental types remain ambiguous. Probe function
bytes, locations and globals do not enter the historical acceptance oracle.

Fresh verification recovered Tcontrol/Tgamepad evidence in hisc, Tgamepad and
Tmenu_char_selection in menu, and Tgamepad in replay. Seven previously incomplete
interfaces now agree without source changes; real void/unknown declarations and
layout conflicts remain blocked. All function statuses and workflows are unchanged.
The full 249-test suite passed, including probe input/flag/code/symbol/relocation
rejection, serialization and primary-type precedence. See
`docs/attempts/interface-type-probe-validation.json`.


## Typed caller declaration prerequisites

The interface planner previously treated void-pointer and implicit caller
declarations as missing type evidence, then required that evidence before allowing
the declaration repair that would introduce it. A bounded typed-caller recipe now
uses the unique historical signature and generated header for single aggregate
pointers. It refuses definition edits, return changes, variadic/nondefault ABIs,
shared declarations, incompatible existing types and unsupported pointer forms.
Acceptance additionally requires complete historical layout agreement in every
maintained declaration, plus existing scope and whole-CU preservation checks.

The real init_control placeholder and is_any implicit call passed FAST and strict
promotion with no body or emitted-contribution changes. The first is_any trial
exposed a prototype-before-header ordering bug; that compile failure was archived,
the original source restored, and a regression test added before the successful
retry. Three further typed caller tasks remain generated and CHEAP at this
checkpoint. The full 257-test suite passed. Evidence and task links are in
`docs/attempts/typed-caller-validation.json`; complete attempts are in
`docs/attempts/interfaces/`.


## Shifted instruction sequences

Fixed-offset byte differences amplified small instruction-length changes. Cards
and FAST now include bounded heuristic instruction-sequence groups, with separate
original/candidate offsets. Keys preserve registers and ordinary immediates;
candidate relocated fields use independent resolved values, external transfers
use independent targets, and internal branches use decoded instruction indices.
Unresolved fields do not align with original bytes. Complete decode and size
limits bound cost; output is capped at three groups and four instructions per
side. Nothing in this diagnostic feeds status, routing or promotion.

Real change_profile output reduces 171 byte offsets to six sequence groups;
stopGameMusic reduces 16 offsets to two groups. create_profile and add_floor also
retain focused examples. The generated queue, all function statuses and workflows
remain identical. Sixty diagnostic tests, fresh rejecting FAST and global audit
passed. See `docs/attempts/instruction-alignment-validation.json`.


## Compiler-context extent and negative-trial memory

The context probe previously compared only equal-length resolved byte streams. A
peer-only change to the target function extent could disappear from dependency
routing. The shared comparison now records size deltas independently of byte
availability, counts inserted/deleted bytes when comparable, and caps displayed
offsets. Extent-only observations retain an explicit limit: they do not determine
whether source, padding or branch layout caused the change. Unresolved baseline
bytes cannot confirm freshness through a None-equals-None comparison.

Cards and FAST also expose up to three recent compiler trials, including negative
results and baseline freshness. An isolated change_profile experiment omitted
stopGameMusic only in a scratch source copy. It retained the 196-byte target and
all resolved bytes; the negative result is visible without reading the full
source snapshot/RTL report. It does not justify a new source repair rule or a
context-dependency claim for change_profile. Maintained source was unchanged.
Ten context tests and 53 related diagnostic tests passed. Full experiment receipts
are in `docs/attempts/compiler-context/game-main/change_profile.json`.


## Acceptance test process overhead

Function promotion previously launched 11 test processes and interface promotion
launched 21, repeatedly parsing the same DWARF/type graph. Each group now runs in
one fresh interpreter with exactly its prior module inventory. No pass is cached
across promotions. The runner rejects empty modules, load failures, incomplete
execution and selected test-file changes; it clears stale success receipts before
preflight and buffers output from successful test fixtures. Compilation, strict
comparison, scope enforcement, link regression checks and global audit remain
separate and unchanged.

The 196 interface tests took 16.3 seconds separately and approximately 5 seconds
batched in a local comparison. The 109 function tests also passed, plus five runner
negative controls. Real getFloorData re-certification and is_down declaration
acceptance passed through the new runner and full promotion gates. Detailed module
counts, identities, timings and attempt links are in
`docs/attempts/acceptance-test-batching.json`.


## Interface admission authority

Interface admission previously read historical signatures and compiler declaration
locations from a generated conflict cache. It now recollects them from locked DWARF
and verified CU receipts. Interface plans regenerate before application and
verification against saved baseline text bound to receipt hashes; changing session
metadata cannot redefine the historical interface or permitted edits. Saved source
text for every mechanical task is checked against baseline receipt identities, and
unknown task kinds are rejected.

Controlled live edits changed is_fire to a forged void-pointer signature in the
cache and then in the session plan. Admission ignored the cache and retained the
historical Tcontrol pointer; applying the altered plan failed before changing
source. Cache and session were restored byte-for-byte, then the legitimate repair
passed FAST and full promotion with preserved contributions. The expanded focused
suite passed 201 tests, including five admission controls; the global audit passed.
See `docs/attempts/interface-admission-validation.json`.


## Evidence-filtered compiler guidance

Broad difference classes previously attached unrelated compiler advice and gave
a queue bonus even for historical examples. Rules now require explicit observed
features or diagnostics and recorded compiler/flag scope. Historical examples
remain labelled context without a priority bonus. No rule changes proof, task
difficulty or body-edit permission. stopGameMusic loses six unsupported hints;
add_floor and change_profile retain only relevant current symptoms, with past
examples distinguished. Seven selector controls and 53 related diagnostic tests
passed. See `docs/attempts/codegen-guidance-validation.json`.


## Durable unattended-run diagnostics

The mechanical and pattern workers previously retained event histories under
`docs/attempts` but wrote their complete stage output and summary under ignored
`build/`. Build cleanup could therefore remove the exact failure evidence a later
grinder needed. Both workers now write logs and summaries into a run directory
beside the durable history. Tests exercise success and rejected-stage output for
both workers, remove the build tree, and verify full diagnostics and outcomes.
The existing failure-routing and scope gates are unchanged.

A real unattended three-task batch promoted get_url_filename, HTTPRequest and
SplitURL through the strict interface gate without intervention. Its pre-fix
outputs were archived byte-for-byte with an explicit manifest, preserving the
original event history. Each promotion passed 201 interface tests and global
audit; this is interface recovery, not a new function-byte match claim.

A fourth real task, check_dir, promoted using the new durable log path. All 16
worker tests passed. See `docs/attempts/durable-worker-validation.json`.


## Frame-local evidence coverage

Stack diagnostics previously compared only names present uniquely on both sides,
hiding unmatched and shadowed declarations. The new inventory retains original
and candidate types, sizes, scopes and locations without guessing correspondence
for duplicate names. Compact cards show eight prioritized rows and omission counts;
full function evidence retains every row. FAST prints the four inventory counts.

Real validation covers draw_frame (22 historical-only declarations), get_string,
view_profile, replay_selector (shadowed p), and fldads_threadmain (all three locals
paired despite different frame sizes). These observations do not establish source
omissions or stack occupancy. Eight stack/compaction controls and global audit
passed; live FAST retains the expected unresolved result. The entire queue and
ledger function states remain unchanged. See
`docs/attempts/frame-local-inventory-validation.json`.


## Bounded reference context

Grouped calls and globals were still unbounded in compact function cards:
init_game displayed 71 call groups and 160 global groups. Cards now show the
eight nearest groups per list, retain aggregate reference counts, and report
total/omitted groups. Unknown positions sort last. Complete target evidence is
unchanged and remains linked. This reduces serialized init_game context from
119,657 to 50,894 characters while retaining every local and proof field.

Tests cover nearest-group ordering, repeated references, unknown positions,
omission counts and input preservation. All 24 grinder tests and 205 interface
acceptance tests passed. Queue content and function states are unchanged. See
`docs/attempts/card-reference-bounds-validation.json`.


## Explainable body-task routing

Body queue rows previously omitted routing explanations, and base heuristic
cards used a generic sentence. They now list the failed base eligibility checks
and expose the observed size/mismatch/dependency facts. Explicit supervisor
blocks retain their recorded reason. Existing bounded-recipe and prerequisite
overrides remain authoritative; this change does not loosen task admission.

Validation compared the entire before/after queue: every decision, priority and
position is unchanged. Every body-task reason agrees with its card, and every
recorded supervisor reason is preserved. All 24 grinder tests passed. Examples
are recorded in `docs/attempts/routing-explanations-validation.json`.


## GCC depfile quoting

A locked-GCC probe exposed a dependency parser gap: GCC writes a literal dollar
in a path as two dollars for Make. The parser now decodes this quoting before
resolving and fingerprinting dependencies. The regression test invokes the actual
TDM-2 compiler on headers containing single/double dollars, spaces and hash
characters and checks the exact returned paths. Existing included-header
invalidation and unrelated-header preservation controls remain in place.


## Canonical type dependency ordering

A real scratch compile demonstrated that replacing Tstar_field before the local
Tstar typedef causes conflicting declarations: the generated parent header
includes the canonical child header. Both tasks had previously been CHEAP.
Canonicalization now follows transitive generated-header includes and waits for
remaining duplicate-type tasks sharing an affected CU. Disjoint CU declarations
do not create prerequisites, and refresh automatically releases a parent after
its child replacement. Two regression tests cover these cases. The complete
compiler diagnostic is in `docs/attempts/canonical-type-dependency-probe.json`.

Both real replacements passed strict promotion with preserved contributions and
function states. The final gate passed 208 interface tests and global audit. A
read-only replay of the original stars.h confirms that the new planner waits for
Tstar before offering Tstar_field. See
`docs/attempts/canonical-type-order-validation.json`.


## Integrated validation and whole-unit compiler lead

The complete infrastructure suite at b842272 passed 295 tests, including real
compiler, upstream build and static link checks. The recorded readiness snapshot
still has 69 unresolved bodies (18 MEDIUM, 51 SUPERVISOR), separate from 25 CHEAP
mechanical tasks and 20 protected layout tasks. This does not establish the full
handover objective. See `docs/attempts/integrated-production-line-validation.json`.

An isolated stopGameMusic probe compared three compiler switches. Disabling
scheduling made no change; disabling peephole2 reduced the mismatch; disabling
whole-unit compilation produced FUNCTION_MATCH in the diagnostic object. Normal
production source/flags remain unchanged and the ledger still reports DIFFER.
Trial cards now expose original comparison verdicts and mismatch counts, marked
`acceptance_input: false`. Eleven compiler-context tests passed, including a
control proving that an exact flag trial does not become a peer-layout dependency
or acceptance input. Full evidence is retained in
`docs/attempts/compiler-context/game-main/stopGameMusic.json`.

The whole-unit-disabled diagnostic also reduces the CU function-match count
from 50 to 42. Its target match is therefore not a viable global flag fix.
The peephole-disabled trial reduces that count to 27; scheduling-disabled stays
at 50. These counts are retained in the full probe evidence.


## Numbered compiler-pass evidence

Compiler probe indexes used phase names as keys, so the later dce dump silently
replaced the earlier dce entry. They now retain numbered pass records with file
identities, clear stale raw dumps before compilation, and preserve repeated
phase names. Bounded comparisons verify dump identities, report missing passes,
and normalize only exact scratch paths and compiler heap declaration addresses.
They never supply function proof or assign a causal compiler pass.

A real stopGameMusic rerun retained 55 passes per variant, including dce 158 and
186. The 4.8 KB compact trace reports five equal and fifty textually changed
passes; the first is expand, including label/alias metadata changes. The target
diagnostic match reproduces with whole-unit compilation disabled, while the
production baseline remains DIFFER. Three trace tests and eleven compiler-context
tests passed. The initial probe rejected the hyphenated init-regs name; support
and a regression case were added before the successful rerun. Trial cards link
`docs/attempts/compiler-context/game-main/stopGameMusic-rtl.json`.


## Trial memory across follow-up probes

A narrower follow-up probe hid earlier negative experiments because cards read
only the latest record. Trial memory now walks current and archived records in
newest-first order and retains the latest result for each experiment name. Each
trial has independent baseline freshness and an exact archive line reference.
The three-row display limit has an explicit omission count. FAST prints each
trial freshness label rather than implying that the top-level state covers all
rows. No routing or proof decision depends on these summaries.

The real stopGameMusic card again shows the prior scheduling/peephole experiments
alongside the fresh whole-unit experiment. Twelve context tests pass, including
newest-result selection, archived negative retention, stale baseline labels and
omission counts. Queue content is unchanged. See
`docs/attempts/compiler-trial-history-validation.json`.


## Peer probes independent of source order

The old --omit-earlier restriction prevented refreshing draw_scroller evidence
after restoring the historical source definition order: restart_scroller is
now declared later. --omit-peer permits any other definition in the same scratch
CU; the old option remains an alias. Target omission and missing/ambiguous
definitions fail, and every generated variant preserves the target body hash.

The real later-peer probe changes four resolved draw_scroller bytes without
changing its body, renewing the compiler-context protection. Production source
and flags remain unchanged. Two separate stopGameMusic peer probes
(stopMenuMusic and play_sound) changed no target bytes and remain negative
trial memory. Thirteen compiler-context tests passed, including both declaration
orders and target-omission rejection.


## Data-owner prerequisites for generic body tasks

The base task heuristic checked unresolved calls but omitted unresolved data
relocations. This left log2file and four other functions ranked MEDIUM despite
unknown bindings that prevent strict body-only completion. Cards now expose
`ownership_prerequisites`; missing non-call resolved values route to SUPERVISOR.
Known generated source recipes retain the existing narrowly scoped operand
exception, but cannot cover unrelated bindings. Resolved zero values and known
but different references are not mislabeled as missing owners.

Real generation moves draw_reward, draw_progress_bar, log2file, jump_player and
get_replay_property from MEDIUM to SUPERVISOR. Ledger function and workflow proof
states are unchanged. The function acceptance suite passes 123 tests. Live
log2file admission is rejected even when MEDIUM work is explicitly requested,
before creating a session. See
`docs/attempts/ownership-prerequisite-validation.json`.


## Caller-local interface prerequisites

Body routing previously checked only the target function's own declarations.
add_floor therefore appeared ready for register-shape work while its called
get_demo declaration returned Tmap_replay instead of historical Treplay and
lacked complete candidate layout evidence. Direct calls now carry canonical
function names; known callee conflicts are assessed in the caller CU. Cards
show exact call offsets, local declarations, layout issues and interface links.
Resolved addresses do not bypass this check, while remote-only conflicts do not
block locally proven declarations. Unknown indirect callees are not inferred.

Four MEDIUM tasks now route to SUPERVISOR for local callee prerequisites:
add_floor, change_profile, fldads_threadmain and do_replay_menu. Function and
workflow proof states remain unchanged. Six interface-scope controls and the
129-test function acceptance suite pass. A real add_floor admission with MEDIUM
work enabled was rejected before session creation. See
`docs/attempts/callee-interface-validation.json`.


## Return-only partial type views

The supplemental debug probe previously requested only historical type names,
and ran before compiler interface declarations were loaded. It now also requests
missing typedef spellings from maintained compiled interfaces. These names select
probe evidence only; they do not establish type identity. Primary and ambiguous
layouts retain precedence, and raw non-debug emission must remain unchanged.

The type-view planner now associates explicit single-pointer returns with unique
historical function DIEs. Implicit declarations, ambiguous owners and incompatible
pointer forms are excluded. Existing field, filler, scope and acceptance checks
still apply. This generated the bounded view_map_Tmap_replay task automatically.
Its 148-byte partial view became an alias of generated Treplay, preserving both
used field offsets and all emitted contributions. Strict promotion passed 229
acceptance tests, the ordinary link check and global audit. Every function and
workflow proof remains unchanged. add_floor returns from SUPERVISOR to MEDIUM;
the separate main.c Treplay.data mismatch remains visible as a remote conflict.
See docs/attempts/return-view-validation.json and the archived task history.


## Queue prerequisite links and retained failure details

The queue now links editable unresolved bodies to their scoped, blocking own or
called-function interface tasks. Links use complete function evidence, not the
bounded card display. Protected bodies and remote-only conflicts create no edge.
CHEAP repairs receive four priority points per dependent body whose caller CU is
in the repair plan, capped at twenty. Difficulty and admission checks are unchanged;
a link never promises that all blockers will be cleared. The complete graph is in
docs/current/task-dependencies.json and bounded reverse links appear in the queue.

The first real ranked task, log2file, was rejected because its prototype repair
changed fldads_threadmain emission (204 to 223 bytes). The worker restored source
and routed it to SUPERVISOR, preserving all exact proofs. Detailed contribution
diagnostics now go to content-addressed docs/attempts/interface-diagnostics paths;
FAST and promotion histories link these durable files. A cleanup regression test
verifies both earlier and later diagnostic versions survive removal of build/.

The next ranked task, handle_player_collision_combo, passed the unattended worker
and strict promotion, including 234 interface acceptance tests, ordinary link
check and global audit. No function or workflow proof changed. Both runs and the
retained rejected-task diagnostic are indexed by
`docs/attempts/queue-dependency-validation.json`.


## Distinguish useful rejected edits from accepted recovery

Contribution diagnostics now retain original-oracle snapshots before and after
a mechanical edit: body shape, historical/candidate sizes, verdict/workflow,
first mismatch, bounded relocation details and complete mismatch counts.
The rejected log2file experiment is a concrete example: fldads_threadmain grows
from 204 to historical 223 bytes and matches body shape, while literal relocation
ownership still fails. This evidence directs the next investigation but cannot
bypass the unchanged emission gate or claim layout-only correctness.

New supervisor blocks retain summaries of the last failed attempt for the exact
source plan, stopping at the session BEGIN boundary. Only existing content-addressed
diagnostic files with verified filename hashes are included. A changed archive or
a different plan supplies no such evidence. The interface acceptance suite passes
240 tests, including archive tampering, session boundaries, unresolved relocations
and bounded-display controls. The saved candidate pair reproduces every field of
the original archived rejection before enrichment; see
`docs/attempts/interface-emission-diagnostic-validation.json`.


## Literal content versus resolved placement

Literal cards and FAST diagnostics now separate the existing independently resolved
section/object address from an independent search for the candidate payload in
historical read-only data. The search never consumes the tested original operand.
Unique disagreement, unique agreement, missing content, ambiguous duplicates and
empty non-identifying payloads are explicit. Search/display is bounded; truncated
occurrences carry a lower bound rather than a fabricated exact count.

This clarifies fldads_threadmain: several equal strings reside at different offsets
from the current section-based relocation targets. The verifier still keeps its
section binding; content matching cannot override it or promote a body. All function
and workflow proofs are unchanged. The 135-test function acceptance suite passes,
and real FAST prints the two currently aligned conflicts. The previously rejected
223-byte candidate has its remaining literal observations captured separately in
`docs/attempts/literal-placement-validation.json` as historical diagnostics.


## Type-view scope follows compilation dependencies

Partial-view planning no longer treats identical typedef spelling in an unrelated
CU as shared type identity. It inspects the owning CU's actual GCC depfile inputs,
including nested maintained headers, and still rejects included external uses,
unknown input text, incompatible members and non-pointer/size-dependent uses.
This replaces several false global-name blockers with the actual DWARF member
conflicts: HTTPResponse.iNumHeaders, Tprofile.header, Treplay.data and Tmenu_params.font.

The newly exposed main.c Tgame_data view cannot yet become a CHEAP task: generated
Tgame_data imports Treplay while main.c still defines an incompatible Treplay.
Canonical-header dependency traversal is shared with exact type canonicalization,
and partial-view cards now identify local child declarations before admitting the
parent repair. An isolated locked-compiler build reproduces the Treplay conflict;
real task admission refuses the parent without creating a session. The 245-test
interface suite passes and all recovery proofs remain unchanged. Evidence is in
`docs/attempts/type-view-scope-validation.json` and its linked compiler probe.


## Pointer placeholders without whole-struct replacement

The type-view planner now recognizes one unqualified four-byte void-pointer member
at its exact historical offset in an otherwise complete struct. A generated
canonical pointee is required. Typed-pointer substitutions, qualifiers, multiple
pointer levels, changed extents and incomplete layouts are excluded. The bounded
repair retains the local struct tag and every other source byte in the declaration,
imports the generated pointee, and changes only the member type. Fresh acceptance
requires the complete historical layout and unchanged emitted contributions.

The real Treplay.data case demonstrated why these are separate operations. Whole
Treplay replacement reordered two instructions in do_replay_menu and was rejected,
restored and archived for the supervisor. An isolated, baseline-checked member-only
trial preserved emission. The generated member_main_Treplay_data task then passed
FAST and strict promotion with 247 tests, ordinary link check and global audit.
No function or workflow proof changed. Removed caller-interface prerequisites,
both trials and the retained failure are indexed in
`docs/attempts/pointer-member-validation.json`.


## Complete pointee proof for member repairs

Member-only acceptance additionally checks the unique compiled pointee typedef
against its complete historical DWARF layout. Header inclusion and pointer spelling
alone are insufficient. Historical ambiguity, missing or duplicate candidate types,
member offset/signedness changes and an omitted generated-header scope all fail.
The accepted real Treplay.data repair passes the stricter check against its current
verified CU report. The interface suite passes 248 tests; function and workflow
proofs are unchanged. See `docs/attempts/member-pointee-validation.json`.


## Bounded compound experiments for prerequisite interactions

A supervisor can use compound_probe.py to test one existing compiler/DWARF
interface recipe together with inversion of one explicit scalar if/else in an
isolated CU copy. It compiles three fixed variants: unchanged baseline, interface
only and the combined edit. The scratch baseline must preserve raw non-debug
sections, symbols and relocations. Source, probe, verifier, fixture and locked
compiler inputs are checked; production files and the ledger are never edited.
Ambiguous conditions, unbraced alternatives, labels and preprocessor blocks are
excluded. Compile failures are retained and do not become comparison results.

The real fldads_threadmain/log2file trial disproved the simple coupled repair:
baseline is 204 bytes, the interface-only variant is 223 bytes with matching body
shape, and interface plus branch inversion returns to 204 bytes. All remain DIFFER.
The function card and FAST JSON retain a compact three-variant summary linked to
the full source-bound experiment, marking changed inputs as historical. This does
not alter admission, matching or literal-owner proof. All recovery proofs are
unchanged and the 138-test function suite passes. See
`docs/attempts/compound-probe-validation.json`.


## Call arity admission and unattended batch validation

Two real worker batches promoted six declaration repairs: collision old, original
and vector variants, open_web_browser, save_config and update_frame. The vector_2
repair changed emitted contributions; FAST rejected it, restored the source and
recorded a supervisor block. The first batch stopped safely when installing the
my_alert prototype exposed a seven-argument call against four historical parameters.

Mechanical interface planning now inspects source-spelled direct calls in affected
compiled CUs before admission. Incompatible argument counts become bounded
CALLSITE_REPAIR_REQUIRED supervisor cards, including caller, line, arguments and
historical count. The scan handles nested expressions and masked literals/comments;
it is deliberately not macro expansion or compiler type proof. It never authorizes
removing arguments. Real my_alert admission now fails before creating a session,
and the resumed worker skipped it and completed three further repairs.

The 252-test interface suite and global audit pass. All raw function and workflow
proof states are unchanged. Durable run histories, admission rejection and queue
counts are indexed in docs/attempts/call-arity-batch-validation.json. Full cheap-body
handover remains unfinished; ordinary link acceptance also still recompiles every
recovered CU after each promotion and needs verified reuse for unaffected objects.


## Verified ordinary-link object reuse

Ordinary recovered-game link acceptance now reuses objects only after fresh GCC
preprocessing confirms the resolved include closure, preprocessed contents, every
dependency identity, flags/configuration, compiler locks, build-tool identities and
environment digest. Object and build-report identities must also match. Locked
inputs are verified before and after the link; each object's inputs and bytes and
the library archive inputs are rechecked before publishing the link result. Failed
runs do not retain an old link.json as their result. This cache is confined to
ordinary linking: owning-CU FAST and strict function acceptance still compile fresh.

Real validation compiled all 26 objects cold in 10.690 seconds, then reused all
26 in 3.888 seconds. Tampering with the cached stars object rebuilt only that
object (4.114 seconds). A historical-compiler fixture detected both changed header
contents and a newly shadowing header with identical contents. All game links kept
the max_speed frontier and were never executed. The 255-test interface suite,
141-test function suite and global audit pass. Evidence is recorded in
docs/attempts/link-cache-validation.json. These timings are local observations,
not a universal performance guarantee.


## Five consecutive unattended promotions

The guarded worker completed for_each_directory, is_up, Tcommandline,
Tavailable_profile and Tcharacter consecutively without supervisor edits or
intervention. The first two repair historical declarations; the last three replace
exact duplicate structures with generated historical headers and layout assertions.
Every promotion passed its fresh owning-CU contribution comparison, acceptance
suite, ordinary link check and global audit. Existing raw function and workflow
proofs stayed unchanged, and the final promotion reused 25 ordinary-link objects
while rebuilding its changed CU. No task session remains open.

This demonstrates sustained mechanical interface/type work, not sustained cheap
function-body recovery. See docs/attempts/sustained-mechanical-validation.json and
the complete run logs it references. The full handover goal remains open.


## Recurring supervisor prerequisite ranking

The generated supervisor-queue.json groups complete direct caller prerequisites
by repair card, deduplicates callers, and reports whether the existing repair is
planned in each caller CU. CHEAP repairs remain in the grinder queue; protected
layout bodies are counted separately. Remaining non-cheap body observations are
grouped by CU and difference class, explicitly as symptoms rather than shared
causes. Five bounded examples link to original cards and the full dependency graph.
No admission or proof status changes.

Real evidence ranks load_replay first with five caller prerequisites, three within
the planned repair scope. Its replay.c return layout differs at Treplay.data
(Treplay_data pointer versus historical Trecord pointer), identifying a concrete
shared type-identity investigation. All 20 layout-protected bodies stay protected.
The 258-test interface suite, 144-test function suite and global audit pass; raw
function/workflow proofs are unchanged. See
docs/attempts/supervisor-queue-validation.json.


## Nested pointee correspondence in interface blockers

Aggregate interface conflicts now include bounded field correspondence for uniquely
compiled, simple named pointees against unambiguous historical game types. Matching
offsets and complete field shapes expose renamed fields; unmatched candidate
members remain explicit. Unknown extents, overlaps, bitfields, pointer qualifiers
and ambiguous types do not produce correspondence. This is diagnostic evidence,
not alias identity, layout acceptance or permission to remove filler.

The real load_replay card now shows Treplay_data.type at offset 0 corresponding
to Trecord.key_flags, value at offset 4 corresponding to cycle_count, and the
extra three-byte reserved field. The repair stays SUPERVISOR because typed
use-site migration and contribution preservation are not yet proven. This removes
the need to manually traverse child type DIEs when planning that shared repair.
The 261-test interface suite passes; function/workflow proofs stay unchanged.
See docs/attempts/pointee-correspondence-validation.json.


## Isolated typed pointee migration experiment

The supervisor command `python tools/pointee_probe.py game-replay Treplay data`
now generates a scratch-only recipe from unique compiled and historical types. It
requires complete field correspondence, unused byte filler, simple parent-pointer
index accesses, unique compiled function-scope roots, and no unsupported alias
uses. It replaces the typedef with a generated canonical header and explicit
legacy alias, updates the parent pointee and renames only the selected accesses.
The unchanged scratch baseline must preserve the raw non-debug fingerprint.
Inputs, compiler locks, tools and oracle identities are checked around the run.

The real Treplay_data migration changes no production source. Candidate comparison
shows no changed functions/sections or preservation metadata, but the raw
fingerprint correctly retains one generated local-symbol rename from
_C.146.9670 to _C.146.9673 at rdata offset 800. The existing preservation predicate
agrees; no new exception or function-match claim was introduced. The 147-test
function suite passes. Full source-bound evidence and edits are retained under
docs/attempts/pointee-probes, indexed by pointee-migration-validation.json.

The next step is bounded migration admission plus fresh compiled canonical type
verification through the existing atomic gate. This diagnostic probe is not that
gate and cannot promote a result.


## Atomic canonical pointee migration

POINTEE_TYPE tasks now turn the bounded scratch recipe into a generated mechanical
task. Admission and every scope check regenerate the plan from the verified
baseline receipt and saved original source. Exact and layout-protected function
bodies are excluded from token edits. Apply accepts only the complete generated
edit spans; arbitrary body work is prohibited. FAST and ACCEPTANCE require fresh
complete compiled parent/pointee layouts, exact generated header identities and
actual dependencies, existing no-regression guards and the unchanged full
contribution preservation predicate. The worker recognizes the task kind.

The real pointee_replay_Treplay_data task promoted through this gate after 12
planned edits, 265 interface tests, ordinary link verification and global audit.
It uses generated Trecord, keeps a legacy sizeof alias and changes typed member
accesses to key_flags/cycle_count. It removed 12 recorded caller-interface
prerequisites in replay.c. Every raw function and workflow proof state is unchanged.
CANONICAL_POINTEE_MATCH is a separate type-migration result, never a new function
match. The full attempt and resulting dependency changes are indexed in
docs/attempts/pointee-promotion-validation.json.


## Validated supervisor-to-worker handoff

After the shared replay pointee intervention, an unmodified mechanical worker
selected and promoted load_replay and save_replay interface qualifiers across
main.c and replay.c, then canonicalized Toptions. All three completed in one
unattended run through normal FAST/ACCEPTANCE, link and audit gates. This removed
seven additional direct caller prerequisites, with every raw function and workflow
proof unchanged. No session remains open. The replay-type lesson enabled routine
follow-up work rather than another per-caller type investigation. Complete evidence
is indexed in docs/attempts/pointee-handoff-validation.json. This does not complete
the outstanding cheap function-body handover requirement.


## Decoded branch destination context

Unresolved function cards now include the three direct branches nearest the first
mismatch on each side, with byte-decoded destinations, encoding lengths, conditions,
preceding instructions, fallthrough offsets and small target windows. Outside
function and non-instruction-boundary targets are explicit. Original and candidate
windows are independent: matching offsets do not establish corresponding blocks,
and no CFG-equivalence or source-cause proof is inferred. The existing strict
localized-guard recipe remains unchanged.

The real my_strcmp card exposes the differing first branch destinations without
requiring a whole-CU report. The 149-test function suite passes, including byte
decoding despite misleading assembly labels and invalid/external target handling.
All raw function and workflow proof states remain unchanged. Evidence is retained
in docs/attempts/branch-context-validation.json.


## Retained truth-test experiment

The reusable supervisor command `python tools/predicate_probe.py game-replay
my_strcmp "a->directory"` replaces exactly one simple unnegated scalar/member
condition with equality to one in an isolated CU. Ambiguous, negated or complex
expressions fail. An unchanged scratch baseline must preserve raw non-debug
contributions; the experiment retains complete source, compiler/input identities,
raw differences and original-oracle diagnostics. Production source is untouched.

The real equality-to-one trial changes emitted comparison code but remains DIFFER
at 123 versus 128 bytes, with the first mismatch still at offset 21. It therefore
does not solve the branch-layout problem. Function cards retain this negative
result and mark it historical after source/tool/compiler/oracle changes, avoiding
repeat rediscovery. No new recipe admission or exact claim was introduced. The
152-test function suite passes; all raw function/workflow proof states are unchanged.
Evidence: docs/attempts/predicate-probes/game-replay/my_strcmp.json.


## Guard-tail interaction trial

The predicate probe additionally accepts --invert-guard for one top-level braced
scalar equality guard with an unconditional terminal return. It moves the remaining
function tail into the negated branch and keeps the returning branch as else.
Nested guards, a final return controlled by an unbraced statement, fallthrough,
existing else branches, labels and preprocessing are rejected. This remains an
isolated supervisor experiment, not a semantics proof or grinder recipe.

On my_strcmp, guard inversion alone preserves the baseline raw contribution; the
equality-to-one plus inversion variant remains non-exact, like equality-to-one
alone. All four variants remain DIFFER. The function card retains all four with
source/tool freshness checks; older trials remain archived. The 154-test function
suite passes and all function/workflow proof states are unchanged. This rules out
the simple outer-guard inversion hypothesis without modifying production source.


## Interval-switch trial and bounded supervisor escalation

The predicate probe can test one guarded unsigned interval as a bounded switch
(maximum eight contiguous cases), alone and combined with equality to one. Only a
unique supported source form with a terminal unconditional return is accepted;
fallthrough, labels and break/continue/goto inside the arm are rejected. This is
a compiler experiment, not an equivalence proof (including signed-overflow edge
cases). It cannot edit production source or promote results.

For my_strcmp the switch alone preserves baseline emission; the combined variant
remains DIFFER at 123 versus 128 bytes with the first mismatch at offset 21. The
card now retains distinct archived guard trials as explicitly historical evidence
as well as the latest switch trials. After these bounded failures, the standard
grinder block command recorded BLOCKED_SUPERVISOR with the exact mismatch and
evidence links. Source was restored unchanged and the task session closed. The
155-test function suite passes. Future work must explain compiler/block ordering
before admitting another body recipe; cheap workers automatically skip this task.


## Pointee access root admission

The member-access recipe now rejects a root embedded in another member chain.
Previously the suffix r in holder.r->data[i].field could borrow the DWARF type of
a separate local r. The same ambiguity applies to holder->r, holder[0].r and
(*holder).r. All four are rejected before source edits. Standalone local roots
continue to require unique compiled function-scope type evidence.

All 268 interface tests pass. Replaying the archived real pre-migration replay
source and compiled type evidence yields exactly the prior 12-edit recipe; this
replay is diagnostic, not new acceptance proof. Evidence is indexed in
docs/attempts/pointee-root-scope-validation.json.


## Mixed canonical-type and profile-view batch

One unattended worker run promoted Tmenu_char_selection, Tmenu_floor_selection,
Tmenu_selection, Tprofile_basic and Tprofile_checksum. It rejected Tcustom,
Tprofile_advanced, Tprofile_control and Tprofile_load, archived focused contribution
differences, restored only the attempted source edits, recorded supervisor blocks
and continued automatically. Five promotions and four safe rejections completed
without manual source edits or intervention. Existing function/workflow proofs
are unchanged and the task session is closed.

Failed canonicalizations include same-size instruction permutations; no exception
to the preservation gate was introduced. Detailed changed-function evidence and
remaining queue availability are indexed in docs/attempts/type-batch-validation.json.
This validates sustained mechanical work across several task shapes but leaves
the cheap body-recovery requirement open.


## Source-context reconsideration of canonicalization blockers

The type_context_probe supervisor tool compiles four isolated variants: baseline,
baseline without assertion declarations, canonical recipe, and canonical recipe
without assertion declarations. It overlays only compiled maintained inputs and
generated headers; the unchanged overlay must preserve raw non-debug contributions.
Paired diagnostics distinguish canonicalization from assertion effects. Production
assertions are never disabled or proposed as an acceptance option.

Fresh current evidence showed the previously rejected advanced-profile recipe now
preserves all raw contributions after other profile migrations changed declaration
context. Tcustom also lost its old instruction permutation, but still differs in
the raw fingerprint; removing assertions changes another function and is not a fix.
The new reconsider_type command holds the publication lock, checks source/tool
snapshots, probes every affected CU, requires raw baseline/canonical equality, and
atomically retires a block only if ordinary planning then yields a CHEAP task.
The old block and content-identified probe paths are retained. No proof or source
status is promoted by reconsideration.

The worker then promoted view_profile_Tprofile_advanced through normal fresh type,
contribution, link, test and audit acceptance. Tcustom remains blocked. All 269
interface tests pass, including wrong/incomplete/duplicate/non-preserving probe
rejection. Every function/workflow proof is unchanged. See
docs/attempts/type-reconsideration-validation.json.


## Type-trial memory in task cards

Canonical-type and partial-view task cards now show bounded per-CU summaries of
their latest type-context experiments: raw and preservation verdicts, changed
functions, and full evidence links. Source/header, compiler configuration, oracle
and probe-tool identities determine whether a trial is current or historical.
The summary is presentation only, outside the edit plan and proof predicates.
Unplanned supervisor cards without affected targets receive no inferred trials.

Fresh reconsideration probes for Tprofile_control and Tprofile_general remain
non-preserving both with and without assertion declarations; their blocks remain
intact. Both cards now expose those current negative results, preventing repeated
blind retries. The 271-test interface suite passes and all function/workflow proof
states are unchanged. See docs/attempts/type-trial-card-validation.json.


## Complete type views and forward-declared dependencies

Five blocked type views were complete same-shape declarations rejected only because
their CU used them by value, in arrays or through sizeof. The planner now classifies
`COMPLETE_LAYOUT` versus `PARTIAL_LAYOUT`; a complete view is a renaming typedef and
admits those uses, while partial views keep the pointer-only rule. Pointer members are
compared through proven explicit compiled aliases, same-name declarations defer to the
canonical-type task only on exact member tokens, and identified vendored CUs keep their
upstream text. Seven tests cover the positive and negative boundaries.

Two unattended Sonnet-run batches then promoted FLDAdSpot, Tgd_combo, Tgd_jump_sequence,
Tgame_data, Thisc_post, Thisc_table, HTTPHeader, Toptions and the reset_hisc_table caller
declaration. The first batch stopped safely when the generated Tgame_data header
conflicted with a local `typedef struct Treplay Treplay;`; the abort restored source.
The planner now blocks such forward declarations unless the owning CU's historical DWARF
defines the type completely, in which case one generated include edit is planned; the
game_data CU's Treplay came from replay.h and the repaired task then promoted. The
HTTPResponse view in httpget changed extractHTTPResponse emission and was blocked with
retained evidence. Aggregate-layout interface blockers fell from 40 to 33; function
statuses are unchanged. Remaining hisc callers need return-type, definition, implicit-call
or double-pointer repairs outside the typed-caller recipe. See
docs/attempts/complete-view-validation.json.


## Caller placeholders and library-typed members

The typed caller recipe refused every return-type change and every non-single pointer.
Five hisc/control callers were therefore blocked by `void *` returns, `void **` parameters
and implicit calls whose historical return is void. The recipe now restores those forms
when the declaration is a CU-local placeholder and, for implicit calls, when every spelled
call discards its value; definitions and named types remain supervisor work. An unattended
batch promoted poll_control, make_hisc_table, view_scores and destroy_hisc_table.
get_controls was rejected: retyping the profile.c return permuted independent constant
stores in select_profile, the same effect recorded for the Tprofile_control view.

Same-name aggregate mismatches were dominated by `void *` members standing in for library
pointers. Member-only repairs now accept several placeholders and use the owning CU's own
historical library typedef layout, reproduced by the compiled CU, as pointee evidence; the
debug-retention probe requests those pointee names. The menu.c Tmenu_params repair
promoted through the unchanged gates. Function statuses are unchanged. See
docs/attempts/complete-view-validation.json for the run indexes.


## Independent-write projection, reopened blocks and link closure

Four blocked declaration tasks (get_controls, Tcustom, Tprofile_control, Tprofile_load)
shared one rejection shape: adjacent constant stores to distinct stack slots and constant
register loads emitted in a different order, with unchanged bodies and sizes. The
candidate-only preservation projection, which already canonicalized adjacent independent
register clears, now covers adjacent runs of immediate writes with pairwise disjoint
destinations (never ESP/EBP, entry targets or relocation fields). Reconsideration reopens
a block when the recipe variant satisfies that same acceptance predicate, and it now
covers interface recipes. Fresh 25-CU verification refreshed every stored projection;
function statuses are unchanged. A worker batch then promoted all four reopened tasks
plus the main.c Tmenu_params member repair and two global-object views. The follow-on
Tmenu_params canonicalization was rejected on handle_menu with a second, undisplayed
difference window and remains blocked with evidence.

Global-object layout evidence now proposes views for uniquely named file-scope objects,
which surfaced Tcmdline and Tjump_sequence in main.c.

player.c declared `max_speed` extern although the historical CU defines it and
`gravity_modifier` as initialized .data at lines 14 and 16. Both definitions were
restored from DWARF type and verifier bytes; the storage census reports EXACT_OWNER for
both, and the ordinary recovered-game link of all 25 objects with the built Allegro and
Xiph archives now completes with no unresolved symbols. The executable is not executed.
`--verify-all` publishes the link record. Per the user's direction the priority is now
matching the remaining 69 game function bodies toward a standalone build; library byte
reproduction and PE layout are deferred.


## Compile-order coupling and probe-driven definition moves

Isolated probes restored main.c's definitions to DWARF line order. Emission-order
agreement with the original rose from 33% to 90%, play_sound became exact and
check_beta_tester reached its historical size, but line_alert and uninit_game regressed:
a function's register choices depend on what the compiler emitted just before it, so a
whole-file reorder cannot pass the gate while neighbors still differ. The lesson is in
the codegen rule database with the retained probe records.

Instead of forcing the order, cards now expose emission-order context and the queue
prefers frontier functions whose historical predecessors already match in order. A
supervisor probe compiles one single-definition move per out-of-order function; moves
that gain exact functions without regression become bounded SOURCE_ORDER tasks bound
to the current source and object identities. The first real trial found three safe moves
among seventy; the first, moving draw_progress_bar after its historical predecessor,
promoted through the unchanged gate and made stopGameMusic exact without a body edit
(185 exact functions). The first worker attempt crashed because the generated plan
lacked a file key; sources were verified byte-identical to the session snapshot, the
generator was fixed and tested, and the session closed.


## Read-only literal resolution for x87 memory operands

The unique-content literal resolver sized only four x87 load forms, so a `fadds` or
`fmuls` constant fell through to the C-string path and stayed unresolved even when its
twelve-byte neighbourhood located uniquely in the original read-only data. The size table
now covers the d8/dc arithmetic forms and flds/fldl. play_sound became FUNCTION_MATCH with
its remaining same-CU displacement recorded as BODY_MATCH_LAYOUT_BLOCKED (187 exact).
Reports also retain `literal_anchor_evidence`: the pool bases implied by every uniquely
located literal; a base is adopted only when at least two distinct literals agree and
none disagrees. main.c's pool order still disagrees, so no base was adopted there. A
trial content check at anchored addresses was removed because it turned a known data
difference (the it15 URL in options.c) into a false function regression; string content
stays a separate data proof.
