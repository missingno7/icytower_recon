# Partial `menu.c` experiment

The recovered slider and selection accessors are byte-exact at `-O2`.
`set_slider_value` accepts only inclusive slider bounds, while
`set_selection_value` accepts selection indices in the half-open range from
zero to `max`. The remaining menu rendering and input functions are not yet
recovered; this target uses only reconstructed source and the original
executable as a comparison oracle.
