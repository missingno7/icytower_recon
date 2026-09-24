# extractHTTPResponse inline-index study (2026-09-24)

Target: `game-httpget / extractHTTPResponse`, using TDM-2 GCC 4.4.1, i386, `-O2`, historical definition order, and the current `--no-prototypes` TU probe context. All candidates were isolated body overlays. No maintained source, generated current state, or ledger was edited.

## Prior-work deduplication

`docs/attempts/game-httpget/extractHTTPResponse.jsonl` has 12 rows but only two distinct body hashes: `ab89023ade74` (baseline body, 11 rows) and `2242f69c2acb` (manual first-line loop, one row). The historical TU-context spec also records the manual loop form and its exact preheader observation. This batch therefore varied count-local identity/scope/declaration order instead of repeating those spellings.

## Strict outcomes

| Probe | Candidate / historical bytes | First mismatch | CU exact functions after | Neighbor effect | Effective identity |
|---|---:|---:|---:|---|---|
| `do_count_local` | 922 / 923 | 14 | 9 | none | `67c99da66ece9bee` |
| `while_count_local` | 930 / 923 | 8 | 7 | loses `HTTPFetchInternal`, `dumpHTTPResponse` | `f9df636e89922542` |
| `nested_count_if` | 937 / 923 | 14 | 9 | no function loss; raw displacement on `HTTPFetchInternal`, `HTTPRequest` | `ce5948c77146b79a` |
| `capacity_then_count` | 922 / 923 | 14 | 9 | none | `54ad359facc0bb04` |

None is `FUNCTION_MATCH`. In the best-sized forms, the first divergence is the argument spill layout: historical EAX/EDX homes are `-0x834(%ebp)` / `-0x82c(%ebp)`; candidates use `-0x838(%ebp)` / `-0x834(%ebp)`. The `do_count_local` form does reproduce the historical count preheader at offset 70 (`mov count,%edx; test %edx,%edx; jle`). Matching that sequence does not account for the prologue spill mismatch or the remaining 798/799 differing byte positions in the two best-sized reports.

Narrowing `bytesRead` into the positive-count branch substantially regresses code size. Replacing the positive-count `do` with a `while` also changes TU output and breaks two previously exact neighbors. Declaration reordering yields a different effective output at the same size, so the stack mismatch is sensitive to source local lifetime/order, not only the loop's byte count.

## Evidence paths

- Candidate bodies and manifests: this directory (`do_count_local.c`, `while_count_local.c`, `nested_count_if.c`, `capacity_then_count.c`, `batch-manifest*.json`).
- Strict probe receipts: `docs/attempts/tu-context/game-httpget/extract-http-*-20260924.json`.
- Per-probe comparison reports and complete candidate instruction/relocation evidence: `build/tu-context/game-httpget/extract-http-*-20260924/comparison.json`.
- Focused historical local scopes and mismatch: `docs/current/function-evidence/httpget/extractHTTPResponse.json`.
- Prior TU finding: `docs/attempts/game-httpget/tu-context-spec.json`.

## Next discriminator

The requested pointer-versus-index and exit-store discriminators are complete. The pointer form remains closer (922/923, first difference 14, 9 exact CU functions); both explicit-index forms are smaller and first differ at offset 8. Three store-placement variants and two `i = 0` placement variants collapse to the pointer control. See “Cursor and exit-store follow-up” below.

The next distinct source direction is to use outer `i` itself as the input index while retaining the historical output-pointer/capacity loop. Before compiling, compare it with the archived source and effective identities; stop if it collapses to a saved output without improving spill ownership.

## Cursor and exit-store follow-up

The original executable's cursor path is now archived in `historical-cursor-disassembly.txt`. It uses EDX for the output pointer and saves it at `-0x828(%ebp)`, EBX for remaining capacity, CL for the previous byte, and ESI for consumed input bytes. It initializes the outer `i` slot at `-0x824(%ebp)` and commits ESI there on CRLF and input-end paths before writing the final terminator.

The pointer `do_count_local` candidate instead spills its output pointer at `-0x824(%ebp)`, so the local/stack ownership is demonstrably displaced. Two explicit-index overlays did not improve alignment: `index_capacity` was 910/923 bytes (first difference 8, 761 differing bytes); `index_fixedcap` was 873/923 (first difference 8, 748 differing bytes). Both preserved 9 exact CU functions and had unique effective identities (`b0da3fc226aad9bd`, `b70aaf84cea38311`).

Moving `i = bytesRead` before the final terminator, duplicating it on the CRLF path, and moving it to the positive-count block exit collapsed to two outcomes: the first two forms were byte-for-byte the pointer control (`67c99da66ece9bee`, 922/923, first difference 14); the positive-block form was 931/923 (`b11857ad1c4abce2`). Adding `i = 0` before or after initializing `linebuf[0]` also collapsed to the 922-byte control, showing GCC removes that initialization when the later unconditional count commit dominates it.

This discriminates the cursor representations and the store position: the pointer spelling is closer in size and preserves the CU neighbors, while the explicit-index spellings move the frame/spills farther from the original. The remaining blocker is that the separate `bytesRead` source variable does not map to the original's outer `i` home/register lifetime. The outer-`i` form is already represented in the current maintained candidate; its convergence and strict mismatch are recorded below.


## Outer-`i` convergence check

The requested outer-`i` input-index form is already the current maintained candidate: its extracted function body hash is `2242f69c2acb5256f827d611245e43968fbf7327e8139271f1dd591736edd188`, matching archived FAST attempt 12 exactly. The full `src/httpget.c` input also matches attempt 12's saved identity (9,974 bytes, SHA-256 `410d68918baff159faa2c35215724353af937fe62574129746c3082f0ac04999`), along with both recovered header hashes. That saved strict result is `DIFFER`, size 924 versus 923, first mismatch at offset 14.

The generated current focused card independently reports the same body hash, compiler `tdm-2` with `-O2`, candidate size 924, and first mismatch at offset 14. The outer-`i` plus pointer/capacity source therefore collapses to an already compiled, current-source-backed result; no redundant compiler invocation was run. This is not a function match.