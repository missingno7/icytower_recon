You are starting a new independent reconstruction project for Icy Tower 1.5.1.

Existing research/oracle repository:

D:\Games\DOS\dos_recosystem\icytower_forged

Create a separate sibling project/repository, conceptually:

```text
icytower_reconstruction
```

Do NOT turn `icytower_forged` itself into this project.

`icytower_forged` is an evidence repository, behavioral oracle, reverse-engineering laboratory, and source of already-established facts.

The new project has a different goal:

> Reconstruct the original Icy Tower software project and build as completely as practical, using the original compilation-unit structure, original toolchain family, original third-party libraries, recovered game source, PE/resources/assets, and real linking rules.

This should follow the philosophy established by:

D:\Prog\empires_reconstruction

but adapted to a Win32 PE/COFF/GCC program with unusually rich DWARF/debug evidence.

# Fundamental goal

Do NOT begin by making another carrier or another source port.

The target pipeline is:

```text
original icytower15.exe
        ↓
recover original build topology
        ↓
recover original game translation units
        ↓
recover/reuse exact third-party sources and libraries
        ↓
compile to real COFF objects
        ↓
link with reconstructed historical toolchain/build rules
        ↓
reconstructed icytower15.exe
```

The strongest desired endpoint is byte-identical reproduction of the original executable.

If exact identity is blocked by specific linker/build metadata, identify and isolate the exact differing fields rather than weakening the target prematurely.

The final reconstructed project should eventually resemble a normal historical source tree, not a carrier project:

```text
icytower_reconstruction/
├── src/
├── include/
├── third_party/
├── resources/
├── build/
├── tools/
├── docs/
└── toolchain/
```

The original executable should ultimately be a verification fixture, not an input to normal generation.

# Extremely important: exploit the existing evidence first

Before recovering new code, thoroughly inspect `icytower_forged`.

Important evidence already exists under:

```text
artifacts/
notes/
src/icytower/
carrier/
tools_recon/
```

In particular inspect:

```text
artifacts/dwarf_cus.json
artifacts/compile_units.txt
artifacts/functions.json
artifacts/library_compat.json
artifacts/toolchain_fingerprint.json

notes/toolchain_fingerprint.md
notes/library_boundary.md
notes/library_compat_verdict.md
notes/binary_recon.md
notes/external_research.md
notes/extraction_plan.md
notes/layout_determinism.md

src/icytower/PROMOTIONS.md
src/icytower/INVIVO.md

imports.json
```

Do not rediscover facts that are already proven there.

Import facts, not accidental architecture from the old carrier.

# Known high-value facts

## 1. DWARF gives us the historical compilation-unit topology

The executable contains approximately:

```text
148 DWARF compilation units
```

with producers:

```text
145 × GNU C 4.4.1
2   × GNU C 4.2.1-sjlj (mingw32-2)
1   × GNU AS 2.19.1
```

This is extraordinarily valuable.

Unlike the DOS Empires reconstruction, we do NOT need to infer most source-file boundaries from function adjacency.

DWARF already gives historical compilation units and source paths.

There are exactly 25 compilation units under the original game source tree:

```text
F:\projects\icytower\trunk\source\
```

They are:

```text
beta.c
control.c
csv.c
custom.c
directories.c
fld_adspot.c
game_data.c
hisc.c
httpget.c
loadpng.c
main.c
map.c
menu.c
options.c
particle.c
player.c
profile.c
regpng.c
replay.c
savepng.c
scroller.c
stars.c
strptime.c
timecompat.c
timer.c
```

Preserve these names and historical translation-unit boundaries unless evidence proves otherwise.

Do not replace them with `F_401234.c`-style mechanical files in the final project.

## 2. Not all 25 game-tree files are actually original game code

The existing library-boundary analysis separates them into:

```text
18 true game-owned CUs
7 vendored / third-party CUs
```

The true game-owned code is approximately:

```text
217 functions
116,113 bytes of .text
15.45% of total .text
```

The whole game-tree contribution including vendored code is:

```text
253 functions
125,641 bytes
25 CUs
```

Known vendored files include:

```text
loadpng.c
savepng.c
regpng.c
strptime.c
timecompat.c
csv.c
httpget.c
```

More precisely:

```text
loadpng.c / savepng.c / regpng.c
    → Allegro 4.4.1 loadpng addon

strptime.c
    → BSD/glibc-style strptime implementation

timecompat.c
    → timegm compatibility shim

csv.c
httpget.c
    → origin currently ambiguous;
      treat as game-owned until stronger provenance exists
```

