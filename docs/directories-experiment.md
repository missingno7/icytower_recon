# directories.c recovery

All seven functions and the complete 307-byte logical text contribution match at -O2,
including inter-function padding and independently resolved relocations.
Initialized path and format strings are verified separately. No object or
debug-metadata equality is claimed.

DWARF establishes the original signatures and source order: profiles, custom
characters, logfile, configfile, character, adcache, profile-specific directory.
The compiler emits a different order, reproduced without placement directives.

The recovered policy preserves the original operations: fixed paths use
strncpy; the custom-character root writes an empty string and returns zero;
the character path uses snprintf and returns file_exists with FA_DIREC.
The profile-specific function calls get_profiles_dir and then the original
overlapping sprintf operation. These details are retained for historical
fidelity rather than modernized.

This CU is compiled from source and included in the synthetic integration
link. The missing custom CU still interrupts natural original object layout.
See `docs/experiments/game-directories-O2.json` for all functions, data,
symbols, common allocations and relocations.
