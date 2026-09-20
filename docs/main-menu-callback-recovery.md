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

The callback's persistent scroller state is now emitted by `main.c` from
DWARF and the pinned executable-data asset records: `scroller_greetings[156]`
and `init_string[7]` reproduce their manifest SHA-256 values, and
`greeting_scroller` is a typed `Tscroller` BSS object. The callback now has a
source-level lifecycle body using this state: ad/input handling, backdrop and
head rendering, greeting scrolling, guest/profile presentation, slider and
selection synchronization, and menu-music adjustment. Its pinned-toolchain
candidate is 2,571 bytes against the 3,741-byte oracle and remains `DIFFER`;
the remaining gap is historical visual and branch layout recovery.

The callback's two internal persistent scalars are now represented separately:
`face` and `count` correspond to DWARF addresses `0x4dd31c` and `0x4dd318`.
The character-loading callback has its own function-static `count` at
`0x4dd330`; keeping that counter at function scope prevents character discovery
from sharing main-menu animation state.

The entry block is now decoded through its return branches. Each invocation
increments the menu `count`; when `new_rand() % 198 == 1`, it increments
`face`, wrapping `3` back to `0`. The screenshot-input branch calls
`take_screenshot(swap_screen)` and waits for its observed byte-sized input
flag to clear before returning to the resolution/ad path. The ad gate first
tests the horizontal input coordinate against the loaded bitmap's first word;
its true branch derives the vertical gate from the display-state object and
the bitmap's second word. It then preserves the mouse-button transition across
the browser launch and alert before restoring the normal cursor. The unnamed
Allegro input and display fields remain described by their oracle addresses in
the disassembly until their typed declarations are independently recovered.

The decoded line table provides the required complete phase map. Lines
5220--5228 scroll and render the welcome scroller; lines 5231--5248 choose
between the guest welcome text and the ranked-profile presentation, including
four `get_rank` rows. Lines 5255--5277 refresh music sliders and the welcome
message; lines 5282--5288 transfer the four gameplay selections; line 5293
adjusts menu music. Any implementation must include all of these phases and
the exceptional screenshot, cursor, browser, and scroller-restart edges that
branch back into them.

The direct-call map fixes the phase boundaries: `0x41010a..0x4101e7` contains
random/update/browser/alert handling; `0x410261..0x4104bf` contains backdrop,
ad, head, and blend work; `0x410598..0x41075c` drives the greeting scroller;
`0x4107df..0x410bd3` is the guest/profile rank presentation; and
`0x410c3f..0x410db6` reads menu values and adjusts music. The exceptional
cursor, screenshot, and scroller restart calls lie at `0x410e73`, `0x410e8d`,
and `0x410ea9`. These ranges are a complete call-level checklist, rather than
a substitute for recovering the callback's source body.
