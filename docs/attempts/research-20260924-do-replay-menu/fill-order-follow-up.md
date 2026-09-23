# `do_replay_menu`: follow-up on the first `fname` fill

Date: 2026-09-24
Context: current-order `--no-prototypes` full-TU GCC 4.4.1 overlays; no maintained source or recovery edits.

## Historical anchor

The corrected play-again/exit body restores the historical `0x185c` frame and moves the first mismatch to function offset `+364` (`0x16c`), historical VA `0x411104`. Historical line mapping identifies this as source line 5508, the first `fname` fill. The adjacent rows put the preceding log call at line 5506 and the `fname[511] = 0` terminator at line 5509.

The original instruction order is:

```asm
+364  b0 20                 mov $0x20,%al
+366  b9 ff 01 00 00        mov $0x1ff,%ecx
+371  89 df                 mov %ebx,%edi
+373  f3 aa                 rep stos %al,%es:(%edi)
+375  c6 85 e8 fd ff ff 00  movb $0x0,-0x218(%ebp)
```

This is `memset(fname, ' ', 511)` followed by the terminator. The historical source-level operation sequence is preserved in the overlay. The two independent setup loads differ in order: original loads the fill byte before the count; corrected candidates load the count before the byte. The subsequent destination setup, `rep stos`, and terminator align. At a later comment fill, the original instead loads count before byte, so there is no uniform TU-wide ordering rule to recover from these sites.

## Candidate comparison and probes

The corrected scoped-exit body is the baseline for these probes. All use the whole TU, current source order, and `--no-prototypes`; all compiled, stayed 2643 bytes versus historical 2661, first differed at `+364` (`candidate b9`, historical `b0`), and retained 63/82 exact functions with no gains or losses.

| Probe | Fill expression | Effective output | Result |
|---|---|---|---|
| `luna-drm-scoped-exit-control-20260924` | `memset(fname, ' ', 511)` | `9c5e2914f8b97f6e` | baseline |
| `luna-drm-fill-decimal-32-20260924` | `memset(fname, 32, 511)` | `9c5e2914f8b97f6e` | collapsed to baseline |
| `luna-drm-fill-sizeof-count-20260924` | `memset(fname, ' ', sizeof(fname)-1)` | `9c5e2914f8b97f6e` | collapsed to baseline |
| `luna-drm-rank-predecessor-context-20260924` | baseline body plus evidence-backed predecessor context | `2cfea875896db232` | distinct context output |

The predecessor-context overlay changes a later local reload at `+379` from `%edx` to `%ecx` and consequently changes following encodings/branches, but it leaves the `+364..+378` fill sequence unchanged. The two semantic-preserving fill spellings also leave it unchanged. Thus the observed fill ordering is not explained by these equivalent argument spellings or by the tested predecessor context.

## Outcome

The first mismatch is a local instruction-scheduling/register-allocation difference between independent constant loads. Historical line/CFG evidence identifies the operation but does not support a different source operation or sequencing. The tested, source-grounded spellings converge to one effective instruction/relocation output; no strict candidate was found. Do not infer a source-level dependency solely to swap these independent loads. Further work needs a concrete compiler-context or source-structure explanation for this scheduling choice.

Receipts: `build/tu-context/game-main/luna-drm-{scoped-exit-control,fill-decimal-32,fill-sizeof-count,rank-predecessor-context}-20260924/comparison.json`. Effective-output grouping: `python tools/effective_outcomes.py game-main do_replay_menu --pattern 'luna-drm-*-20260924.json' --compact`.

Maintained-file integrity check after probes: `src/main.c` SHA-256 `259aa5890bda71a2bd6488c03166d961f4f083b2dbf0074475c6ee3690d40942`; `src/recovery.json` SHA-256 `2f0710c753742dda1de1bb624cce6fa378ba14c6a205adb9e3552c67bbd8f360`.
