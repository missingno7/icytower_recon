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
