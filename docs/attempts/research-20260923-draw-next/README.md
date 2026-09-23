# `draw_frame` fifth frame-zero height load trace

Scope: isolated research only. No maintained source, generated current state, or recovery ledger was changed. The current focused card is `docs/current/functions/main/draw_frame.json`; the retained complete function is `docs/attempts/game-main/draw_frame-merged.c`. Prior status/pose-independent findings were read before this trace.

## Original predecessor trace

The five accesses are all attributed to historical `main.c:2606` by `evidence/census/line-mappings.json`. The matching disassembly instruction starts and function offsets are:

| Original instruction | Function offset | Incoming path | `p_im` DWARF range |
|---|---:|---|---|
| `0x409a20` | 1924 | positive speed/reset predecessor; height is read before `%esi` is assigned 1 at `0x409a3c` | `%esi` range `0x4099dd–0x409a46` |
| `0x409ba7` | 2315 | status-zero narrow-speed shortcut, leading directly to edge handling | no listed `p_im` location covers the instruction itself; location resumes at `0x409bb5` |
| `0x409cd3` | 2615 | status/pose predecessor after the frame reset; joins at `0x409ceb`/`0x409cf8` | `%esi` range `0x409c9d–0x409d06` |
| `0x409fdb` | 3391 | negative-speed/reset predecessor; `%esi` is set to 1 at `0x409fef` | `%esi` range `0x409fc1–0x409ff4` |
| `0x40aa3f` | 6051 | frame-cap continuation at `0x40aa26`; both `frame <= 3` and reset cases reach it | `%esi` range `0x40aa26–0x40aa58`; `%esi` is set to 1 at `0x40aa4e`, after the height calculation |

At the fifth predecessor the loaded `p_im` value is live in `%esi`; it is overwritten after the `1 - custom.frame[0]->h` sequence. This corrects the earlier tentative reading that the value was not live there. The distinction supported by the assembly is statement ordering: the cap-route height read precedes its final `p_im=1` write. The other two explicit `p_im=1` writes are after their respective height reads at `0x409a3c` and `0x409fef`.

The complete original source-line markers are exactly `0x409a20`, `0x409bad`, `0x409cd9`, `0x409fdb`, and `0x40aa3f`; the middle addresses are line-table markers inside the corresponding load sequences. Original instruction windows are retained in `original-window1.txt` and `original-window2.txt`.

## Isolated ordering probe

A research copy moved the cap-route `customFrame = custom.frame[0]; oy = 1 - customFrame->h;` before `p_im = 1` and kept a separate copy on the other predecessor. This tested whether the original cap-path write/read ordering and predecessor split were lost by the retained body. It was compiled with locked TDM-GCC 4.4.1 (`-O2 -g -mfpmath=387`) in current TU order, with both retained `draw_frame` and retained `play`, using `--no-prototypes`-equivalent source context.

The probe produced `draw_frame` at 8203 bytes, `DIFFER`, first mismatch offset 8 (`0xcc` candidate versus `0xdc` original), and the same four direct `_custom + 0x80` height loads as the retained baseline. Its `draw_frame` instruction bytes compare exactly equal to the retained status-zero-sign baseline, so this is a deduplicated effective outcome, not a new compiler emission. The TU has 63 exact functions in this current-order probe. No candidate is promoted.

The source and build artifacts are `draw-frame-cap-height-before-pim.c`, `run_height_probe.py`, `height-before-pim/`, `height-before-pim.comparison.json`, and `height-before-pim-draw-frame.txt`. Object SHA-256: `ef05fdf2f27c27fff12528d35a37bf95bb1a0b38a5a850a07b53fccd3906ff5e`.

## Handoff

The five-versus-four gap is now localized: the original extra read is the cap-route copy at `0x40aa3f`, not another status/speed spelling of one of the earlier four. The directly evidenced ordering change compiles to the existing four-load outcome. Stop local spelling changes here; a next useful investigation would need historical source/CFG evidence explaining why GCC preserves a separate cap-route copy, or compiler/tree dump evidence for the transformation that merges it. Existing status, speed, and cap spelling trials remain excluded.
