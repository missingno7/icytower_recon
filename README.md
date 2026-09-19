# Icy Tower 1.5.1 reconstruction

An independent reconstruction of the historical Win32 C project and build.
The original 25 game-tree translation units are preserved. This project
compiles real i386 COFF objects with archived TDM-GCC 4.4.1 and reuses exact
historical upstream sources. The ultimate target is whole-executable byte
identity, including debug metadata.

The first pipeline is implemented. **This is not yet a playable or complete
reconstructed game.** Unknown CUs remain explicit skeletons, and the only
linked executables are clearly labeled synthetic CRT and integration experiments.

Current results:

- Fresh PE/COFF census, 148 DWARF CUs, 130,019 DIEs, 39,981 line rows,
  32,978 type DIEs, complete source-file tables, location/range lists, and
  no unresolved abstract-origin/specification chains.
- All 25 historical game source filenames generated; 18 GAME, 5
  VENDORED_UPSTREAM (two exact revisions unresolved), and 2 AMBIGUOUS.
  Three loadpng source files are populated verbatim from Allegro 4.4.1.
- Complete game control.c and timer.c: all 18 functions and their entire
  902-byte text contributions match, including padding and resolved relocations.
- All 114 historical Allegro core CUs build into a static library. The recovered
  game CUs link against it with a synthetic main and no fallback code.
- Allegro 4.4.1 timer.c and color.c: complete text contributions match at
  -O2, totaling 11,752 bytes; initialized data is checked separately.
- A real historical CRT link produces the original entry RVA 0x1110 and
  eight original startup symbol addresses with TDM-2. The first 792 bytes have matching
  function starts and spans. It is not a game layout or whole-byte match.
- Nine validation tests include wrong relocation targets, altered code and
  padding, unknown relocation kinds, origin chains, and independent builds.

See [machine-readable progress](docs/progress.json),
[blockers](docs/blockers.json), [proof levels](docs/proof-levels.md), and
[the timer experiment](docs/timer-experiment.md),
[control recovery](docs/control-experiment.md), and
[runtime selection and integration](docs/runtime-selection.md). Measurements and full
symbol/relocation records are retained in [docs/experiments](docs/experiments).

## Reproduce locally

Python 3.10+ standard library is sufficient. No pip packages, PortForge,
carrier, guest dispatch, binary execution or original-function fallback is
required. Use PowerShell from this directory.

One-time local export (the external research tree is read-only):

```powershell
python tools/bootstrap.py --research D:\Games\DOS\dos_recosystem\icytower_forged
python tools/fetch_xiph.py
```

The existing assets/icytower15.exe and runtime DLLs are user-supplied local
fixtures, ignored by Git. The bootstrap checks that the research binary is
identical before importing its address-based facts. Toolchain/upstream trees
are copied into this project and hashed individually. After bootstrap,
normal compilation has no dependency on the research repository or assets.

Normal compilation of complete CUs:

```powershell
python tools/build.py game-control game-timer allegro-timer allegro-color allegro-blit --compiler tdm-2
```

Verification and experiments (these explicitly read the original fixture):

```powershell
python tools/census.py --objdump C:\msys64\mingw64\bin\objdump.exe
python tools/experiment.py game-control game-timer allegro-timer allegro-color allegro-blit --matrix --compiler tdm-2
python tools/link_probe.py --compiler tdm-2
python tools/test_pipeline.py
python tools/progress.py
python tools/audit.py
```

The modern objdump is an identified analysis tool only. Historical gcc,
assembler, linker, archiver and resource compiler come from the local lock.
The census refuses a changed original hash; builds refuse changed locked
inputs; progress publishing refuses stale source/header or toolchain reports.

## Project map

| Directory | Purpose |
| --- | --- |
| src/ | The 25 original game-tree CUs, ownership inventory and proof overlay |
| include/ | Reconstructed game interfaces, upstream loadpng header, platform configuration |
| third_party/ | Historical Allegro/Xiph sources, source provenance and licenses |
| toolchain/ | TDM-GCC/binutils/MinGW local inputs and per-file SHA-256 lock |
| resources/ | Resource ownership and structural rebuild status |
| evidence/census/ | Fresh canonical PE, COFF, DWARF, types, globals, lines and source-file tables |
| evidence/research/ | Hash-pinned historical evidence; claims retain their original status |
| tools/ | Bootstrap, census, compiler/relocation verifier, real linker probe and validation |
| build/ | Reproducible objects, logs, full comparisons, link maps and synthetic PE; ignored |
| docs/ | Scope, measurements, proof policy and actionable blocker ledger |

`src/units.json` is the generated baseline inventory. `src/recovery.json`
overlays current validated recovery states. A census rerun never overwrites
source bodies. The whole DIE graph is retained as JSONL with references,
including parameters, local variables, inline instances, static functions,
array subranges and member offsets. Type DIE counts include duplicates;
they do not imply that 32,978 canonical C types have been emitted as headers.

Inherited research's 751,448-byte function-span denominator differs from
the PE .text virtual size of 761,928 bytes. Keep those measures separate.
Old recommendations for Allegro 4.4.3.1 or modern DLL substitutions belong
to the source-port research and do not apply here. No behavioral replay
equivalence from that repository is counted as historical build equality.

The startup cmshared mismatch is resolved by the separately locked TDM-2
runtime candidate. Remaining work includes full game CUs, old libogg compiler,
modified logg, exact compatibility sources, resources, common/data ordering,
and historical debug metadata. See the [full project brief](docs/project-brief.md).
