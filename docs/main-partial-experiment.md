# main.c helper recovery

`src/main.c` currently recovers two historical helpers while the remaining
main CU entities stay absent. `getSampleFromOggDatafile` matches its complete
32-byte body at -O2, including the tail call to `logg_load_memory`: it passes
the DATAFILE entry's data pointer and byte count without a substitute layer.

`log2file` has a same-sized 189-byte candidate but is not exact. Its recovered
source preserves the original early `itrcheck` gate, pthread mutex, lazy
logfile path, append-mode output, newline, and historical va_list reuse. The
first instruction-level difference is how the compiler loads `itrcheck`.
The function therefore remains DIFFER even though its visible control flow
and call order agree.

`new_rand` and `new_srand` also match their complete 128-byte and 14-byte
bodies at -O2. The verifier resolves the random generator's x87 double and
single-precision literal relocations by their unique bytes in the original
read-only data, independently of masked instruction equality. That exact
dependency permits the recovered particle CU to enter the separate synthetic
custom-audio link.

This is intentionally a partial CU report: there are 82 original main.c
functions, so it cannot support a CU-wide text or object claim. The exact
helper is checked by the pipeline test, and the complete comparison inventory
is `docs/experiments/game-main-partial-O2.json`.
