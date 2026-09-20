# Storage scope production-line validation

The storage census contains every original static-storage variable in the game
CUs, including variables that the strict ownership resolver cannot bind. It also
lists unpaired candidate definitions. Names, scopes, types and COFF evidence remain
separate from initializer and allocation proof. No target operand or similar
initializer content establishes a renamed declaration identity.

## Accepted generated task

`scope_fld_adspot_localFilename` moved the existing unchanged
`static char localFilename[256];` declaration from file scope into
`fldads_get_local_cache_name`, as independently recorded by original DWARF.
Candidate source uses elsewhere belonged to compiler-located locals, including a
loop-local shadow. Tests reject uses before a local declaration, after its lexical
block, and in its own initializer.

FAST and fresh acceptance preserved raw `.text`, allocated section contents,
normalized static-symbol identities, common allocations and non-debug relocations.
The existing strict resolver then proved the 256-byte BSS owner at `0x4dd040`.
The four previously unresolved references became exact. The owning CU increased
from 7 to 8 FUNCTION_MATCH results without changing any function expression.
The verified ledger publication, focused tests, ordinary link check and global
audit succeeded. The ordinary link still has the prior `max_speed` blocker.

The complete attempt is retained in
`docs/attempts/interfaces/scope_fld_adspot_localFilename.jsonl`.

## Rejected generated task

`scope_main_face` attempted the same declaration-only move into
`main_menu_callback`. GCC reordered BSS: `face` moved from offset 1072 to 1068,
while `number` moved from 1068 to 1072. Emitted text operands changed too.
The preservation gate rejected the experiment. `main.c` was restored byte-for-byte
and the task was marked BLOCKED_SUPERVISOR. The existing 47 exact main functions
and ledger status were retained. The target remains DIFFER, candidate size 2571
versus original 3741, with its first historical mismatch at offset 8.

The failed plan, precise layout differences and rollback are retained in
`docs/attempts/interfaces/scope_main_face.jsonl` and the current supervisor block.
Future scope failures automatically report bounded before/after contribution
changes, including symbol names and offsets.

Common-to-static moves, changes to already-proven bodies, ambiguous lexical
ownership, initializer changes and unresolved external uses are not cheap scope
tasks. This workflow does not claim whole-object or CU equality.
