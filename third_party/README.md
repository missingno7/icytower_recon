The normal build uses local, hash-locked inputs. It never reads PortForge or
the external research repository. Large upstream/toolchain trees are ignored
by Git and can be populated with the documented bootstrap commands.

- Allegro 4.4.1: source exported from the archived checkout at commit
  `38624f977d957c32fd7a7ade31ee308a740f4022`; per-file hashes in
  `toolchain/lock.json`. The Giftware license is retained in
  `licenses/allegro-license.txt`. No Allegro 4.4.3.1 input is used.
- loadpng.c, savepng.c, regpng.c and loadpng.h are copied verbatim from that
  release into the historical game source locations. Their public-domain
  notices remain intact. They are KNOWN_UPSTREAM, not yet compiled/matched;
  exact libpng 1.2.34 headers/import libraries remain to be pinned.
- libvorbis 1.2.0 and libogg 1.1.3 are from the
  [Xiph Vorbis archive](https://downloads.xiph.org/releases/vorbis/) and
  [Xiph Ogg archive](https://downloads.xiph.org/releases/ogg/). Fetching checks
  the publisher's SHA256SUMS; archive and extracted-file hashes are in
  xiph-lock.json. Licenses remain in each release's COPYING file.
- libogg 1.1.3 remains a binary-version candidate. The original framing.c and
  bitwise.c report GCC 4.2.1-sjlj (mingw32-2); that compiler is still missing.
- logg.c is VENDORED_MODIFIED. The unmodified Allegro file remains upstream
  source; `recovered/logg.c` reconstructs the memory extension separately.
  All 18 emitted functions and complete text now match at -O2; Xiph linkage
  and debug metadata remain unresolved. Its MIT license is in
  `licenses/logg-license.txt`.
- csv.c and httpget.c are AMBIGUOUS and remain recovery-owned. strptime.c
  and timecompat.c have identified compatibility-code families but unresolved
  exact revisions. They remain skeletons rather than guessed replacements.

Runtime DLLs and original game assets are user-supplied, ignored files.
Original program bytes and proprietary datafiles are not vendored into Git.
