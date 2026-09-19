# Partial `fld_adspot.c` experiment

`fld_adspot.c` is now compiled as its own historical game translation-unit
target. The recovered `get_url_filename` helper performs the oracle's
backward slash scan over a remote URL and returns the cache-name boundary used
by the ad subsystem.

Its 33-byte candidate is semantic source recovery but differs from the
historical 42-byte compiler loop layout, so it is recorded as `DIFFER`. The
other eleven functions remain unrecovered; no original code or object content
is linked into this target.
