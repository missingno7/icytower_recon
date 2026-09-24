# force_create_profile residual: register/context finding

Date: 2026-09-24
Baseline: HEAD `520e4a27`
Scope: read-only inspection of the current focused card, strict report, accepted object disassembly, and DWARF/line data. No source, tools, ledger, current-state, or compiler inputs were edited. No candidate overlays or locked-compiler builds were run in this residual pass.

## Exact current result

The strict main CU report has **64 FUNCTION_MATCH peers out of 82**. `force_create_profile` remains `DIFFER`: 1537 candidate bytes vs 1538 historical bytes, first byte difference at function offset `0x15`, 288 differing bytes. Diagnostic sequence alignment reports 292 original vs 291 candidate instructions and 28 changed groups. Branch count is 19 on both sides. This does not change the proof state.

See `focused-evidence.json` for the focused-card evidence captured at this baseline and source hashes.

## Aligned code and calls

The first clearly instruction-selection difference is inside the inline Allegro `draw_sprite` expansion at function offset `0x98` (historical line table maps the inline to `draw.inl:238`, from `main.c:5670`). The original loads the bitmap field through `%edx` and lays out the two bitmap arguments using `%eax`/`%edx` in one order; candidate accesses the corresponding field through `%eax` and lays the arguments in the reverse register order. Both issue the same indirect call through vtable slot `0x44`. This is a live-register/context difference within the inline helper, not evidence of a missing edge.

All named direct call edges through the setup/render path resolve to the same named functions. The three unequal tail transfers (`my_alert`, `syncOptionsFromProfile`, `my_alert`) occur in the unaligned tail where instruction alignment is already lost; their fixed-offset comparisons are not valid target evidence.

## Relocations

The 11 aligned screen accesses are candidate `_screen` relocations at function offsets beginning 237, 305, 373, etc. Each aligns to the same five-byte `mov moffs32,%eax` instruction shape, but the candidate object resolver yields `0x4dda8c` while the original operand window contains `0x4dd194`. The focused evidence classifies this as `ALIGNED_OPERAND` and explicitly says the original fixed-offset value is diagnostic only; it is not an independent ownership/target binding. Treat the address discrepancy as a data/layout lead, not as a proven source-body defect.

Six `.rdata` references and the later `_screen`, `_profile`, `_makecol`, `_load_profile`, and `_create_profile` operand windows are `UNALIGNED_OR_UNTYPED`/`UNALIGNED_BYTE_WINDOW`. They do not support a local edit while the tail is unaligned.

## DWARF and line table

Historical `res` is a child of the loop lexical range list (`0xc20`), with location-list ranges in EAX. The nested historical child range (`0xc40`) contains the inline `draw_sprite` ranges, not a lexical scope for the outer `res >= -1` condition. Candidate DWARF likewise keeps `res` within the loop block, records the `draw_sprite` inline DIE, and has no added lexical block for the outer guard. The outer conditional's topology therefore supplies no basis for changing scope or variable lifetime.

Historical line rows distinguish the main source call and the inline Allegro line (`main.c:5670` then `draw.inl:238`); the candidate line table maps the equivalent inline draw to the corresponding current source call. There is no row or lexical-scope anomaly to repair.

## Probe decision and blocker

**No new causal probe was run.** The inspected evidence rules out the outer-scope hypothesis and confirms the expected inline call shape. Remaining ways to perturb EAX/EDX would add an unobserved temporary, change local lifetime/declaration topology, force argument evaluation with a non-historical construct, or guess at register allocation. None is supported by the original call/CFG/DWARF evidence. This pass therefore stops before a speculative source variation; the existing 64 exact peers are untouched.

## Next useful experiment

Recover stronger source/compiler evidence for the original `draw_sprite` call context (historical call-site source or an original compiler dump showing its RTL/register allocation). If that evidence establishes an omitted lifetime/use or different surrounding expression, test only that variation in a uniquely named isolated overlay under the locked compiler and compare the call/branch graph plus all 64 exact peers. Without it, the one-register-order difference is not a causal source hypothesis.
