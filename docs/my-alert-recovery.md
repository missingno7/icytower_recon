# `my_alert` recovery map

`my_alert` is the unresolved main-CU modal routine at `0x40cd68..0x40d452`
(1,770 bytes). DWARF fixes its source declaration at `main.c:464` and its
four-argument boundary:

```c
int my_alert(char *func, char *txt, int choice, int enter_hint);
```

It is not a direct call to Allegro's six-argument `alert`. The first two
arguments are the displayed label and message; `choice` determines whether
the modal renders and selects between two answer images, while `enter_hint`
selects its input/exit path. Its locals are `status`, `done`, and `w`.

The oracle body first measures the non-null strings with the loaded primary
font. It records black and white colours, applies a translucent drawing mode,
fills the active screen, and then copies that screen to the `swap_screen`
back buffer. It draws the label centered at `(320, 135)` and, when present,
the message centered at `(320, 180)` using the secondary loaded font.

The interaction phase is source-level control polling. Before accepting an
answer it drains both `ctrl` and the embedded menu control at
`menu_params.ctrl`; it then clears the keyboard buffer. The modal polls both
controls every frame, debounces held input with `rest(2)`, switches the
answer selection on left/right, and accepts fire or enter. It calls `vsync`
while rendering the selected/unselected answer assets. The exit path redraws
the preserved back buffer before returning the selected `status`.

The initial disassembly establishes the direct Allegro calls and dimensions:
`text_length`, `makecol`, `set_trans_blender`, `drawing_mode`, `solid_mode`,
`blit`, `textprintf_centre_ex`, `textout_centre_ex`, `clear_keybuf`, `vsync`,
and `rest`; control calls are `poll_control`, `is_any`, `is_left`,
`is_right`, `is_fire`, and `is_enter`. Recover the remaining answer-asset
indices and return mapping from the complete `0x40d0d4..0x40d452` control
flow before emitting a C body. A placeholder or redirect to Allegro's alert
API is not acceptable.
