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

`update_game_menu` and `draw_menu` now use the original signed-byte terminator
test for each menu entry. The entry keeps a 32-bit `flags` field, but its
termination flag is the high bit of the low byte; this reproduces the historical
`test dl,dl` input-path check and extends that exact instruction prefix to 103
bytes. The renderer retains an earlier stack-layout gap, so this source fix
does not claim an exact renderer body. The input path also keeps the historical
F1 jump inside the primary-control path: with no primary control it leaves the
selected entry unchanged. It finds
the selected entry through the terminating flag, draws the current page,
accepts primary and alternate control navigation, and evaluates up and down
independently as the original does. It updates the selected bit and movement
sound, then independently evaluates select, left, and right actions in that
order, allowing a later simultaneous directional action to replace the return
code. The candidate is now 582 bytes against the historical 583 and is
recorded as `DIFFER` for the remaining code-generation byte.

draw_menu now reconstructs the historical rendering loop from its independent
DWARF types and original control flow. Its source-local declaration order is
`pos`, `str[256]`, then `h`, matching the historical debug record. It advances
rows by `font_height - 12`,
formats every entry, renders key bindings in two columns, draws the selection
bullet, and renders the three-piece and movable slider assets through Allegro's
historical inline `draw_sprite` dispatch. The movable asset is one row below
the text baseline (`y + h`), rather than the incorrect `y + y` placeholder.
The candidate is 956 bytes against
the historical 1,118-byte function and is recorded as `DIFFER`; its shorter
code results from equivalent compiler register allocation and branch folding.

handle_menu now reconstructs the menu event loop. Its source-local sequence
includes the optimized-out `done` declaration between `handle_keys` and `data`,
as established by historical DWARF. It resets the selected entry, draws through
an optional callback, debounces both controls, dispatches nested
menus, adjusts sliders and each selection type within its historical bounds,
toggles boolean options, captures control keys, and handles profile actions.
The original return-code table and menu data tables establish these actions.
The candidate is 1,034 bytes against the historical 1,120-byte function and
is recorded as `DIFFER`.

`key_to_str` is an exact 2,543-byte match for the complete 108-label scan-code
dispatch at `0x416a9c`. The historical source uses an ordered `if`/`else if`
chain, not a C `switch`; restoring that topology prevents GCC from replacing
it with a compact jump table. It copies the original key labels and uses
`"undefined"` for all unlisted scan codes; scan code 18 intentionally produces
lower-case `"r"`, and code 105 is the separate semicolon case. The historical
cases use numeric scan codes so their observed 1.5.1 layout remains independent
of the installed Allegro headers.
