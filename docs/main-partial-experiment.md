# main.c helper recovery

`src/main.c` currently recovers eleven historical helpers while the remaining
main CU entities stay absent. `get_version_str`, `get_demo`, and
`get_controls` each match their complete 10-byte bodies at -O2. The version
accessor's anonymous `"1.5.1"` string relocation is resolved only by its
unique NUL-terminated bytes in the original read-only data; `get_demo` and
`get_controls` resolve their `demo` and `ctrl` globals by name.

`ok_to_play` returns the original constant `1`, while `switchedFromProgram`,
`switchedToProgram`, and `clickedCloseButton` exactly update the named
`hasFocus` and `closeButtonClicked` globals.

`is_custom_replay` matches its 66-byte predicate over the five recovered
`Treplay` settings fields: floor shrink, floor size, start speed, speed
increase, and gravity.

`getSampleFromOggDatafile` matches its complete
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

`update_reward` was independently derived from its named `reward_time` and
`reward_scale` globals, but both source control-flow forms tested at -O2 emit
a 54-byte body with the high-reward branch placed after the shared epilogue;
the original is 55 bytes and places that branch first. It remains absent from
`src/main.c` pending a source-level explanation for that compiler layout.

This is intentionally a partial CU report: there are 82 original main.c
functions, so it cannot support a CU-wide text or object claim. The exact
helper is checked by the pipeline test, and the complete comparison inventory
is `docs/experiments/game-main-partial-O2.json`.
