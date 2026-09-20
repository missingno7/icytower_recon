# Aligned literal content evidence

The previous layout classification conflated unknown data ownership with incorrect
source literals. The diagnostic now requires matching decoded instruction boundaries,
identical bytes outside the relocation operand, a supported immediate-pointer or
x87 memory form, valid read-only extents, and no overlapping data relocations.
Original operand addresses are explicitly diagnostic observations. They never enter
the independent relocation resolver.

The first generated source experiment changed only add_profile's filename format
from "%s%s" to "%s%s.itp". FAST proved all 195 bytes after independent relocation
resolution; strict acceptance preserved neighbors, checked the ordinary link and
published the ledger atomically. The exact source and before/after proof remain in
[the attempt history](attempts/game-main/add_profile.jsonl).

Repeated literals require maintained-source compiler line mappings identifying each
edited token. Unsupported escapes, embedded NULs, concatenation, prefixed strings,
ambiguous mappings and inconsistent expected payloads are refused. The source pattern
application recomputes its plan from validated receipts within an active body session.

The automatic worker uses the existing begin/apply/check/promote gates. A real
fldads_dump_local_cache run reached exact FAST but publication and rollback hit
filesystem write failures, including outside the sandbox. The worker stopped with
RECOVERY_REQUIRED and retained the journal and source. Recovery restored the prior
complete state; the source was then explicitly restored before changing infrastructure.
The failure is retained in docs/attempts/pattern-runs/20260920T205152162605Z.jsonl.

Shared output writes now leave identical bytes untouched and replace changed files
through a flushed temporary file. Rollback uses the same primitive. Injected failures
verify that prior contents survive failed writes and replacements. This is an I/O
hardening change, not a relaxation of publication, function or object proof.

After the writer fix, the same automatic worker promoted fldads_dump_local_cache
and delete_profile through complete acceptance. It then corrected both evidenced
check_characters logging strings, found a remaining named-global mismatch at +214,
restored the source and blocked the task. The current candidate refers to curr_char;
DWARF plus the original global COFF root identifies the original address as
play_char.max. This is now a concrete next supervisor problem, not a license to
accept the masked body. [Machine-readable validation](attempts/literal-repair-validation.json)
records all three accepted function proofs and the remaining mismatch.

The fld_adspot literal repair also allowed the unchanged fldads_get_random_ad and fldads_update_local_adimg bodies to pass independent relocation resolution. All five new FUNCTION_MATCH statuses came from fresh whole-CU comparison; only three function bodies received generated literal edits. The final 197-test suite and global audit passed, with no active session or publication journal.

Shared pool evidence is now generated under `docs/current/literals/<target>/` and
linked from function cards as `literal_dependencies`. Each card groups candidate
COFF `.rdata` references by section addend, lists same-CU consumers, records the
historical operand addresses and preserves supported payload diagnostics. Identical
payloads at different candidate addends stay separate. Multiple observed historical
addresses are visible; none becomes an independent relocation binding. Payload
length is not proof of an independently allocated object's extent.

This exposes create_profile's empty-string dependency without asking the grinder
to parse the whole profile CU. Its instruction permutation is separate from the
unproved literal placement. Shared references do not establish which peer caused
the placement and do not authorize editing any peer body.

FAST writes target-relevant pool cards beside its own build evidence, using the
fresh source identity. It never links an edited candidate's pool to an older
canonical pool card. Canonical publication closes obsolete literal cards.

The real create_profile card has four peer functions for its candidate empty-string
pool entry. Only one historical address has established operand correspondence;
eleven peer references remain unaligned observations. Raw bytes at those candidate
offsets are never presented as historical addresses. The initial broader address
count was preserved and explicitly invalidated in
`attempts/shared-literal-validation-before-alignment-review.json`; the corrected
validation is `attempts/shared-literal-validation.json`. No match or owner binding
was ever derived from either diagnostic.
