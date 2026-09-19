# Custom dependency link

`tools/audio_link.py --with-custom` creates an unexecuted synthetic PE from
the recovered custom, directories, partial-main and particle objects, reconstructed
logg, 22 candidate Xiph objects, historical Allegro and pthread. The linker
resolves all of these objects without fallback definitions.

The artifact proves only dependency resolution. Custom still has one differing
function, main.c is partial, Xiph byte equality is unproven, and this PE does
not claim the original address layout, resources, debug data or executable
bytes. Its input hashes, commands and output hash are retained in
`docs/experiments/custom-audio-link.json`.
