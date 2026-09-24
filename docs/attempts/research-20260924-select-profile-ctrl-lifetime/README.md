# select_profile control parameter lifetime probe

Question: can an explicit entry-saved local alias for the historically register-resident `ctrl` parameter change the compiler allocation at the first mismatch?

Evidence: original prologue stores `[ebp+0x14]` in ESI at function offset +9 before font setup. The best retained source-backed candidate has the same 0x16c frame and exact switch/UI paths, but reloads ctrl from `[ebp+0x14]` for `poll_control` and `is_any`; historical DWARF shows the parameter has a register location during the body, while candidate DWARF leaves it stack-based.

Probe changes only the five helper-call arguments to a function-scope `Tcontrol *cached_ctrl = ctrl` initialized at entry. Alias type is the exact `Tcontrol` type used by helper prototypes. This is a compiler-response probe; it cannot grant a match.
