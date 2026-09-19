# Runtime candidate and integration build

The baseline TDM-1 crtbegin.o lacks the original cmshared call. The archived
TDM-2 package supplies it. `tools/import_tdm2.py` exports that package into a
separate local tree and pins all inputs in `toolchain/tdm-2-lock.json`.
The baseline lock remains historical evidence, including its old missing
runtime note; the new candidate resolves that specific startup blocker.

TDM-2 crt2.o and crtbegin.o have matching complete text contributions after
independently resolving their COFF relocations. The real synthetic CRT link
matches eight startup starts and spans across 792 bytes. Its literal byte
prefix is only seven bytes because references point to its own layout.
Neither result proves exact compiler-distribution or full-object identity.

All 114 original Allegro core CUs compile into liballeg.a, including nine
data-only driver/vtable CUs absent from the old function-only ownership
count. The modified logg addon is excluded and still needs recovery.

The DirectX header candidate is dx80_mgw.zip from Allegro's official archive:
https://liballeg.org/old.html (download https://liballeg.org/files/dx80_mgw.zip).
Its observed SHA-256 is pinned; no publisher checksum or exact original
header identity is claimed. Payloads remain local and ignored by Git.
Only headers are used; import libraries come from the locked compiler.

Reproduction after baseline bootstrap:

```powershell
python tools/import_tdm2.py --research D:\Games\DOS\dos_recosystem\icytower_forged
Invoke-WebRequest https://liballeg.org/files/dx80_mgw.zip -OutFile third_party/dx80_mgw.zip
python tools/import_directx.py
python tools/build_allegro.py --compiler tdm-2
python tools/integration_link.py --compiler tdm-2
python tools/link_probe.py --compiler tdm-2
python tools/runtime_compare.py
python tools/recovered_game_link.py
```

The integration executable uses a synthetic main and the recovered
beta/control/csv/directories/timer/stars objects plus the rebuilt archive. It
has linked successfully but has not been run. Building the archive does not
establish byte equality of all its CUs; the selected timer/color/blit
comparison results remain separately scoped.

`tools/recovered_game_link.py` links all currently recovered game objects with
main-partial's own historical `WinMain` wrapper. It records the ordinary
linker's result in `build/recovered-game/tdm-2/link.json` without any
synthetic entrypoint, stubs, original-code input, or execution. The current
frontier starts with `SplitURL` and `HTTPFetchInternal`, then `_mangled_main`,
custom image loading, profile/game-flow/presentation routines, remaining ad
HTTP support, profile data tables, and logg audio. This failed link is a
dependency measurement, not a game executable.

The three loadpng source files are exact Allegro 4.4.1 inputs, but they cannot
yet join this link: the locked TDM toolchains contain neither `png.h` nor a
libpng import archive, while the user-supplied `libpng3.dll` and `zlib1.dll`
are runtime assets and deliberately excluded from object generation. The
historical libpng 1.2.34 headers and import library must be pinned before a
`game-loadpng` target is introduced. The adjacent recovery-owned HTTP unit is
mapped in `docs/httpget-recovery.md`; its two public request wrappers and its
transport call graph are now oracle-derived. The wrappers, socket-error helper,
and `HTTPRequest` compile as exact partial-unit functions; the ordinary link
now exposes the remaining split and transport helpers.
