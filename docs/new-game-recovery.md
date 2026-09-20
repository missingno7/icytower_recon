# `new_game` recovery

`new_game` is reconstructed in `src/main.c` from the original function at
`0x40dc9c` (1,139 bytes, DWARF declaration line 2871). Its only named local
is `i`; the compiler also records inlined `new_srand` at source line 2878 and
`is_custom_replay` at line 2914.

The recovered source resets session and recording state, derives replay
settings for either an existing replay or a new recording, seeds both random
streams, clears the map and game statistics, adds the first 30 floors,
initializes the active player, and loads the selected custom character. The
literal messages and direct game API targets come from the original code and
read-only data.

The TDM 4.4.1 `-O2` candidate is 1,127 bytes versus the original 1,139 and
is classified `DIFFER`. It is linked as normal reconstructed source:
`python tools\\recovered_game_link.py --compiler tdm-2` no longer reports
`new_game` or its recovered `reset_player` dependency as unresolved. Further
work must converge the source shape and code generation; no original code or
fixed placement is used.
