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

All 114 Allegro core CUs observed in the original debug census compile into
liballeg.a, including nine data-only driver/vtable CUs absent from the old
function-only ownership count. The archive also includes pinned Allegro 4.4.1
`inline.c` and `math3d.c`: neither has a debug-CU record in the original, but
the original game directly calls the former's `_draw_sprite` and `_rectfill`
exports, and the latter owns the perspective globals referenced by that
member. The modified logg addon is recovered separately.

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
python tools/stage_recovered_game.py
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
frontier begins with `HTTPFetchInternal`, then `_mangled_main`, profile and
game-flow routines (`select_profile`, `new_game`, `play`), presentation, the
alert loop, and `_strptime`. This failed link is a dependency measurement,
not a game executable.

The three loadpng source files are exact Allegro 4.4.1 inputs. The project now
pins the publisher's Windows libpng 1.2.34 sources and zlib 1.2.3 sources in
`third_party/png-lock.json`, supplying the historical headers needed to build
all three units. `tools/import_png.py` derives a candidate `libpng3.a` from
the named exports of the user-supplied `libpng3.dll`; this allows a normal
link with that DLL but does not establish the identity of the original import
archive. The runtime DLL itself remains excluded from object generation. The
adjacent recovery-owned HTTP unit is
mapped in `docs/httpget-recovery.md`; its two public request wrappers and its
transport call graph are now oracle-derived. The wrappers, socket-error helper,
and `HTTPRequest` compile as exact partial-unit functions. With all three PNG
units included, the ordinary link resolves `load_png` and now begins at the
remaining HTTP transport helper.

`tools/stage_recovered_game.py` copies the source-linked executable and only
the fixture's runtime assets into `build/recovered-game/tdm-2/runtime`. It
records hashes in `stage.json`, includes `data/data.dat`, character/profile
trees, configuration files, and the two non-system DLL imports, and excludes
the original `icytower15.exe`. Staging does not execute the candidate.
