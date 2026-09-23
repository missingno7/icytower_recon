# `change_profile` isolated Luna research — 2026-09-23

## Strict result

The retained candidate `change_profile-local-lifetime.c` is a strict `FUNCTION_MATCH` at 188/188 bytes in two full-CU overlays: current definition order and historical definition order, both with `--no-prototypes`. Each overlay starts from 62 exact functions, gains only `change_profile` (63 exact), and loses none. In both comparison receipts the focused function has `relocation_resolved_equal: true`, `first_difference: null`, and `status: FUNCTION_MATCH`. The complete object and CU remain non-matches.

- Candidate body: `docs/attempts/research-luna-change-profile/change_profile-local-lifetime.c`
- Production-equivalent receipt: `docs/attempts/tu-context/game-main/luna-change-profile-local-lifetime-20260923.json`
- Historical-order receipt: `docs/attempts/tu-context/game-main/luna-change-profile-local-lifetime-historical-20260923.json`
- Strict full comparison: `build/tu-context/game-main/luna-change-profile-local-lifetime/comparison.json`
- Historical full comparison: `build/tu-context/game-main/luna-change-profile-local-lifetime-historical/comparison.json`

## Decisive source lifetime

The original function has one DWARF local, `Tprofile *newProfile`, and the historical code loads global `profile` for the initial null test. On the non-null path it refreshes the global after `syncProfileFromOptions` and `save_profile`, then passes the refreshed pointer to `select_profile`; on the null path the original pointer value reaches the shared call setup directly.

The earlier retained body used the global directly for the guard and selector argument. GCC 4.4.1 formed a zero-valued merge for `select_profile` on the null edge, laid it out as a far conditional to a trailing `xor`/back-jump, and emitted 196 bytes. Reuse the evidenced `newProfile` local across the guard and call instead:

```c
newProfile = profile;
if (newProfile) {
    syncProfileFromOptions();
    save_profile(profile);
    newProfile = profile;
}
newProfile = select_profile(newProfile, profiles, numProfiles, &ctrl);
```

This preserves the updated global value after calls on the non-null path while carrying the already-loaded pointer on the null path. The compiler now emits the original shared call setup and exact body. No declaration, header, or compiler-flag changes were used.

## Hypothesis and outcome record

- Existing local-copy spelling (save/test a copied pointer, still select from the global): 196/188; same first difference at +13.
- Existing explicit else passing constant zero: 232/188.
- Existing unconditional `free(profile)`: 192/188, different prologue.
- New mutually exclusive duplicate `select_profile(profile, ...)` call sites: 232/188; did not reproduce the shared setup.
- Decisive local-lifetime spelling above: 188/188 strict match in both order probes.

The pre-existing details are in `docs/attempts/game-main/change_profile-variants.json` and the earlier production attempt ledger. The duplicated-call candidate and its TU receipt remain in `docs/attempts/research-luna-change-profile/` and `docs/attempts/tu-context/game-main/` as a negative experiment.

## Context caveat

The successful isolated TU overlays report 14 non-exact unchanged bodies whose emitted bytes change in this context. No existing exact function status is lost. Strict CU/object equality is not established. The candidate was subsequently accepted through the serialized MEDIUM body workflow: `grinder_task.py begin --medium`, `check_function.py`, then `promote_function.py --claim BODY_MATCH_LAYOUT_BLOCKED`. Acceptance passed 156 tests, diagnostic linking, and global audit. Current generated progress records 209 `FUNCTION_MATCH` functions and 35,299 strict game-function bytes. The extra layout state records two proven same-CU targets whose current call displacements differ from the original partial layout; it is not object or CU equality.
