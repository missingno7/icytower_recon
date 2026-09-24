# force_create_profile residual refresh (2026-09-24)

Isolated diagnostic refresh after the accepted sentinel CFG correction. No maintained source, generated state, or recovery ledger was edited. The probe compiled the current authentic whole `game-main` TU in historical definition order with `--no-prototypes`, under locked TDM-2 / GCC 4.4.1. A focused FAST check was also run against the maintained source. No source variant was compiled in this branch because the evidence supplied no causal, historically supported variation that predicted a target residue change.

## Refreshed strict context

The whole-TU control `force-profile-residue-control-20260924` compiled successfully and preserved **64/82 exact functions**, with no gains or losses. `force_create_profile` remains `DIFFER`, 1537 candidate bytes / 1538 historical bytes. Historical and candidate definition positions are both 61. The fresh FAST report agrees: first byte difference at function offset `+0x15`, 288 differing bytes, 24 relocation mismatches and 9 unaligned transfer/layout differences. The exact whole-TU comparison remains the authority for peers; no recovery credit is claimed here.

## Residue and original evidence

The first aligned source-level instruction-selection mismatch is at `+0x98` inside the inline Allegro `draw_sprite` expansion. Original bytes load the field through `%edx` (`mov 0x1c(%edx),%ecx`); candidate uses `%eax` (`mov 0x1c(%eax),%ecx`). The inline call maps to original `draw.inl:238` (original line row `0x40d4ec`), between the `main.c` call-site rows. Its indirect vtable call shape is otherwise the same. The initial `+0x15` mismatch is a branch displacement in a function whose total size differs by one byte; after alignment is lost, later fixed-offset branch/call windows are not reliable source residues.

The original DIE graph places `res` (declared at historical line 5683) in loop lexical range `0xc20`; the nested range `0xc40` covers inlined draw operations. There is no lexical block for the outer `res >= -1` guard. The current body already scopes `res` and `buf` inside the loop. The refreshed evidence therefore rejects moving `res` into a new lexical scope as a supported hypothesis. Original line rows show the expected call/inlining mapping, with no line-table anomaly to repair.

The aligned `_screen` operand windows at `+0xed`, `+0x131`, `+0x175`, and subsequent repeated sites resolve to candidate `_screen` address `0x4dda8c`, while the original operand bytes contain `0x4dd194`. The comparator marks these as aligned operands but explicitly does not establish independent ownership/target binding from original raw bytes. This is a data/layout lead, not a body edit authorization. Remaining relocation and transfer residues occur after instruction alignment has diverged and remain untyped/unaligned.

## Prediction and stop decision

Prediction recorded before any new source compile: a source/DWARF scope relocation has no basis in the original DIE structure and would not discriminate the `%eax`/`%edx` allocation at the inline call. A source spelling change or temporary introduced solely to force those registers would be speculative; no compile was run for it. The existing sentinel correction remains useful CFG/source work but did not change the next recovery decision for the register/layout residue. Close this local sentinel-scope branch and seek original call-site source or stronger compiler-context evidence before another `force_create_profile` experiment.

## Artifacts

- `control-context.json`: fresh historical-order whole-TU context receipt.
- `fresh-focused.json`: refreshed FAST target report, including aligned instruction windows and relocation classes.
- `identity.json`: source/card/receipt hashes and exact status summary.
- Prior CFG evidence: `docs/attempts/research-20260924-force-profile-next-20260924/README.md`.
- Earlier DWARF/line and register-context analysis: `docs/attempts/research-20260924-force-profile-residual-register-context/README.md` and `focused-evidence.json`.
