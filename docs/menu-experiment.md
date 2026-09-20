# Partial `menu.c` experiment

The recovered slider and selection accessors, plus `reset_menu`, are
byte-exact at `-O2`.
`set_slider_value` accepts only inclusive slider bounds, while
`set_selection_value` accepts selection indices in the half-open range from
zero to `max`. `reset_menu` clears each entry's selected bit through the
byte-sign sentinel, selects `sel_pos`, and refreshes the cached font height.
The remaining menu rendering and input functions are not yet recovered; this
target uses only reconstructed source and the original executable as a
comparison oracle.

`build_menu_string` is recovered from its original DWARF local types and
static control flow. Both key-label temporaries are `char[32]`; the separate
heading-asset branches are required by the historical flag tests. The result
is the original 415-byte body with no non-relocation byte difference.

`update_game_menu` now keeps the historical F1 jump inside the primary-control
path: with no primary control it leaves the selected entry unchanged. It finds
the selected entry through the terminating flag, draws the current page,
accepts primary and alternate control navigation, and evaluates up and down
independently as the original does. It updates the selected bit and movement
sound, then returns the selected/left/right action with the entry data. The
candidate is 518 bytes against the historical 583 and is recorded as
`DIFFER`.

draw_menu now reconstructs the historical rendering loop from its independent
DWARF types and original control flow. It advances rows by `font_height - 12`,
formats every entry, renders key bindings in two columns, draws the selection
bullet, and renders the three-piece and movable slider assets through Allegro's
historical inline `draw_sprite` dispatch. The movable asset is one row below
the text baseline (`y + h`), rather than the incorrect `y + y` placeholder.
The candidate is 956 bytes against
the historical 1,118-byte function and is recorded as `DIFFER`; its shorter
code results from equivalent compiler register allocation and branch folding.

handle_menu now reconstructs the menu event loop. It resets the selected entry,
draws through an optional callback, debounces both controls, dispatches nested
menus, adjusts sliders and each selection type within its historical bounds,
toggles boolean options, captures control keys, and handles profile actions.
The original return-code table and menu data tables establish these actions.
The candidate is 1,034 bytes against the historical 1,120-byte function and
is recorded as `DIFFER`.

`key_to_str` is reconstructed from its complete 108-case scan-code dispatch
at `0x416a9c`. It copies the original key labels and uses `"undefined"` for
all unlisted scan codes; scan code 18 intentionally produces lower-case `"r"`,
and code 105 is the separate semicolon case. The historical cases use numeric
scan codes so their observed 1.5.1 layout remains independent of the installed
Allegro headers.
