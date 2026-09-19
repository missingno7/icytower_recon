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

build_menu_string is behaviorally reconstructed. It formats slider progress, a selected value, boolean choices, key bindings, headings, and plain captions from recovered menu flags and data layouts. Its 407-byte candidate retains a different temporary-buffer stack layout from the 415-byte historical body, so it is recorded as `DIFFER`.
