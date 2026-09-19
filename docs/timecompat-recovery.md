# `timecompat.c` recovery map

`src/timecompat.c` is a one-function vendor compatibility unit. Its
`timegm` implementation at `0x41fe50` is fully reconstructed and its ordinary
`game-timecompat` object has whole-text equality with the historical 84-byte
compilation unit.

The function derives a local-to-GMT offset from `time(NULL)`, `localtime`,
`gmtime`, and `mktime`, then applies that offset to `mktime(ptm)`. The
comparison resolves all six CRT calls independently. It provides the exact
time conversion dependency used by the HTTP `Last-Modified` parser.
