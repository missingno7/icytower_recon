Original verification fixture: assets/icytower15.exe, 3,753,885 bytes,
SHA-256 `7570c6b0c7cddf6180d7c421bdc7d7bc1486c47a6d62cc6fde90670f62d4388d`.
The research repository's executable has the same identity.

Fresh PE/COFF parsing records ImageBase 0x400000, entry RVA 0x1110, GUI
subsystem 2, section alignment 0x1000, file alignment 0x200, and fifteen
sections. The .text virtual size is 761,928 bytes; raw size is 762,368.
The .bss virtual size is 223,608 bytes. Full headers, timestamps, checksum,
DOS stub bytes, section hashes, symbol/auxiliary records and all data
directories are in evidence/census/pe.json. There are 227 COFF File records
and 9,107 primary COFF symbols; auxiliary slots are preserved separately.

Export, base-relocation, TLS, load-configuration and PE debug directories
are absent. Nine .debug_* sections remain present: DWARF metadata is not
the PE debug directory. The .reloc section is absent. These are measured
directory/section facts, not assumptions applied by the parser.

There are **320 imports across 14 descriptors**, including two separate
msvcrt.dll descriptors. All DLL/name/IAT-address triples agree with the
exported imports.json. The research ownership table's 309 import-thunk
function spans are a different count and must not replace the import census.
No imported CRT routine is treated as a game recovery target.

The fresh DWARF census contains 148 CUs (145 GNU C 4.4.1, two GNU C
4.2.1-sjlj (mingw32-2), one GNU AS 2.19.1), 130,019 DIEs, 39,981 decoded
line rows, 8,491 location lists and 1,274 range lists. Original include
directories and filename indices are retained. Parameter/local/member/type
graphs and all raw attributes remain in dwarf-dies.jsonl; array bounds and
inline instances have not been flattened away.

The 2,465-function catalog combines freshly resolved DWARF records with the
existing COFF-only extent estimates. Every function includes its original
byte hash. Non-DWARF spans and the library ownership classifications remain
explicitly labeled inherited evidence. No new decompilation was required
for this census.

evidence/census/provenance.json identifies the fixture, analysis tool, parser
sources and raw-dump hashes. evidence/census-lock.json hashes every canonical
census output. `python tools/audit.py` checks these identities, upstream
copies, imported evidence, ownership totals and the input locks. Regenerating
with `tools/census.py --reuse-dumps` is permitted only when the old dump,
fixture and analysis-tool hashes all agree.
