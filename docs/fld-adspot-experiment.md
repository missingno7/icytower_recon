# Partial `fld_adspot.c` experiment

`fld_adspot.c` is now compiled as its own historical game translation-unit
target. The recovered `get_url_filename` helper performs the oracle's
backward slash scan over a remote URL and returns the cache-name boundary used
by the ad subsystem. `fldads_get_local_cache_name` rebuilds the 256-byte
static cache path through the recovered directory policy and appends the
requested cache filename. `fldads_get_local_filename_from_url` composes the
two helpers with the original tail-call shape.

The URL helper's 33-byte candidate differs from the historical 42-byte loop
layout, and the wrapper's local-call displacement is layout-dependent. The
cache helper has the historical 64-byte extent and masked body but its static
buffer relocation is not independently established. None receives exact
function credit. The other nine functions remain unrecovered; no original code
or object content is linked into this target.