Do not waste time decompiling already-identified upstream source.

Recover what is actually lost.

# 3. Third-party ownership dominates the executable

Existing analysis of 751,448 bytes of `.text` finds approximately:

```text
Allegro            468,724 B   62.38%
Ogg/Vorbis         121,232 B   16.13%
game-owned         116,113 B   15.45%
game-tree vendored   9,528 B    1.27%
CRT/libgcc          33,379 B    4.44%
```

Third-party code is more than 83% of the executable.

Therefore:

> Do not reconstruct Allegro, Ogg/Vorbis, CRT, etc. function-by-function.

Identify the correct historical source/version/build and reproduce their object/library contributions from that.

# 4. Allegro is very strongly identified

The embedded library identifies itself as:

```text
"Allegro 4.4.1, MinGW32.s"
```

The `.s` is evidence of:

```text
ALLEGRO_STATICLINK
```

Known configuration:

```text
Allegro 4.4.1
MinGW32
static link
C-only implementation
no DEBUGMODE
```

DWARF contains approximately 106 Allegro compilation units.

Ownership census:

```text
Allegro core         906 functions / 289,796 B
Allegro C blitters   270 functions / 106,148 B
Allegro Win32        306 functions / 64,664 B
Allegro misc          31 functions / 6,075 B
logg addon            18 functions / 2,041 B
```

Historical source paths include for example:

```text
C:\Lib\allegro4\src\keyboard.c
C:\Lib\allegro4\src\joystick.c
C:\Lib\allegro4\src\allegro.c
C:\Lib\allegro4\src\sound.c
...
C:\Lib\allegro4\addons\logg\logg.c
```

Use upstream Allegro 4.4.1 as the reconstruction source.

Do not substitute Allegro 4.4.3.1 in the historical reconstruction.

4.4.3.1 may remain useful later for a modern source port, but the reconstruction target is 4.4.1.

# 5. Ogg/Vorbis versions are also known

Existing evidence identifies:

```text
libvorbis / libvorbisfile 1.2.0
libogg approximately 1.1.3
```

The binary includes approximately:

```text
libvorbis       181 functions / 92,320 B
libvorbisfile    47 functions / 22,032 B
libogg           68 functions / 6,880 B
```

The game does NOT directly call these libraries.

The entire ~121 KB Ogg/Vorbis subsystem is reached through only:

```text
logg_load
logg_load_memory
```

This is an exceptionally clean ownership boundary.

libogg's two DWARF CUs:

```text
framing.c
bitwise.c
```

report:

```text
GNU C 4.2.1-sjlj (mingw32-2)
```

and historical build paths reference:

```text
libogg-1.1.3
```

Do not blindly rebuild libogg with GCC 4.4.1 if historical object reproduction requires the older compiler.

# 6. `logg.c` has a small local modification

The historical logg CU is mostly Allegro 4.4.1's upstream:

```text
addons/logg/logg.c
```

but contains seven extra functions, approximately 667 bytes, including:

```text
logg_load_memory
logg_load_internal
logg_vf_memfile_seek
logg_vf_memfile_tell
logg_vf_memfile_read
logg_vf_memfile_close
...
```

Upstream Allegro's logg addon does NOT contain `logg_load_memory`.

Treat this as a small historical local patch/vendor extension.

Recover this patch instead of reconstructing all of logg/Vorbis.

# 7. External DLL versions are known

Existing evidence identifies at least:

```text
libpng3.dll
    libpng 1.2.34
    GnuWin32 build

zlib1.dll
    zlib 1.2.3
    GnuWin32 build

pthreadGC2.dll
    pthreads-win32 2.8.0
    GNU C / GC flavour
```

The executable also imports normal Win32/DirectX-era APIs from:

```text
DDRAW.dll
dinput.dll
dsound.dll
GDI32.dll
KERNEL32.dll
msvcrt.dll
OLE32.dll
SHELL32.dll
USER32.dll
WINMM.dll
WSOCK32.dll
```

The complete import table already exists in:

```text
imports.json
```

Use it as evidence.

Do not reconstruct imported CRT routines such as:

```text
malloc
free
rand
srand
strlen
toupper
memcpy
...
```

They are imports from `msvcrt.dll`, unlike the statically linked runtime situation in Empires.

# 8. The historical compiler/toolchain is unusually well identified

Known from the executable:

```text
TDM-GCC 4.4.1
mingw32
SJLJ exception/runtime variant
```

