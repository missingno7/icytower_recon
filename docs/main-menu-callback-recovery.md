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
