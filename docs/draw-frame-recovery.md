# `draw_frame` recovery map

`draw_frame` spans `0x40929c..0x40b3e4` (8,518 bytes) in `main.c`. It is the
only remaining direct renderer dependency in the recovered-game link.

Oracle call order establishes phases: camera/background blits and random
variation; map and player sprite virtual draws; score and HUD text; clipping
and formatted debug/status overlays; reward presentation through `draw_reward`;
then final compositing and control-sensitive overlays. It uses Allegro virtual
methods for bitmap drawing as well as `blit`, `textout_ex`, `textprintf_ex`,
`textprintf_centre_ex`, `text_length`, `set_clip_rect`, `makecol`, `sprintf`,
and `strcpy`.

Recovery must retain its rendering phases and shared game state; a blank or
synthetic frame is not a valid replacement. The function should be recovered
in source slices, beginning with the camera/background and floor/player draw
loops before HUD and debug overlays.

DWARF source anchors divide the body: entry is line 2490; the first sprite
phase is line 2562; map/HUD work reaches line 2822; reward rendering anchors
at line 2722; compositing is at line 2707; and control-sensitive presentation
continues through line 2780. These anchors intentionally overlap in address
order because the original compiler interleaves branches from the same source
regions.