libgcc build paths include:

```text
c:\crossdev\b4.4.1-tdm-1\build-sjlj\mingw32\libgcc
```

DWARF include paths reference the MinGW bundled with Code::Blocks.

The strongest current conclusion is:

```text
TDM-GCC 4.4.1-tdm-1 SJLJ
binutils / GNU AS 2.19.1
Code::Blocks-era MinGW environment
```

Both TDM-GCC 4.4.1 tdm-1 and tdm-2 toolchains have already been archived/fingerprinted in the research repo.

The compiler fingerprint experiment found no codegen differences between tdm-1 and tdm-2 for the tested functions, but historical provenance points specifically at tdm-1.

Pin the exact historical toolchain components needed for reconstruction:

```text
gcc.exe
as.exe
ld.exe
ar.exe
windres.exe
collect2.exe
libgcc pieces
MinGW startup objects
import libraries
headers
```

as required.

Do not redistribute proprietary/non-redistributable inputs if applicable; use hash-pinned local inputs when necessary.

# 9. Compiler flags differ between game and library code

Do NOT assume one optimization level for the whole executable.

Existing fingerprint evidence strongly suggests:

```text
game code:
    likely -Os for at least important game CUs

Allegro 4.4.1:
    likely -O2
```

For example `control.c` reaches 9/11 exact functions at `-Os`, while the tested Allegro CUs strongly favor `-O2`.

Use per-CU compiler fingerprinting.

Candidate dimensions include:

```text
-O0 / -O1 / -O2 / -O3 / -Os
-fomit-frame-pointer variants
-march variants
x87 settings
alignment options
section/function alignment
```

The original is x87-sensitive.

Do not "clean up" floating-point logic until historical behavior is understood.

# 10. Preserve x87 semantics

Existing carrier verification proved that several recovered functions require true x87-style intermediate precision.

Examples include:

```text
new_rand
update_particle
create_particle
jump_player
line_intersect
update_player
```

The reconstruction build should preserve the historical x87 environment.

Do not silently replace x87 intermediate behavior with SSE/double semantics.

Existing research uses the control-word behavior around:

```text
CW = 0x037F
```

Treat this as build/runtime evidence to verify, not as optional source-port behavior.

# 11. PE facts

The existing fingerprint/reconstruction tooling treats the executable as a fixed-base PE around:

```text
ImageBase = 0x400000
```

and records that the original carries no ordinary `.reloc` section.

Verify all PE facts fresh and publish them in the new reconstruction project:

```text
PE header
section table
ImageBase
entry point
section alignment
file alignment
imports
exports
resources
debug sections
DWARF sections
COFF metadata
relocations
TLS
load configuration
timestamps/checksum
```

Do not discard debug/DWARF information after using it.

The reconstructed historical executable should eventually reproduce the original debug/source metadata where practical.

# 12. The DWARF is a first-class source-recovery input

Build a complete machine-readable DWARF census before doing broad decompilation.

Recover:

```text
compilation units
source filenames
producer strings
function names
function addresses/ranges
parameter names
parameter types
return types
local variables
global variables
structs
unions
enums
typedefs
array dimensions
line mappings
abstract_origin/specification chains
inlined functions
static functions
```

The existing forged repo already contains machinery for following:

```text
DW_AT_abstract_origin
DW_AT_specification
```

because some addressed function instances have no direct name/type and refer to an abstract DIE.

Reuse the knowledge, not necessarily the old carrier architecture.

Generate a canonical project skeleton from DWARF.

# 13. Original headers/includes should be reconstructed too

Unlike Empires, this project contains enough type/prototype evidence that a high-quality header reconstruction is realistic.

Recover:

```text
shared structs
typedefs
enums
extern globals
function declarations
library includes
platform includes
```

Separate:

```text
game-owned headers
Allegro/public library headers
MinGW/Win32 headers
local compatibility headers
```

Do not claim an original header filename unless evidence exists.

But where DWARF or source paths expose original filenames, preserve them.

The target is not just matching functions; it is a coherent buildable source tree.

# 14. Start reconstruction at the compilation-unit level

Because the historical CU boundaries are known, do NOT make one source file per recovered function.

For each original game CU create the historical file immediately, for example:

```text
src/control.c
src/main.c
src/player.c
src/replay.c
...
```

Inside each file maintain ownership states such as:

```text
RECOVERED_EXACT
RECOVERED_BEHAVIORAL
KNOWN_UPSTREAM
UNKNOWN
```

