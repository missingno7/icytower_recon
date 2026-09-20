# Partial `fld_adspot.c` experiment

`fld_adspot.c` is now compiled as its own historical game translation-unit
target. Its historical build needs `-fno-toplevel-reorder`: the setting
preserves the source's natural function order, which is independently visible
in the original unit's local call displacements. Seven functions now match
byte-for-byte. They include `get_url_filename`, whose backward slash scan
returns the filename following the final slash, `fldads_destroy_cache`, which
frees each local path, remote URL, and visit URL before releasing the cache
allocation, and `fldads_start`, which starts the historical ad worker through
`pthread_create`.

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
Historical DWARF confirms the outer `shouldDownloadAds` and `statCsv` locals
plus the lexical `pResponse` local. The 223-byte oracle spills `pResponse` to
the frame across the logging and update calls, while the 204-byte candidate
keeps the same local in `ebx`; both preserve the null-response, status, payload,
cleanup, and cache-age branches. No unsupported source change is retained for
this register-allocation difference. The cache-path helper retains its 64-byte
masked body. The URL wrapper, CSV loader, and local-cache loader are now exact.
No original code or object content is linked into this target.
