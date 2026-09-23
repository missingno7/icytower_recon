# Output indexing probe

Hypothesis: the original DWARF reports inline `pOutBuffer` in `%edx`, while the retained helper-call candidate introduces a saved copy of that pointer at IRA (`insn 366`) and a 16-byte frame increase. Both observed `extractLine` calls in `extractHTTPResponse` pass a 1024-byte `linebuf`. Replace post-incremented output pointer writes with indices derived from `iOutSize`, and write the final sentinel at byte 1023. This preserves the 1024-byte call behavior and tests whether the pointer pseudo / live range drives the spill.

This is an isolated diagnostic hypothesis, not a historical source claim. The probe uses a full retained TU overlay and the current declaration/order context.
