# `do_replay_menu` residual research

Research-only TU overlays using the retained shared-copy and lexical-scope candidate. No maintained source, generated current state, or recovery ledger was edited. All probes used `game-main`, TDM-2 `-O2`, current definition order, and no generated prototypes.

## Original bytes and guest-copy CFG

The focused card records the aligned operand at function offset `+411`, VA `0x4d4bb3`, from the guest branch at `0x411132`. Original disassembly shows the guest path loading that pointer and joining the one `_strcpy` call at `0x41113e`; the non-guest branch at `0x41112c` reaches `0x411790`, loads `profile->handle`, and jumps back to the same call setup at `0x411137`.

Reading the original image with `objdump -s -j .rdata` gives bytes at `0x4d4bb0`:

```text
65 64 00 00 20 2d 20 00
```

Thus `0x4d4bb3` contains a lone NUL and `0x4d4bb4` begins `" - "`. The PE maps this address within `.rdata` (section RVA `0xd4000`; target raw file offset `0xd28b3`). The address has no named COFF symbol, and [`docs/current/literals/game-main/94.json`](../../current/literals/game-main/94.json) explicitly leaves literal ownership/placement unproven. The bytes establish the empty C-string payload at the observed operand, but do not identify which source literal or pooled owner supplied that byte.

Replacing the retained guest expression with `isGuest ? "" : profile->handle` keeps the shared `_strcpy` call in the emitted CFG, resolves the operand relocation to `0x4d4bb3`, and preserves all 63 exact peer functions. The code size remains 2643 bytes before the separate filename-call-order correction.

## Probe outcomes

`python tools/effective_outcomes.py game-main do_replay_menu --pattern 'research-do-replay-residual-*.json' --compact` grouped four probes into three effective outputs:

| Variant | Size | First mismatch | Peers |
|---|---:|---:|---:|
| Empty guest string only | 2643/2661 | `+406` (`0x41112e`, branch displacement) | 63 preserved |
| Shared copy with `" - "` plus status-1 call order; nested `exists()` form | 2647/2661 | `+411` (literal relocation) | 63 preserved |
| Empty guest string plus status-1 call order | 2647/2661 | `+1442` (`0x41153a`, branch displacement) | 63 preserved |

The two status-1 call-order variants are the same effective outcome. They move `replaceBadCharacters(fname, '_')` before the `action == -1` test, matching the original order at `0x4115bb..0x4115d8`, and add four bytes. The first branch at `0x41112e` then reaches the same function-relative target `+0x7f8` as the original. The nested `if (exists(fpath)) { if (!my_alert(...)) ... }` spelling produces no additional output change.

With both the empty guest string and status-1 call order, the first remaining effective mismatch is the branch at `0x411538`: original target `+0x884`, candidate target `+0x880`. `do_replay_menu` is still `DIFFER`, 14 bytes short, with no strict function match. This is a new CFG/layout investigation point; it does not establish body equality or a layout-only classification.

## Artifacts

- Shared-copy baseline: `main.c` from the earlier isolated research directory; result `build/tu-context/game-main/research-20260924-do-replay-menu-shared-copy/comparison.json`.
- Status-1 order variant: [`main-status1-call-order.c`](main-status1-call-order.c); receipt `docs/attempts/tu-context/game-main/research-do-replay-residual-status1-call-order.json`; strict comparison `build/tu-context/game-main/research-do-replay-residual-status1-call-order/comparison.json`.
- Nested overwrite variant: [`main-status1-exists-nested.c`](main-status1-exists-nested.c); receipt `docs/attempts/tu-context/game-main/research-do-replay-residual-status1-exists-nested.json`; strict comparison `build/tu-context/game-main/research-do-replay-residual-status1-exists-nested/comparison.json`.
- Empty guest variant: [`main-empty-guest.c`](main-empty-guest.c); receipt `docs/attempts/tu-context/game-main/research-do-replay-residual-empty-guest.json`; strict comparison `build/tu-context/game-main/research-do-replay-residual-empty-guest/comparison.json`.
- Combined variant: [`main-empty-guest-status1-order.c`](main-empty-guest-status1-order.c); receipt `docs/attempts/tu-context/game-main/research-do-replay-residual-empty-guest-status1-order.json`; strict comparison `build/tu-context/game-main/research-do-replay-residual-empty-guest-status1-order/comparison.json`.

## Maintained-source audit and serialized-gate input

The complete retained body [`do_replay_menu.c`](do_replay_menu.c) was diffed against the current maintained definition. It differs in exactly two places:

1. The guest source passed to `strcpy` is `""`. At `0x41112c`, the non-guest branch goes to `0x411790` and returns to the shared call setup at `0x411137`; the guest path loads the aligned pointer `0x4d4bb3` and both reach `_strcpy` at `0x41113e`. The pointer's original byte is NUL, so the source expression is consistent with the observed call and content. Its anonymous `.rdata` owner remains unknown.
2. `replaceBadCharacters(fname, '_')` runs immediately after `get_string` and before `action == -1` is tested. At `0x4115bb`, the original saves the result from EAX into EDI, calls `_replaceBadCharacters` at `0x4115cd`, then increments/tests EDI at `0x4115d2..0x4115d8`. This supports the call order and shows the result is preserved across that call.

The remaining body text matches maintained source. The raw current-order/no-prototypes TU_CONTEXT spec is [`tu-context-spec.json`](tu-context-spec.json). Its canonical-source body-overlay probe compiled with 63 exact peers before and after and no changed unchanged-body effective bytes. The function remains `DIFFER`, 2647/2661 bytes; its first mismatch is the later branch at `0x411538` (original target `+0x884`, candidate `+0x880`).

This source correction can proceed through the serialized TU_CONTEXT gate without claiming layout-only equality. The gate must preserve exact peers and proven data owners and it does not grant a `FUNCTION_MATCH`; the current comparator still reports `DIFFER`, and the anonymous literal owner remains unproven. No production plan, source edit, recovery status change, or function-match claim was made.
