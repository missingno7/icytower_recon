Proof levels are recorded per function, CU, and linked image. They are not
interchangeable percentages.

| Level | Required evidence |
| --- | --- |
| BEHAVIOR_EQUAL | Named workload and compared state, including invocation coverage; external oracle runs only |
| CODEGEN_SIMILAR | Instruction/byte comparison; relocation-masked equality alone stays at this level |
| FUNCTION_MATCH | Same DWARF body length and every machine byte after independently resolving COFF relocation targets |
| OBJECT_MATCH | All code/data/BSS contributions, symbols, alignment, relocations and applicable debug records reproduced; unavailable original object records must be acknowledged |
| CU_MATCH | Complete historical CU, including local/static entities and metadata, satisfies the object-level contract |
| LINKED_LAYOUT_MATCH | Addresses and section placement arise from ordinary object/archive order and linker rules |
| PE_MATCH | Every PE section, directory, header and auxiliary record matches under an explicitly recorded comparison policy |
| WHOLE_EXE_MATCH | Entire file SHA-256 and byte comparison match; no excluded fields |

The additional metric `whole_text_contribution_equal` includes inter-function
padding across the DWARF CU span. It requires matching function order and
extents, all relocations resolved, and identical bytes for the whole span.
It is deliberately not called CU_MATCH. Object-file tail padding outside
the DWARF span is reported separately through section logical/raw sizes.

Anonymous read-only data is resolved by finding the complete, relocated
contribution uniquely in the original section. The verifier never obtains a
relocation target by copying the original value at that relocation site.
These observed placements never flow into build.py or link commands.

No original .o files have been located. COFF auxiliary File attribution for
late global symbols often names cygming-crtend.c and is not trusted as
ownership. DWARF supplies global/type ownership; COFF supplies linked names
and addresses. COFF-only function spans are inherited estimates that may
include padding. Duplicate type names remain separate DIEs until layout
equivalence is established.
