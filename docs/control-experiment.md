# Complete control CU

The recovered `src/control.c` contains all 15 original functions. At -O2
and -O3 its complete 750-byte text contribution matches, including padding,
relative layout and independently resolved relocation targets. -O0 matches
3 functions, -O1 12, and -Os 13. No object/CU match is claimed: historical
debug metadata and final common placement remain unresolved.

DWARF establishes a 36-byte control structure (eight ints and a flag byte)
and a 144-byte gamepad structure. Natural ABI padding is retained. The
gamepad global is a common allocation; it is not initialized data.

Reuniting the exported control and poll bodies was insufficient by itself.
The original source declaration order, recorded by DWARF, places poll before
the predicates and save before load. GCC rearranges the emitted functions;
restoring source order produces the original text layout without placement
attributes. The is_any expression requires the full-width complement of
CTRL_PAUSE. fread/fwrite use the full natural structure size.

The complete comparison and optimization matrix are in `docs/experiments`.
The synthetic integration link resolves these functions and timer.c against
the rebuilt Allegro archive. It neither executes nor embeds original code.
