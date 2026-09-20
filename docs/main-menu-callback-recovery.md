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