or equivalent external manifests.

Unknown functions may temporarily remain represented mechanically, but their location must be inside the correct historical CU.

Prefer reconstructing one complete CU at a time.

# 15. Establish a strong matching compiler loop

For each recovered function/CU:

```text
candidate C
    ↓
historical GCC
    ↓
COFF object
    ↓
compare against original contribution
```

Mask or separately resolve relocation fields when performing object-code comparison.

Compare:

```text
length
machine bytes
instruction sequence
COFF relocations
public/static symbols
section contribution
alignment
data
BSS
DWARF where useful
```

Define proof levels similar to Empires:

```text
BEHAVIOR_EQUAL
CODEGEN_SIMILAR
FUNCTION_MATCH
OBJECT_MATCH
CU_MATCH
LINKED_LAYOUT_MATCH
PE_MATCH
WHOLE_EXE_MATCH
```

Do not conflate deterministic replay equality with historical source/build reconstruction.

# 16. Recover the linker structurally

Once enough CUs compile:

```text
historical game .o files
+ reconstructed/pinned Allegro 4.4.1
+ libvorbis 1.2.0
+ libogg 1.1.3
+ MinGW runtime/startup
+ import libraries
+ resources
        ↓
historical GNU linker/binutils
        ↓
icytower15.exe
```

Infer the original object/library ordering using:

```text
DWARF CU address order
COFF File records
function address ranges
section contribution ordering
static-library extraction behavior
symbols/relocations
startup/CRT layout
```

Do not hard-code final function addresses.

The address of each function must eventually emerge from:

```text
CU contents
section sizes
alignment
object order
library extraction
linker script/default rules
```

Keep a fixed-layout reconstruction only as a verifier if needed.

# 17. Treat library boundaries as libraries, not decompilation targets

Existing analysis proves a very clean game ↔ Allegro boundary:

```text
100 distinct Allegro-family functions used
26 Allegro globals
24 callback registrations
exactly one genuine game→internal Allegro symbol edge:
    _win_hcursor
```

No static function-pointer table mixes game and library families.

No library code writes game globals.

This strongly supports reconstructing the historical project using real Allegro source/library modules.

Do NOT copy 1,500 Allegro functions into the reconstructed game source.

# 18. Existing recovered game source is valuable evidence, not unquestioned truth

`icytower_forged/src/icytower/` already contains many recovered functions.

The carrier has extensively verified these against the original.

Examples of the verification infrastructure include:

```text
deterministic input replay
per-tick state digests
per-function invocation comparison
original-vs-src runtime binding
snapshot/restore
frame oracle
```

One major replay:

```text
human_test.txt
2293 gameplay ticks
100 floors
score 2386
```

has already been used extensively.

Many recovered functions run simultaneously with an EQUAL whole-game digest.

Reuse these sources where they are supported.

But do NOT simply copy the directory and declare the original source recovered.

Each recovered function should be assigned to its historical DWARF CU and tested under the historical compiler.

The forged project's current C often intentionally optimizes for semantic recovery/carrier integration rather than exact historical code generation.

# 19. Keep the carrier as an independent behavioral oracle

The existing forged carrier is extremely valuable.

Do not delete or merge it into the reconstruction project.

Use:

```text
icytower_forged
    → original executable behavioral oracle

icytower_reconstruction
    → historical source/build reconstruction
```

Run the same deterministic workloads against both when useful.

For semantic validation:

```text
same replay/input
        ├── original through forged carrier
        └── reconstructed executable
               ↓
compare normalized state
```

But remember:

```text
behavioral equality != build equality
```

The reconstruction project needs both.

# 20. Assets/resources are another independent ownership axis

The existing forged repo already has:

```text
artifacts/asset_manifest.json
asset census tooling
Allegro datafile knowledge
PE resource tooling
```

The game uses files including:

```text
data/data.dat
data/loading.dat
data/sfx15.dat
data/com/default.dat
data/com/temp.dat
tower.cfg
gamepad.txt
characters/
profiles/
replays/
```

and produces screenshots/logs/replays/profile data.

Separate:

```text
PE embedded resources
Allegro datafiles
external runtime assets
generated/user data
```

The reconstruction build should recreate PE resources structurally.

External original game assets may remain user-supplied verification/runtime inputs where redistribution is inappropriate.

Do not embed copyrighted asset blobs in the repository merely to get equality.

# 21. Reconstruct the original build before modernizing

Do not yet:

