# Profile rank and display tables

`profile.c` owns seven initialized tables in the historical game contribution.
They were recovered from the original executable's `.data` and referenced
strings, then restored as ordinary C definitions in `src/profile.c`.

| Symbol | Historical VA | Type | Recovered initialized entries |
| --- | ---: | --- | ---: |
| `jcLabels` | `0x004bdbc0` | `char *[5]` | 5 |
| `rankLables` | `0x004bdbe0` | `char *[16]` | 12 strings, 4 null entries |
| `rankFloors` | `0x004bdc20` | `int[16]` | 12 values, 4 zero entries |
| `rankCombos` | `0x004bdc60` | `int[16]` | 12 values, 4 zero entries |
| `rankCCCs` | `0x004bdca0` | `int[16]` | 12 values, 4 zero entries |
| `rankNMLs` | `0x004bdce0` | `int[16]` | 12 values, 4 zero entries |
| `comboNames` | `0x004bdd20` | `char *[10]` | 10 |

The target's `profile.c` `.data` contribution begins at `0x004bdbc0` and is
392 bytes. The restored candidate has the same logical `.data` size and the
same named-global layout. `recovered_game_link.py` resolves all seven symbols
after this restoration.

Full `.rdata` equality is intentionally not claimed: the target's profile
contribution is 12,640 bytes and contains literals for unrecovered profile
functions, while the present candidate contribution is 1,504 bytes. The
pointer fields are therefore verified by recovered strings and named data
layout, rather than by a fabricated full read-only contribution.
