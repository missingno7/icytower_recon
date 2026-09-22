# `handle_player_input` — recorded finding (not resolved)

`handle_player_input` (`src/main.c`, currently lines 2003..2088) is 728 of 728 historical bytes
(exact size), 50 differing bytes, all in one contiguous cluster. Retained body used for
measurement: `docs/attempts/game-main/bodies/handle_player_input.c` (currently a byte-identical
copy of `src/main.c`; no fix landed). Measured via `tools/tu_context_probe.py game-main src/main.c
<label> --order historical --body handle_player_input=... --no-dumps`, labels `hpi-1` through
`hpi-6`.

## The one real difference

After filtering rebasing/relocation noise (absolute jump targets and global addresses differ
because the candidate function sits at a different address in the diagnostic overlay; those are
not real differences), exactly one genuine cluster remains: **historical offsets 469..524**
(~50 bytes), all attributable to historical source lines 2418/2420/2423/2427/2428 (the `if
(recording) { ... }` branch's inner chain that updates the replay buffer):

```c
flags=control->flags&0x93;                          /* 2420 */
if (demo->data[rec_pos].key_flags&0x80) {            /* 2418 */
    ...                                              /* 2433..2436 */
}
else if (demo->data[rec_pos].key_flags==flags)       /* 2423 */
    demo->data[rec_pos].cycle_count++;                /* 2424 */
else {
    rec_pos++;                                         /* 2427 */
    demo->data[rec_pos].key_flags=flags;                /* 2428 */
    demo->data[rec_pos].cycle_count=0;                  /* 2429 */
}
```

`function_lines --source-view 2417 2436` shows the original's instruction order precisely:

- Line 2418's test (`js 40b645`, offset 504) branches to lines 2433..2436 (offsets 609..644,
  the `key_flags&0x80` true-branch body) **before** line 2420 (`control->flags&0x93`, offsets
  506..512) ever executes.
- Line 2433..2436's body ends with `jmp 40b427` (offset 637). `40b427` is exactly offset 67 —
  the start of the `is_left(control)` check (historical line 2441), i.e. the code **after the
  entire `if (recording) {...} else {...}` statement**, completely bypassing line 2420 and the
  rest of the chain.

So `flags = control->flags & 0x93` genuinely executes on **only one path**: the `key_flags&0x80`
true-branch jumps straight past it. This is proven by the jump target, not inferred.

A second, separate register-choice symptom in the same cluster: at offset 532 the original
stores the flags value via `%dl`; our (still-unfixed) candidate uses `%cl` there. A third,
unrelated register swap sits outside this cluster entirely, at offset 327-333 (`rejump`'s test:
`%ecx` historically, `%esi` in our candidate) — noted for completeness, not investigated further.

## Three shapes ruled out by measurement, none accepted

All three reproduce the *evidenced* instruction order (`key_flags&0x80` tested before
`control->flags&0x93` is computed) but each was rejected:

1. **`flags` moved into the `else` of the first `if`, written as nested
   `if (A) {...} else { flags=...; if (B) ... else ... }`.**
   Result: 728 -> **764 bytes**. Prologue changed from `push edi; push esi; push ebx` to
   `push esi; push ebx` — one fewer callee-saved register kept live across the function.
2. **Same restructuring, written as an `else if` chain** (`else if (A) {...} else { flags=...;
   if (B) ... else ... }` — textually different from #1, semantically identical GIMPLE).
   Result: **identical regression** (728 -> 764, same 2-register prologue). Confirms the
   regression is caused by the semantic reordering itself, not surface syntax.
3. **`flags = control->flags & 0x93;` moved to directly after the closing `}` of
   `if (demo->data[rec_pos].key_flags & 0x80) {...}`, outside any `else`** (the shape
   suggested as a third option, on the theory that it avoids creating a new live-on-one-path
   arm for `flags`). **Not attempted** — ruled out by the jump-target check above before
   writing any code: since the `key_flags&0x80` branch's body unconditionally jumps past this
   point (to offset 67 / line 2441) in the original, placing `flags=...` there without an
   `else` would make our candidate compute it on **both** paths (falls through normally after
   an `if` with no `else`), which is not what the original does. Writing this shape would
   either misrepresent the original's control flow or (if GCC's DCE happened to reintroduce an
   equivalent skip) offer no real evidence either way. Per the instruction to check jump targets
   before assuming, this is recorded as ruled out rather than measured.

## Fast-reject criterion for future attempts

**Check the prologue register set before the byte count.** The original and our current
(unfixed) baseline both push `edi`, `esi`, `ebx` (three callee-saved registers). Any source
shape that changes GCC's choice of which/how many callee-saved registers to use for this
function is wrong before the byte count is even worth computing — shapes #1 and #2 above both
dropped to two registers and their byte counts (764) confirmed the rejection, but the prologue
alone would have caught it in one measurement.

## Status

Two dead ends measured and rejected (bigger, wrong prologue), one shape ruled out by jump-target
proof before implementation. `handle_player_input` remains `DIFFER`, unchanged, at 728/728 with
the same 50-byte cluster. This is the second function (after `load_character`) where the real
difference is a register-allocation/pressure decision rather than a statement the source is
missing — recorded per the coordinator's note that this class of problem now has two instances.