```text
convert everything to C++
replace Allegro with SDL
rewrite renderer
add widescreen
modernize input
refactor all globals
```

Those are later source-port tasks.

First:

```text
make the original project reconstructible
make its historical build topology explicit
make its game code readable
prove it against the original
```

Then a future branch can modernize it.

Keep the same philosophy as Empires:

> First make it reconstructible.
> Then understandable.
> Finally beautiful.

# First concrete phase

Implement an MVP reconstruction pipeline.

## Deliverable A — immutable binary census

Produce canonical documents for:

```text
original EXE identity/hash
PE headers and sections
imports
resources
DWARF CUs
COFF File records
functions
globals
types
library ownership
toolchain fingerprints
```

All facts should have provenance.

## Deliverable B — historical source tree skeleton

Generate the 25 known original game-tree source files.

Classify each CU as:

```text
GAME
VENDORED_UPSTREAM
VENDORED_MODIFIED
AMBIGUOUS
```

Populate known upstream files from exact historical upstream releases where licensing permits.

Do not recover their functions manually.

## Deliverable C — toolchain lock

Pin:

```text
TDM-GCC 4.4.1-tdm-1
binutils 2.19.1
MinGW runtime/startup inputs
historical headers
Allegro 4.4.1
libvorbis 1.2.0
libogg 1.1.3 candidate
external DLL identities
```

Record SHA-256/provenance for every build input.

## Deliverable D — first exact compilation-unit experiments

Start with small game CUs where existing recovered source is already strong, for example:

```text
control.c
particle.c
timer.c
map.c
```

Compile the complete CU with the historical compiler.

Compare all functions, static data, symbols and relocations.

Do not cherry-pick only functions that match.

A complete CU match is much more valuable.

## Deliverable E — library reproduction experiments

Build selected Allegro 4.4.1 CUs using the historical compiler and test them against embedded bytes.

Use existing fingerprint evidence:

```text
Allegro likely -O2
game likely -Os
```

Treat unexplained near-matches as compiler/alignment/flags problems and investigate them systematically.

## Deliverable F — first structural link

Produce a PE using real relocatable COFF objects.

The first linker milestone is:

> A substantial prefix of the original `.text` obtains the correct addresses from natural object/library ordering, with no per-function forced placement.

Then progress toward:

```text
.text exact layout
.rdata exact layout
.data exact layout
.bss semantics
imports exact
resources exact
DWARF/debug layout
PE header exact
whole EXE exact
```

# Metrics

Maintain a machine-readable progress report.

At minimum report:

```text
game CUs total
game CUs skeletonized
game CUs partially recovered
game CUs function-complete
game CUs object-exact

game functions total
game functions recovered
game text bytes reconstructed
unknown game text bytes

upstream library CUs identified
upstream library CUs reproduced

data bytes structured
BSS globals typed
DWARF types recovered

linker-resolved functions
linker-resolved bytes
natural-layout prefix length

PE sections matching
whole executable status
first current blocker
```

Do not use a single misleading "% decompiled" metric.

# Blocker discipline

Whenever progress stops, create a blocker entry containing:

```text
target
current evidence
first mismatching function/address/byte
hypotheses
experiments already tried
specific missing artifact or fact
highest-leverage next experiment
```

Examples:

```text
compiler flags not yet reproduced
static library extraction order differs
function alignment differs
DWARF inline abstract origin unresolved
third-party version uncertain
local vendored patch unresolved
resource script missing
linker metadata/timestamp differs
```

Do not report vague blockers such as "linker does not match".

# Independence requirement

The new reconstruction project must be buildable independently of PortForge.

It may consume exported research facts from `icytower_forged`, but its normal build must not require:

```text
carrier/
PF_* APIs
guest-address dispatch
binary execution
runtime patching
original-function fallbacks
```

The old carrier is an external verifier.

The reconstruction is the software project.

# Immediate instruction

Start now.

Do not spend the first pass recovering more isolated functions.

First inspect all existing evidence and create:

1. the reconstruction repo structure,
2. the binary/toolchain/CU census,
3. the historical 25-file source skeleton,
4. the third-party ownership map,
5. the compiler/linker experiment harness,
6. a concise progress/blocker ledger.

Then select the first complete game compilation unit and drive it toward a real historical COFF/object match.

The project succeeds when we can eventually say:

> This is not merely an Icy Tower source port. It is a reconstructed buildable form of the original Icy Tower 1.5.1 software project, derived from its binary/debug evidence and independently verified against the original executable.
