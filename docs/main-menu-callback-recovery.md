# `main_menu_callback` recovery map

`main_menu_callback` spans `0x4100f8..0x410f95` (3,741 bytes) in `main.c`,
declared at source line 5136. DWARF names its renderer state as
`scroller_step`, `face`, `count`, `old_msc`, `head_bmp`, `head_shadow`,
`head`, `headX`, `headY`, and `welcomeMessage`.

The oracle contains sprite and translucent-sprite phases, two fixed-point sine
animation regions, rotation, three rectangle fills, and a final inline
`syncProfileFromOptions` region. Recovery must retain the menu music-volume
transition, animated head presentation, scroller/welcome state, and option
synchronization in ordinary source; the routine remains missing.

Its entry lines 5142--5177 are an update/poster control path: random selection,
window-resolution checks, optional browser launch, and alert fallback precede
the visual work. Rendering begins at line 5187 with backdrop blits and reaches
head bitmap/shadow construction at lines 5206--5212. These two regions must
remain coupled in the recovered callback.

The opening oracle trace resolves the poster ownership without a carrier:
`pFLDAdBitmap` is the `0x4dd30c` bitmap pointer and `pFLDAd` is the
`0x4dd310` ad descriptor. When an ad is active, the callback checks its
timestamp against the system counter, opens its URL with `open_web_browser`,
shows the existing browser alert, and restores the last mouse-button state.
The first rendering phase then blits `data[126]` to `swap_screen`, draws
`data[71]` at `(330, 280)`, and alpha-draws the optional ad bitmap at
`(0, 280)`. The head construction starts from `data[58 + face]` and the
shadow asset at `data[61]`; later animation remains to be recovered with its
fixed-point sine expressions and local lifetimes intact.

The decoded line table provides the required complete phase map. Lines
5220--5228 scroll and render the welcome scroller; lines 5231--5248 choose
between the guest welcome text and the ranked-profile presentation, including
four `get_rank` rows. Lines 5255--5277 refresh music sliders and the welcome
message; lines 5282--5288 transfer the four gameplay selections; line 5293
adjusts menu music. Any implementation must include all of these phases and
the exceptional screenshot, cursor, browser, and scroller-restart edges that
branch back into them.
