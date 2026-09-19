# Xiph candidate build and audio link

All 22 observed Xiph COFF CUs compile from the locked libvorbis 1.2.0 and
libogg 1.1.3 trees into libvorbisfile.a, libvorbis.a and libogg.a. The plan
in `third_party/xiph-build.json` records the observed membership, including
the data-only registry object. The original uses lookup.c through lsp.c;
it is not added as a separate archive member.

The normal build uses TDM-2 GCC 4.4.1, -O2 and x87. These are candidate settings.
The original Ogg CUs identify GCC 4.2.1-sjlj (mingw32-2), still unavailable.
Vorbis has COFF file records but no DWARF compiler record in this executable.
Neither library has been promoted to complete text or object equality.

`tools/audio_link.py` links the reconstructed modified logg object against
these archives and historical Allegro. All dependencies resolve in a real
synthetic Win32 PE. It has not been executed and is not the game executable.
The build scripts do not read the original executable or census. A guarded
test enforces that separation for both compilation and linkage.

Reproduce with `python tools/build_xiph.py`, then `python tools/audio_link.py`.
Archive membership, commands, input identities and output hashes are recorded
in `docs/experiments/xiph-build.json` and `docs/experiments/audio-link.json`.
The next proof step is compiler/configuration comparison, not runtime success.
