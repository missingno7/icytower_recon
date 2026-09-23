# `handle_player_input`: IRA and predecessor-context follow-up — 2026-09-24

## Scope and current baseline

Diagnostic only; no maintained source, generated current state, recovery ledger, or status changed. A clean compiler-probe baseline was saved under the isolated diagnostic alias `game-main-hpi-causal` to avoid touching the earlier compiler-probe output directory. It compiles the maintained complete `game-main` TU with TDM-2 and captures all RTL passes.

Baseline: `handle_player_input` is 728 bytes, DIFFER at +475, with 63/82 strict function matches and no whole-text equality. `new_game` and `run_demo` are both FUNCTION_MATCH (1139 and 159 bytes). The clean focused IRA dump is `build/compiler-evidence/game-main-hpi-causal/handle_player_input/baseline/focus/probe.c.172r.ira`; its full receipt is `docs/attempts/compiler-context/game-main-hpi-causal/handle_player_input.json`.

## Original CFG and GCC allocation evidence

The original branch at +473 tests the recorded `key_flags` high bit. Its taken branch jumps to +592 and later bypasses the recording update, while the fallthrough path reaches the `control->flags & 0x93` computation at historical source line 2420 (around +506). The `flags` DIE is an `unsigned char` in a nested lexical block, with register location entries beginning after that branch. This supports the original lifetime/order already recorded in `README.md`.

The maintained source computes `flags` before testing that high bit. At the current GCC `128r.expand`/`172r.ira` state, the flags load is therefore an input to the recording block before the key-flags read. IRA assigns the candidate flags pseudo to hard register EDI; the emitted candidate starts +475 with `movzbl 0x20(%ebx),%edi`. It then loads the record key flags into CL and tests that value. The historical code starts +475 by loading `demo` and the record key flags, and only loads the control flags after the high-bit branch. The +475 difference is thus primarily the source-level evaluation order and resulting liveness/register allocation, rather than an unexplained register swap.

## Predecessor-context boundary

The current cgraph emission predecessor is `draw_frame`, at historical and candidate position 42; it is not exact. Two already-retained, source-backed full-TU `draw_frame` probes changed that predecessor while preserving the established exact set (63/82, no gains/losses; `new_game` and `run_demo` stayed exact). Their outcomes are recorded in `docs/attempts/research-20260923-draw-frame-csa-context/README.md` and receipts `csa-context-speed-path-height-20260923.json` / `csa-context-live-speed-height-20260923.json`. Both `handle_player_input` results group to the same effective identity `c81b0e2befae0d0a`, 728 bytes, first mismatch +475. The separate scope-only flags probe also collapses with the current control. Thus these exact-neighbor-preserving source/context changes do not alter the target's allocation or first mismatch.

One isolated `compiler_probe.py --omit-peer draw_frame` diagnostic was also run to measure the immediate predecessor's influence. It moves the target's first mismatch to +21 and raises its differing-byte count to 60, but drops the exact count from 63 to 59; the lost functions are `line_alert`, `open_web_browser`, `show_instructions`, and `stopGameMusic`. `new_game` and `run_demo` remain exact. This confirms that removing the predecessor can perturb the target's compiler allocation, but it violates the required exact-neighbor boundary and is not a candidate or useful acceptance path. Its output is retained at `docs/attempts/compiler-context/game-main/handle_player_input.json` and `build/compiler-evidence/game-main/handle_player_input/omit-draw_frame/`.

## Outcome and blocker

The causal split is now bounded: GCC/TU context can affect this function when the actual emission predecessor is removed, but source-backed predecessor variations that preserve all 63 exact functions leave `handle_player_input` byte-identical after same-CU transfer normalization. The actionable +475 difference remains the early flags computation in the maintained body versus the original CFG's post-branch computation. Existing move-into-else variants already make the correct order but grow the function to 760 bytes and lose exact neighbors; do not repeat their syntax variants or promote them. A next useful step requires new historical source/tree evidence or a different source-backed CFG form that preserves the 63-function set and the original three-register prologue.
