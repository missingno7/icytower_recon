"""One-time export of research evidence and local historical build inputs.

Normal compilation never reads the research repository. No carrier code is
copied into the build. Re-running verifies previously locked inputs, and
refuses changed snapshots rather than silently re-pinning them.
"""
import argparse
from pathlib import Path
import shutil
from common import ROOT, TC, identity, read_json, run, write_json

EVIDENCE = [
    'artifacts/dwarf_cus.json', 'artifacts/compile_units.txt',
    'artifacts/functions.json', 'artifacts/library_compat.json',
    'artifacts/toolchain_fingerprint.json', 'artifacts/lib_boundary.json',
    'artifacts/asset_manifest.json', 'artifacts/pe_resources.json',
    'artifacts/src_equivalence.json',
    'notes/toolchain_fingerprint.md', 'notes/library_boundary.md',
    'notes/library_compat_verdict.md', 'notes/binary_recon.md',
    'notes/external_research.md', 'notes/extraction_plan.md',
    'notes/layout_determinism.md', 'src/icytower/PROMOTIONS.md',
    'src/icytower/INVIVO.md', 'src/icytower/timer.c',
    'third_party/MANIFEST.json', 'imports.json',
]

def copy_checked(source, dest):
    if dest.exists():
        if identity(source) != identity(dest):
            raise ValueError(f'Existing evidence/input differs: {dest}')
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--research', type=Path, required=True)
    args = ap.parse_args()
    r = args.research.resolve()
    fixture=identity(ROOT/'assets/icytower15.exe')
    if identity(r/'assets/icytower15.exe')!=fixture:
        raise ValueError('Research EXE and supplied EXE differ; inherited addresses cannot be imported')
    for name in ['src', 'include', 'third_party', 'resources', 'build', 'docs', 'toolchain', 'evidence/research']:
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    snapshots = []
    for rel in EVIDENCE:
        source, dest = r / rel, ROOT / 'evidence/research' / rel
        copy_checked(source, dest)
        snapshots.append({'source': str(source), 'snapshot': dest.relative_to(ROOT).as_posix(), **identity(dest)})
    write_json(ROOT / 'evidence/research-lock.json', {'repository': str(r), 'files': snapshots})
    write_json(ROOT/'evidence/research-fixture.json',{'source':str(r/'assets/icytower15.exe'),
               'local':'assets/icytower15.exe','identical':True,**fixture})
    inputs = []
    roots = [
        (r / 'third_party/tdm-gcc-4.4.1-tdm-1/mingw32', TC, 'TDM-GCC 4.4.1-tdm-1 SJLJ / bundled binutils and MinGW'),
        (r / 'third_party/allegro-4.4.1', ROOT / 'third_party/allegro-4.4.1', 'Allegro 4.4.1, commit 38624f977d957c32fd7a7ade31ee308a740f4022'),
    ]
    for source_root, dest_root, provenance in roots:
        for source in sorted(source_root.rglob('*')):
            rel = source.relative_to(source_root)
            if not source.is_file() or '.git' in rel.parts:
                continue
            dest = dest_root / rel
            copy_checked(source, dest)
            inputs.append({'path': dest.relative_to(ROOT).as_posix(), 'source': str(source), 'provenance': provenance, **identity(dest)})
    for name in ['libpng3.dll', 'zlib1.dll', 'pthreadGC2.dll']:
        path = ROOT / 'assets' / name
        inputs.append({'path': path.relative_to(ROOT).as_posix(), 'provenance': 'User-supplied runtime DLL; research version identification is separate', **identity(path)})
    lock = {'schema': 1, 'inputs': inputs, 'archive_provenance': 'evidence/research/third_party/MANIFEST.json',
            'versions': {name: run([TC / 'bin' / (name + '.exe'), '--version']).splitlines()[0] for name in ['gcc', 'as', 'ld', 'ar', 'windres']},
            'separate_dependency_lock': 'third_party/xiph-lock.json',
            'missing': ['GNU C 4.2.1-sjlj (mingw32-2) for libogg', 'Original libpng 1.2.34 import archive (candidate derived from supplied runtime exports)', 'Exact pthreads-win32 2.8.0 headers/import library', 'Matching cmshared-enabled historical crtbegin.o/libgcc runtime'],
            'historical_flags': {'game': {'candidate': '-Os -mfpmath=387', 'status': 'INFERRED; per-CU verification required'}, 'allegro': {'candidate': '-O2 -DALLEGRO_STATICLINK', 'status': 'INFERRED; per-CU verification required'}}}
    out = ROOT / 'toolchain/lock.json'
    if out.exists() and read_json(out) != lock:
        raise ValueError('Lock changed; explicit review required, old lock retained')
    write_json(out, lock)
    for name in ['loadpng.c', 'savepng.c', 'regpng.c']:
        copy_checked(ROOT / 'third_party/allegro-4.4.1/addons/loadpng' / name, ROOT / 'src' / name)
    copy_checked(ROOT / 'third_party/allegro-4.4.1/addons/loadpng/loadpng.h', ROOT / 'include/loadpng.h')
    generated = ROOT / 'include/allegro/platform/alplatf.h'
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text('/* Reconstructed CMake platform configuration; not an original game header. */\n#define ALLEGRO_MINGW32\n#define ALLEGRO_NO_ASM\n#define ALLEGRO_USE_C\n', encoding='utf-8')
    print(f'Exported {len(snapshots)} evidence files; locked {len(inputs)} local inputs.')

if __name__ == '__main__':
    main()
