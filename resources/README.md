The resource census is in evidence/census/resources.json. The original has
one RT_ICON (ID 1, language 1033, 2,216 bytes) and one RT_GROUP_ICON
(ALLEGRO_ICON, language 1033, 20 bytes). Directory timestamp is 1323184024.
There is no embedded VERSIONINFO resource in this executable.

Resource payloads are hash-identified, not copied into tracked source. The
icon does not match the available Allegro shooter example icon. Recovering
the original user-supplied icon plus a resource script and matching windres
directory ordering/timestamps remains an explicit blocker. No raw .rsrc
section is used as a normal link input.

Keep PE resources separate from Allegro datafiles, external game assets,
and generated profiles/replays/logs. The inherited full asset census is in
evidence/research/artifacts/asset_manifest.json; assets/ is ignored.
