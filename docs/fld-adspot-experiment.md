# Partial `fld_adspot.c` experiment

`fld_adspot.c` is now compiled as its own historical game translation-unit
target. The recovered `get_url_filename` helper performs the oracle's
backward slash scan over a remote URL and returns the cache-name boundary used
by the ad subsystem. `fldads_get_local_cache_name` rebuilds the 256-byte
static cache path through the recovered directory policy and appends the
requested cache filename. `fldads_get_local_filename_from_url` composes the
two helpers with the original tail-call shape. `fldads_load_local_cache` opens
the derived `ads.csv` path through the recovered CSV CU, imports its contents,
and destroys the parser.

The URL helper's 33-byte candidate differs from the historical 42-byte loop
layout, and the wrapper's local-call displacement is layout-dependent. The
cache helper has the historical 64-byte extent and masked body but its static
buffer relocation is not independently established. The cache loader has its
historical 55-byte extent with all typed CSV and local-call targets resolved,
but its partial-CU direct-call distances differ. None receives exact function
credit. The other eight functions remain unrecovered; no original code or
object content is linked into this target.
