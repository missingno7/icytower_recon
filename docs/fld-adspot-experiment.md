# Partial `fld_adspot.c` experiment

`fld_adspot.c` is now compiled as its own historical game translation-unit
target. Two functions match byte-for-byte: `get_url_filename`, whose backward
slash scan returns the filename following the final slash, and
`fldads_destroy_cache`, which frees each local path, remote URL, and visit URL
before releasing the cache allocation. `fldads_start` also matches exactly: it
starts the historical ad worker through `pthread_create`.

`fldads_get_random_ad` now reproduces the 192-byte weighted selector body. It
computes the cumulative frequency under the cache mutex, chooses a scaled
random threshold, and walks the cache in source order. The function is
`CODEGEN_SIMILAR`; its anonymous `RAND_MAX` floating literal has no
independent section placement proof.

`fldads_load_cache_from_csv` accepts only three-field rows, rejects entries
whose cached image is absent, duplicates the remote/local/visit strings,
parses its frequency, and atomically replaces the old cache under the
historical pthread mutex. Its 282-byte body has every named call and typed
global relocation resolved; it is retained as `CODEGEN_SIMILAR` because the
partial CU's local layout and anonymous string section remain unproven.
`fldads_dump_local_cache` recreates `ads.csv` while holding the same mutex.
`fldads_update_cache` parses a downloaded CSV response, updates each local
image, reloads the cache, and persists the accepted rows.
`fldads_update_local_adimg` has its historical 230-byte extent: it compares a
local image timestamp with HTTP metadata, downloads stale or missing payloads,
and writes successful responses in binary mode.
`fldads_threadmain` loads the local cache, refreshes a listing older than three
days, validates the HTTP response and payload, and reports the final count.
The cache-path helper retains its 64-byte masked body. The URL wrapper and
local-cache loader have their historical extents but differ in local branch
layout. No original code or object content is linked into this target.
