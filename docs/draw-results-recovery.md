# `draw_results` recovery

`draw_results` spans `0x4076c0..0x407a07` (839 bytes) in `main.c`. The
recovered candidate is `CODEGEN_SIMILAR`: it has the original 839-byte extent,
all instructions match after masking relocations, and all named-symbol and
unique-literal relocations resolve to their oracle values. The only remaining
unproven relocation addresses the file-local category table through its object
section base.

The source reproduces the three displayed categories (`Score`, `Floor`, and
`Best Combo`), their datafile fonts and markers, the optional personal-best
and qualification icons, and the original layout derived from DWARF lines
3359--3401. It keeps the local five-entry category table so the remaining
section-relative relocation remains explicit rather than being hidden behind
an absolute address.
