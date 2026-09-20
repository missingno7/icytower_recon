# `update_player` recovery map

`update_player` is the player-CU routine at `0x418740..0x4189cb` (651 bytes).
It takes `Tplayer *p` and owns player integration after input but before the
main-CU collision dispatch.

The oracle first clamps vertical speed against a collision-mode indexed table
at `0x4bdb80`, then clamps horizontal speed relative to the same mode before
adding `sx` and `sy` to `x` and `y`. It limits the vertical position using the
constants referenced at `0x4d713c` and `0x4d7140`, dampens horizontal velocity
at either boundary, and sets the edge-drawing offset to `+20` or `-20` when a
boundary clamp coincides with a particular horizontal threshold.

For nonzero status it adds gravity from the demo's mode-indexed table at
`0x4bdba8` plus the base at `0x4d7158`. A jumping player (`status == 1`)
changes to falling (`status == 2`) when the resulting vertical speed reaches
zero. Recovery must preserve this ordering: clamp, integrate, position clamp,
then gravity/status transition. The collision-mode table values and exact
floating constants remain the outstanding evidence needed for a source body.
