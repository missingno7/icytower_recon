# `force_create_profile` recovery

`force_create_profile` spans `0x40d454..0x40da56` (1,538 bytes) in `main.c`.
Its recovered candidate is `DIFFER` at 1,458 bytes. The source keeps the
oracle's screen snapshot, profile-name prompt/retry loop, sanitization,
existing-name retry, guest fallback, option synchronization, and profile-list
refresh.

DWARF lines 5650--5722 and the executable establish the flow and the datafile
assets. The remaining code-generation difference includes the candidate's
stack-frame layout; this status makes no byte-equality claim.
