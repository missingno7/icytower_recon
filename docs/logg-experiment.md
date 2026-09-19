# Modified logg recovery

The historical `C:\Lib\allegro4\addons\logg\logg.c` CU now has a complete
source candidate in `third_party/recovered/logg.c`. At -O2, all 18 emitted
functions and its complete 2061-byte logical text contribution match, including
padding and independently resolved relocations. The 4-byte initialized data
and 76-byte read-only contribution also match. This does not establish object
or debug-metadata equality.

The candidate retains Allegro 4.4.1 streaming code from the locked upstream
file. Original DWARF and disassembly establish the added 12-byte memory context,
four callbacks, shared decoder and memory-loading wrapper. The emitted census
includes the Vorbis header's `_ov_header_fseek_wrap`, not just explicitly
written source functions. Build inputs use the locked libvorbis 1.2.0 and
libogg 1.1.3 headers. The upstream addon has its own MIT license, retained in
`third_party/licenses/logg-license.txt`.

The memory reader returns a byte count, and SEEK_END assigns the buffer length
without applying its offset argument. These historical semantics are preserved.
The initial switch-based seek candidate was 55 bytes versus the original 51;
an if/else chain reproduces the exact branch sequence. No placement directives,
copied machine code, or fallback paths are used.

The addon is a separately verified object and now links with the 22 candidate
Xiph objects and Allegro in a synthetic audio PE. Xiph byte equality and the
GCC 4.2.1 libogg compiler remain unresolved. Game main helpers also remain absent.
See `docs/experiments/allegro-logg-O2.json` for the full inventory and the
optimization matrix for alternative compiler settings.
