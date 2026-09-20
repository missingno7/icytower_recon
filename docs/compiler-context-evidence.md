# Compiler context and source definition order

This is diagnostic evidence, not an alternative matching oracle. Production flags,
historical toolchain locks, original assets and protected function bodies remain
unchanged. Probes compile isolated full-CU copies under `build/compiler-evidence`.
They cannot be promoted as game objects.

## Observed dependencies

HTTPFetchInternal has three one-byte scratch-push differences at offsets 127, 164
and 444. In an isolated copy, replacing the earlier destroyHTTPResponse definition
with a declaration changes the first two offsets without changing the target body.
Omitting extractHTTPResponse or getSocketError does not help. Correcting the local
dataPtr declaration to its original DWARF unsigned-char pointer also leaves all
three mismatches. These failed alternatives are retained with source snapshots,
commands, object identities and focused RTL excerpts in
`docs/attempts/compiler-context/game-httpget/HTTPFetchInternal.json` and its JSONL
history. No register masking or behavioral-equivalence acceptance was added.

The official GCC 4.4.1 source explains a plausible mechanism. The i386 peephole2
patterns turn small stack adjustments into scratch-register pushes; the register
search uses a persistent search position across successful allocations. Relevant
primary sources are the tagged
[i386.md patterns](https://github.com/gcc-mirror/gcc/blob/releases/gcc-4.4.1/gcc/config/i386/i386.md#L20975)
and [peep2_find_free_register](https://github.com/gcc-mirror/gcc/blob/releases/gcc-4.4.1/gcc/recog.c#L2930).
The locked compiler's actual peephole2 dump records these scratch pushes. This
explains the HTTP probe; it does not prove that every register mismatch has this
cause. Source copies fetched for research are never compilation inputs.

draw_scroller also changes when restart_scroller is omitted in a diagnostic copy,
although the target body remains unchanged. That dependency routes it to the
supervisor. The original six mismatches at offsets 93, 96, 100, 103, 107 and 110
remain unresolved. Removing init_scroller or disabling instruction scheduling did
not repair them. Disabling unit-at-a-time optimization added mismatches at offsets
13, 15, 118 and 121 and reduced exact neighboring functions from three to two.
The failed flag trials remain diagnostic only.

## Original definition order

Original scroller.c DWARF declaration lines establish init_scroller (16),
draw_scroller (45), scroll_scroller (70), restart_scroller (75). The previous
candidate used executable-address order instead. The SOURCE_ORDER gate restored
the original source order, preserving every function body byte-for-byte and every
existing exact function proof. GCC then emitted the historical natural offsets
0, 16, 44 and 440, with a 640-byte text contribution. The six draw_scroller register
mismatches remain: this is not complete text, object or CU recovery.

`tools/source_order.py` generalizes this repair from unique original DWARF lines.
Interleaved declarations/directives, absent or conflicting lines and newly implicit
declarations prevent automatic acceptance. No function-address linker placement is
used. A completed order task has the separate HISTORICAL_SOURCE_ORDER claim.

## Supervisor workflow

Use `python tools/compiler_probe.py <target> <function> --omit-earlier <peer>`
only to investigate a bounded hypothesis. At most three peer/type/flag variants
are accepted per invocation. Each run first reproduces the unmodified CU's raw
text hash. Target body hashes, source identities and locked toolchain identity are
retained. Full dumps stay under build; target-only excerpts are linked from the
attempt record. Run `python tools/refresh_recovery.py --reanalyze` after a new
observation to update routing.

A context dependency blocks cheap body edits; it never grants layout-only or exact
status. Historical observations remain available after later negative probes, and
are marked stale when inputs differ. Changed target bodies require new evidence.
