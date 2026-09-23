# Replay selector pre-table pool ordering

Research-only TDM-2/GCC 4.4.1 `-O2` probes. No maintained source, generated current state, function card, or recovery ledger was edited.

## The four-byte span is not a standalone object

The original replay `.rdata` contribution starts at VA `0x4d7960`. Its jump table is at contribution `+0x1b8` through `+0x304` (83 words). The bytes immediately before the table are the tail of the source string `WARNING: It will be gone forever.`: that literal starts at `+0x194`; its terminating NUL is at `+0x1b5`; two zero alignment bytes at `+0x1b6` and `+0x1b7` bring the table to `+0x1b8`.

The owner-aligned candidate’s table is at `+0x1b4` through `+0x300`. In the current source ordering, the table follows the folder-title literal. The literal is one byte shorter than the original: candidate source has `Select a new folder and press OK` without the period, while the original PE contains the period. Adding the historically present period alone does not move the table: GCC consumes the added byte from the existing alignment slack. The candidate table therefore does not have a four-byte preceding variable or literal that can be moved as a unit.

The pool inventory explains the differing endpoint:

| Content | Original contribution offset | Owner-aligned candidate before source-order correction |
|---|---:|---:|
| `itr\0` | `+0x154` | `+0x18c` |
| `Select a new folder and press OK.\0` | `+0x158` | `+0x190` |
| empty-string owner used by `replace_filename` | `+0x17a` | suffix NUL in the title at `+0x1b1` |
| `Really delete replay?\0` | `+0x17b` | `+0x176` |
| `WARNING: It will be gone forever.\0` | `+0x194` | `+0x154` |
| switch table | `+0x1b8` | `+0x1b4` |

The COFF candidate’s `.rdata` symbols and relocations show its table is compiler-generated and owned by `replay_selector`. Its first jump target relocation is at `.text+0x1793`, with addend `0x1b4`; there is no symbol or relocation owner for any standalone four-byte object before the table. The original table’s absolute first target is `0x41dadd` at `0x4d7b18`.

## Historical source/CFG evidence and probe

Original `replay_selector` table key 47 targets `0x41db4c`. The disassembly at that target reaches the folder-picker setup and calls `file_select_ex` at `0x41dbde`, using `itr` at `0x4d7ab4`, the title at `0x4d7ab8`, and the empty string at `0x4d7ada`. The original table maps keys 48–51 to default, so the current source’s KEY_F2 through KEY_F5 cases are not historical. The original line table maps Escape to line 786, the file-picker call/title to lines 795–796, and the delete warning call to lines 858–859. This supports a source reconstruction with the chooser under KEY_F1 and before delete handling.

`source-owner-summary.json` is an isolated, source-supported probe that moves the chooser to KEY_F1, removes unsupported KEY_F2–KEY_F5 arms, adds KEY_SPACE as an alias for KEY_ENTER (historical keys 67 and 75 share a jump-table target), and keeps the const named header at `.rdata+0x470`. `folder-title-period-summary.json` adds the original PE’s title period. Both retain `create_replay` as FUNCTION_MATCH and keep the five listed exact neighbors exact, but both retain the table at `+0x1b4` and `get_replay_property` has eight unequal string relocations.

With the corrected chooser placement and title spelling, the candidate pool has `itr` at `+0x154`, title at `+0x158`, and the empty-string reference at `+0x17a`, matching those historical references. The next strings differ: candidate puts the warning at `+0x17c` and `Really delete replay?` at `+0x19e`; history puts the delete question at `+0x17b` and warning at `+0x194`. The historical table follows the warning; candidate table follows the delete question. Thus the remaining table position difference is the ordering and alignment of the two `my_alert` strings, not a separately owned four-byte contribution.

Historical machine code copies the first `my_alert` argument (`Really delete replay?`) into a stack buffer before referencing the warning argument. The candidate emits the warning pointer first and then the first-argument pointer. The existing line/DWARF/COFF evidence does not establish which historical source construct caused that first-argument-before-second-argument emission. I did not add a guessed temporary or modify a protected helper to force it. That missing source-context evidence is the blocker for moving the table and all eight helper string targets together while retaining the header at `+0x470`.

## Retained artifacts

- `pe-neighborhood.json`: original and candidate raw bytes, offsets, and owners.
- `source-owner-summary.json` / `source.c`: key-47/line-order source reconstruction probe.
- `folder-title-period-summary.json` / `folder-title-period-source.c`: same probe with the period restored.
- `base-order-period-summary.json` / `base-order-period-source.c`: period-only control on the prior owner-aligned source order.
- `helper-context-findings.md` in sibling `rdata-order/`: prior strict relocation/context analysis.

The first `summary.json` from the initial case-block move was invalid as a source-preserving probe: its extractor unintentionally removed intervening cases. It is retained only as a failed tooling attempt and must not be interpreted as candidate evidence.
