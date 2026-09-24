# Frozen plan before new compiles

Source SHA-256: 2a12d635e2fbf74bd0388869fd303a6622b9ee31305e110bc7cfaa41d4c05044.
Ledger SHA-256: 1fdd09a43371e21578c7ed5eb6d9c7f16f3cc00ebe4f796f76ba83a106c01a56.

The 14 removable legacy prototype blocks are split into early E (blocks 2-8)
and late L (blocks 9-15), seven blocks each. Keep legacy block 1 and historical
block 16 in all corners. A blanks neither, B blanks E, C blanks L, D blanks
both. Replace each declaration line with equal-length spaces so all retained
token byte offsets, lines, and columns are invariant. Compile historical-order
whole TUs with locked tdm-2 and no newly generated prototypes.

Before reusing A/D receipts, check current source and ledger hashes, generated
overlay parity, compiler/order flags, 64/82 exact peers, and no implicit calls.
For each corner record the first parser-loop PHI sequence, optimized
i/check/replay_path order, effective init_game/play identities,
target-to-oracle first mismatch and byte/relocation residue, and exact-peer
gains/losses. Verify pass dumps are emission-neutral.

If B=D and C=A, E controls the observed class; the reverse points to L.
If B=C=A but D differs, the groups interact or cross a threshold. If B=C=D,
either group suffices. Other classes demonstrate positional/nonmonotonic
behavior, not a license for a count sweep.

The recovery-facing discriminator is the historical init_game +14 register
mismatch: original loads argv into ESI, candidate loads argc. Track
play's +8 historical mismatch and every exact peer separately. If B/C only
reorder candidate instructions near +0x248 while these oracle residues and
strict peers remain, close this count branch. Historical declaration evidence
is required before selecting any prototype count for production.
