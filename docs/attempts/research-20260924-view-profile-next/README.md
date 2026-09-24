# `view_profile` key-space control audit (2026-09-24)

Research only. No maintained source, generated status, or production ledger was edited. The complete retained candidate is `key-space.c`; its raw `TU_CONTEXT` spec is `key-space-tu-context-spec.json`. It changes only the `view_profile` definition in `src/profile.c`. It uses current definition order and no generated prototypes. The spec is prepared for serialized TU-context acceptance; no plan/begin/apply/check/promote command was run.

## Historical CFG and key operand

The original function starts at `0x419aec`. Its relevant disassembly is:

```text
0x419afb  call clear_keybuf
0x419b00  jmp  0x419b19                 ; initial condition check
0x419b04  call get_controls             ; poll body begins at +0x18
0x419b09  mov  $0, 4(%esp)
0x419b11  mov  %eax, (%esp)
0x419b14  call poll_control
0x419b19  call get_controls             ; condition begins at +0x2d
0x419b1e  mov  %eax, (%esp)
0x419b21  call is_any
0x419b26  test %eax, %eax
0x419b28  jne  0x419b04                 ; true -> poll body
0x419b2a  mov  0x5069d3, %al
0x419b2f  test %al, %al
0x419b31  jne  0x419b04                 ; true -> poll body
0x419b33  call clear_keybuf             ; both conditions false -> exit
```

This is a pre-tested `while` loop: after the initial `clear_keybuf`, execution jumps to the condition before the first poll. The controls test and key-byte test both branch to the poll body. Therefore the historically supported source form is:

```c
while (is_any(get_controls()) || key[KEY_SPACE])
    poll_control(get_controls(), 0);
```

A `do ... while` candidate is retained as a negative control in `key-space-do-while.c`; it polls once before checking either condition and contradicts the original initial jump to the condition.

`evidence/census/globals.json` records the Allegro `key` definition in `C:/Lib/allegro4/src/keyboard.c` at `0x506988` (DIE 301341). Its referenced type DIE 301359 is `DW_TAG_volatile_type` wrapping a `char` array. `KEY_SPACE` is 75, so `0x506988 + 75 = 0x5069d3`, exactly the original absolute byte operand.

The fresh retained `while` probe emits `_key + 75` at COFF `.text` section offset 4419 / `view_profile` offset +63. The verifier resolves that named-symbol relocation to decimal `5269971` (`0x5069d3`) and independently reports equality with the original value. This verifies the candidate's address operand without using the EXE as a compilation input.

## Full-TU receipt and ownership

The current-order/no-prototype full-TU probe is `build/tu-context/game-profile/research-20260924-view-profile-next-keyspace/comparison.json`. It compiles successfully and reports `view_profile` as `DIFFER`, 2168/2249 bytes, first mismatch +115. All 11 existing exact profile peers remain exact; no peers are gained or lost. The whole text contribution is unequal. The verifier accepts the same seven proven initialized-data owners as the baseline (`jcLabels`, `rankLables`, `rankFloors`, `rankCombos`, `rankCCCs`, `rankNMLs`, and `comboNames`), with no rejected owners or common allocations. The new external `_key` symbol and its relocation are inventoried.

Two `view_profile` `.rdata` relocations remain unresolved as owners at historical offsets +1222 and +1625. The full CU comparison also retains its pre-existing unresolved section-relative `.rdata` relocation set. This candidate does not resolve those owners and does not claim function, object, or CU equality. It adds the historically observed control condition and preserves every proven owner.

## Prepared raw transaction

`key-space-tu-context-spec.json` names only `view_profile`'s complete retained body. It records the initial CFG, absolute operand, Allegro symbol/type evidence, exact-peer preservation, proven-owner preservation, and remaining owner uncertainty. It is ready for `python tools/tu_context_task.py plan <name> <spec>` when serialized acceptance is authorized. Plan was intentionally not run because it writes a generated task under `docs/current/tu-context-tasks/`.

The key-space candidate remains `DIFFER`; its remaining +115 mismatch is the inlined Allegro `draw_sprite` dispatch with the already-traced equivalent slow/ordinary successors and different physical block offsets. No size target or unsupported follow-on body edits were used.
