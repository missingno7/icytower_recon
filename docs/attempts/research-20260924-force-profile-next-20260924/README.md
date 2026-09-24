# force_create_profile CFG follow-up (2026-09-24)

Isolated research only. No edits were made to `src/`, `tools/`, the recovery ledger, or generated current state. Locked GCC 4.4.1 (`tdm-2`, `-O2`) was used for every full-TU probe. The strict baseline remains 64/82 exact `game-main` functions; the promoted screen-macro body is `DIFFER`, 1546 candidate bytes / 1538 historical bytes.

## Starting promotions reviewed

- `force_create_profile_screen_macros_20260924` and its check transaction are in `docs/attempts/tu-context/transactions/`.
- `force_create_profile_remaining_screen_macros_20260924` and its check transaction are also there.
- Notes and focused original CFG captures: `docs/attempts/research-20260924-screen-macro-replay-01/README.md`, `receipt.json`, `original-force-create-prefix.txt`, and `original-force-create-tail.txt`.
- Both null-driver macro promotions preserved all 64 exact peers. The first screen-macro body was 1490/1538 bytes; after converting the two remaining direct dimension pairs, it is 1546/1538. The correction is CFG-supported; it does not finish the function.

## New original-CFG finding

The original instruction sequence gives a concrete source-control-flow constraint:

- At `0x40d7b7`, `get_string` returns in EAX; `cmp eax,-1` at `0x40d7b7` is followed by `jge 0x40d90c` at `0x40d7ba`. Values below `-1` fall through to `checkMenuFocus` at `0x40d7c0` and redraw.
- At `0x40d90c`, `je 0x40d9c4` uses the same comparison flags. Exactly `-1` takes the “create profile later” alert path.
- Otherwise `cmp BYTE PTR [ebp-0x38],0` at `0x40d912` and `je 0x40d7c0` retry on an empty name. Nonempty names proceed to `replaceBadCharacters` and `create_profile`.

The production source instead had `res<0` retry, `res==0` select the “create later” path, and an empty-name test guarded by `res>0`. This did not encode the original sentinel/empty-name CFG.

## Probe outcomes

All source changes below existed only as saved overlays. Exact-peer counts came from strict full-TU comparison, and effective code outcomes were deduplicated by candidate instruction-byte SHA-256 in `effective-outcomes.json`.

| Probe | CFG/source question | Candidate result | Exact peers |
| --- | --- | --- | --- |
| `rectfill_args_staged` | Stage color and dimensions to test rectfill argument evaluation order | 1546 bytes; no improvement | 64/82 |
| `rectfill_dimensions_staged` | Stage only conditional dimensions | 1546 bytes; no improvement | 64/82 |
| `rectfill_color_staged` | Stage only `makecol` result | 1546 bytes; no improvement | 64/82 |
| `sentinel_then_empty` | Use `< -1` retry, then `==-1`, then empty-name guard | 1544 bytes; 18 jump instructions | 64/82 |
| `sentinel_outer_ge` | Guard success/sentinel handling with `res >= -1`, then `res == -1`, then empty-name check | 1537 bytes; 19 jump instructions | 64/82 |

The argument-order hypothesis was rejected: the promoted body already evaluates `makecol`, the `gfx_driver` width/height pair, then the screen bitmap vtable in the same order shown in the original code. The three staged variants either changed register assignment or emitted the same basic sequence and did not address the remaining CFG mismatch.

`sentinel_outer_ge` is the CFG-supported candidate. Around its input handling it compiles to the same branch structure as the original: `cmp eax,-1; jge +0x4b8`, then `je +0x56f` for the sentinel, then the empty-name check branches to the redraw block at `+0x36c`. It has 19 conditional/unconditional jumps, matching the original branch count. The `sentinel_then_empty` alternative omits one jump and does not match that CFG. The corrected candidate stays `DIFFER`; strict comparison reports 1537/1538 bytes, first raw difference at function offset `0x15` (a branch displacement), and 291 instructions versus 292 in the original. This is not a size-based acceptance claim.

The candidate instruction-stream hashes for the five probes are all distinct. No duplicate effective probe output was counted as a new result.

## Handoff artifacts and reproduction

- Retained complete body: `force_create_profile_sentinel_outer_ge_body.c` (2227 bytes, SHA-256 `f3e78b9f5579115df57f95e0151f353aeb728e3645bcefe9e6fd227839b6b34d`; 58 LF newlines, no CRLF/CRCRLF).
- TU-context spec: `tu-context-spec.json`
- Reproduction output: `python tools/tu_context_probe.py game-main src/main.c force-profile-sentinel-cfg-normalized-20260924 --order current --body force_create_profile=docs/attempts/research-20260924-force-profile-next-20260924/force_create_profile_sentinel_outer_ge_body.c --no-prototypes --focus force_create_profile`
- Reproduction result: compile OK, matches 64 before and after, no exact gains or losses, 79/82 same historical predecessor count, and target remains 1537/1538 `DIFFER`. Identity and captured output are in `normalized-reproduction.json` and `normalized-tu-context.json`; strict focused output is `force-profile-sentinel-cfg-normalized-strict.json`.
- The reproduction printed no missing call-graph edges and four extra compile-side edges from Allegro inline expansion (`draw_sprite`, `rect`, `rectfill`, `memset`).

## Blocker and next experiment

The new body corrects a CFG mismatch but is not a `FUNCTION_MATCH`. It was promoted through `force_create_profile_sentinel_cfg_20260924`: the fresh strict check preserved all 64 exact main functions, then 156 function tests, diagnostic link, and global audit passed. The next experiment should use the refreshed aligned instruction and relocation evidence to locate the remaining code-generation/layout difference after the now-matching sentinel/empty-name edges; inspect the differing lexical-scope/line-table record for the outer `res >= -1` block before trying any additional source-shape edits. Do not optimize toward 1538 bytes.
