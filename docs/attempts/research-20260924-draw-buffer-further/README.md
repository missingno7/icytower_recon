# draw_buffer follow-up: scoped negative

Date: 2026-09-24. No maintained source, recovery ledger, current card, or exact peer was edited. No new compile was run: review of the retained evidence shows the proposed discriminators already exist, so another body spelling or a duplicate pass dump would not change the next decision.

## State and protected evidence

`draw_buffer` remains `DIFFER`, historical size 185, current 181, first historical mismatch at +27 (the conditional displacement after two one-byte load/update reorderings). Strict CU evidence retains 11/17 exact functions (181/185 function bytes); the target has 126 differing bytes and 4/4 unequal raw relocation windows. This is not a recovery credit or layout proof. The independent same-context receipts preserve these 11 exact peers: `hash2`, `generate_profile_checksum`, `get_rank_id`, `get_rank`, `set_next_rank_message`, `profile_data_page_advanced`, `profile_data_page_basic`, `profile_data_page_extra`, `save_profile`, `load_profile`, and `delete_profile`.

## Effective outcome summary

The verified three-receipt effective-outcome grouping reports one class, `c87e157d5dda279a`: 181 bytes, first mismatch +27, 11/17 exact functions, frame 0x12c, five branches, two calls. Those receipts cover the historical-order whole-TU control, direct dereference/no-`c`, and removal of the redundant explicit `makecol` prototype. The earlier 10-overlay source batch has three instruction-byte classes; none changes the target mismatch or peer count. The retained `postincrement_store` whole-TU probe also stays 181 bytes with +27 and historical/candidate emission position both 6.

Source-shape search already tested pointer indexing/update spellings, loop forms, branch polarity/local updates, reset placement, and removing optimizer-only `c`. They either collapse to known outcomes or get shorter and diverge earlier. DWARF confirms parameter/local types and `tempBuf` frame placement; it does not show a distinct lexical-scope explanation.

## CFG / pass evidence and next decision

The retained diagnostic CFG/RTL expansion comparison shows equivalent high-level CFG and that GCC's RTL expansion already carries the incremented pointer into the load. That explains candidate `inc ebx; mov al,(ebx)` versus historical `mov al,1(ebx); inc ebx`, but does not identify the first compiler pass relative to the unavailable historical object/dump. The original and candidate have no source-level CFG difference established by this evidence.

**Decision:** the next recovery decision is unchanged. Do not expand the local spelling family or infer historical source from the compiler-only context. A future discriminating experiment needs new evidence that affects lowering before RTL expansion (for example, recovered historical statement/source-line placement or a justified declaration/type/context fact). Without that evidence, close this branch at “optimizer lowering/instruction scheduling remains unexplained”; preserve the exact profile peers and continue independent recovery.

## Small artifact set

- Focused card: `docs/current/functions/profile/draw_buffer.json`
- Source batch and outcomes: `docs/attempts/research-20260924-profile-draw-buffer-context/findings.md`
- Earlier effective grouping, exact peers, and byte-level mismatch: `docs/attempts/research-20260924-draw-buffer-profile/README.md`
- Pass evidence: `docs/attempts/research-20260924-draw-buffer-profile/cfg-rtl-followup.md`
- Additional whole-TU postincrement receipt: `docs/attempts/tu-context/game-profile/research-20260924-draw-buffer-postincrement-store.json`

Raw source, receipt, and report SHA-256 identities for this audit are recorded in `identities.json`.
