# `view_profile` recovery status

`view_profile` spans `0x419aec..0x41a3b5` (2,249 bytes) in `profile.c`. The
current independently compiled source candidate is `DIFFER` at 1,802 bytes,
not missing. It constructs the profile data pages, rank panel, animated
slide-in/slide-out display, control loop, and cleanup path.

The remaining 447 bytes cover unrecovered layout and presentation details.
This status was established by compiling the current source with the pinned
toolchain and comparing its function body against the local oracle.
