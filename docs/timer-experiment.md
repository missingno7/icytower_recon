The first complete game CU is `src/timer.c`: three functions and five
`volatile int` definitions, in their original source order. The two counter
bodies reuse researched source; `install_timers` follows the original
disassembly and DWARF return type. It installs the Allegro timer, registers
the FPS callback at 1,000 ms, clears fps/frame_count/cycle_count, registers
the cycle callback at 20 ms, and returns -1. No carrier API is involved.

Original DWARF CU DIE: `0x400a1`; source definitions are at lines 13–17,
21, 30 and the install_timers declaration recorded in the census. The
reconstructed timer.h is a new interface filename, not an asserted original
header: this CU's line table does not list a game timer.h.

| Flags, plus -g -mfpmath=387 | Exact functions | Complete text contribution |
| --- | --- | --- |
| -O0 | 3 / 3 | differs: no inter-function alignment |
| -O1 | 3 / 3 | differs: no inter-function alignment |
| -O2 | 3 / 3 | exact, 152 bytes |
| -O3 | 3 / 3 | exact, 152 bytes |
| -Os | 2 / 3 | differs: layout and install_timers return instruction |

At -O2, fps_counter is 45 bytes, cycle_counter 16, and install_timers 88.
Three bytes of alignment after fps_counter make the complete span 152.
All 16 text relocations resolve to the original named globals, Allegro APIs,
and callback functions. The five globals are emitted as 16-byte COFF common
allocations for 4-byte volatile ints, matching the 16-byte spacing observed
in the final original BSS. This establishes typed common contributions, not
the final link order of those commons among all other game globals.

The candidate has no initialized data and no extra functions. Debug sections
are retained, but their contents differ: source paths, source lines, include
configuration and reconstructed header structure are not yet historical.
Consequently OBJECT_MATCH and CU_MATCH remain false.

The first missing artifact for full object reproduction is the exact
historical source/header/line configuration (or original object). The next
experiment is to reconstruct the CU's observed declarations and line layout
from source-files.json and the DIE graph, compare all debug section contents,
and establish common allocation order through a real multi-CU link.
