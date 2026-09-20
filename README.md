# Icy Tower 1.5.1 reconstruction

An independent reconstruction of the historical Win32 C project and build.
The original 25 game-tree translation units are preserved. This project
compiles real i386 COFF objects with archived TDM-GCC 4.4.1 and reuses exact
historical upstream sources. The ultimate target is whole-executable byte
identity, including debug metadata.

The reconstruction and bounded grinder pipeline are implemented. **This is not yet
a playable or complete reconstructed game.** The ordinary recovered-game link has
a recorded unresolved frontier; experimental synthetic links remain labeled.

Current grinder entry point: [docs/grinder.md](docs/grinder.md). The verified
ledger and generated [current progress](docs/current/progress.json),
[queue](docs/current/grinder-queue.json), [type status](docs/current/type-status.json)
and [interface conflicts](docs/current/interface-conflicts.json) are authoritative.
See the [production-line audit](docs/production-line-audit.md) for findings and limits.
Use `python tools/check_function.py game-scroller draw_scroller` for FAST and
`python tools/promote_function.py game-map getFloorData` for strict ACCEPTANCE.
Never edit recovery statuses manually.

Per-function claims, classifications and source identities are generated from fresh
verified CU receipts. Detailed [historical milestone notes](docs/history/readme-recovery-baseline.md)
and [experiments](docs/experiments) remain available as evidence. They are not the
current task queue. See [proof levels](docs/proof-levels.md) for acceptance semantics.

## Reproduce locally

Python 3.10+ standard library is sufficient. No pip packages, PortForge,
carrier, guest dispatch, binary execution or original-function fallback is
required. Use PowerShell from this directory.

One-time local export (the external research tree is read-only):

```powershell
python tools/bootstrap.py --research D:\Games\DOS\dos_recosystem\icytower_forged
python tools/fetch_xiph.py
curl.exe --fail --location --output third_party/archives/lpng1234.zip https://downloads.sourceforge.net/project/libpng/libpng12/older-releases/1.2.34/lpng1234.zip
curl.exe --fail --location --output third_party/archives/zlib-1.2.3.tar.gz https://zlib.net/fossils/zlib-1.2.3.tar.gz
python tools/import_png.py
```

The existing assets/icytower15.exe and runtime DLLs are user-supplied local
fixtures, ignored by Git. The bootstrap checks that the research binary is
identical before importing its address-based facts. Toolchain/upstream trees
are copied into this project and hashed individually. After bootstrap,
normal compilation has no dependency on the research repository or assets.

Normal compilation of complete CUs:

```powershell
python tools/build.py game-beta game-control game-csv game-timer game-loadpng game-savepng game-regpng allegro-timer allegro-color allegro-blit --compiler tdm-2
```

Verification and experiments (these explicitly read the original fixture):

```powershell
python tools/census.py --objdump C:\msys64\mingw64\bin\objdump.exe
python tools/experiment.py game-beta game-control game-csv game-timer allegro-timer allegro-color allegro-blit --matrix --compiler tdm-2
python tools/link_probe.py --compiler tdm-2
python tools/integration_link.py --compiler tdm-2
python tools/verify_integration.py
python tools/recovered_game_link.py
python tools/build_xiph.py
python tools/audio_link.py
python tools/test_pipeline.py
python tools/progress.py
python tools/generate_types.py --check
python tools/next_frontier.py
python tools/audit_signedness.py game-scroller draw_scroller
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

`tools/refresh_recovery.py` publishes current progress, cards, interface tasks and
blockers from verified receipts; `--check` makes stale generated state an audit
failure. Use `--reanalyze` after diagnostic-only changes and `--verify-all` after
verifier changes. Function and interface promotions normally refresh only the
affected dependency closure. `tools/classify_diff.py` labels observed comparison
differences without changing their verdict, and `tools/next_frontier.py`
ranks unresolved functions. `tools/sweep.py` permits at most three explicit
compiler flags for one CU. `tools/stage_forged_evidence.py` records hashes and
named claims from an external forged tree as evidence only; it never imports
or compiles that tree.

Inherited research's 751,448-byte function-span denominator differs from
the PE .text virtual size of 761,928 bytes. Keep those measures separate.
Old recommendations for Allegro 4.4.3.1 or modern DLL substitutions belong
to the source-port research and do not apply here. No behavioral replay
equivalence from that repository is counted as historical build equality.

The startup cmshared mismatch is resolved by the separately locked TDM-2
runtime candidate. Remaining work includes full game CUs, old libogg compiler,
Xiph linkage, exact compatibility sources, resources, common/data ordering,
and historical debug metadata. See the [full project brief](docs/project-brief.md).
