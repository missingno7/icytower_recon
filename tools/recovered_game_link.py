"""Link all available game CUs for diagnosis; gate incomplete recovery by default.

An ordinary link can contain known synthetic replacements and unmatched game
functions. It is therefore a diagnostic artifact until source provenance and
strict function evidence permit a recovered-game claim.
"""
import argparse
import os
import re
import subprocess

from common import ROOT, identity, read_json, write_json
from build import COMPILERS, verify_inputs
from link_object_cache import obtain, verify
from source_scope import body_hash


GAME_TARGETS = [
    'game-beta', 'game-control', 'game-csv', 'game-httpget', 'game-directories', 'game-timer',
    'game-stars', 'game-options', 'game-replay', 'game-main',
    'game-map', 'game-scroller', 'game-particle', 'game-player', 'game-fld-adspot',
    'game-hisc', 'game-menu', 'game-game-data', 'game-profile', 'game-custom',
    'game-loadpng', 'game-savepng', 'game-regpng',
    'game-strptime', 'game-timecompat',
]


def unresolved_symbols(stderr):
    names = re.findall(r"undefined reference to [`']([^`']+)[`']", stderr)
    return list(dict.fromkeys(names))


def provenance_status():
    manifest = read_json(ROOT / 'src/reconstruction-provenance.json')
    known = []; placeholders = []
    for entry in manifest['bodies']:
        source = ROOT / entry['source']
        actual = body_hash(source.read_bytes().decode('cp1252'), entry['function'])
        if actual != entry['body_sha256']:
            raise ValueError('Source provenance changed; reclassify ' + entry['source'] + '::' + entry['function'])
        if entry['kind'] == 'synthetic_replacement':
            known.append(entry['source'] + '::' + entry['function'])
        elif entry['kind'] == 'candidate_with_synthetic_slice':
            placeholders.append(entry['source'] + '::' + entry['function'])
        else:
            raise ValueError('Unknown provenance kind for ' + entry['function'])
    ledger = read_json(ROOT / 'src/recovery.json')
    incomplete = [source + '::' + name for source, row in ledger.items()
                  for name, verdict in row.get('functions', {}).items() if verdict != 'FUNCTION_MATCH']
    return {'manifest': identity(ROOT / 'src/reconstruction-provenance.json'),
            'known_synthetic_bodies': known, 'known_placeholder_bodies': placeholders,
            'nonmatching_functions': incomplete,
            'scope': 'Known-body manifest plus strict ledger; neither is an exhaustive source provenance audit.'}


def main(compiler='tdm-2', diagnostic=False):
    provenance = provenance_status()
    if not diagnostic and (provenance['known_synthetic_bodies'] or provenance['known_placeholder_bodies'] or provenance['nonmatching_functions']):
        raise RuntimeError('Recovered-game link refused: %d known synthetic bodies, %d candidate placeholder bodies, and %d nonmatching functions. '
                           'Use --diagnostic only for an explicitly incomplete link.' %
                           (len(provenance['known_synthetic_bodies']), len(provenance['known_placeholder_bodies']),
                            len(provenance['nonmatching_functions'])))
    verify_inputs(compiler)
    tc = COMPILERS[compiler]
    adir = ROOT / 'build' / 'allegro' / compiler
    library = adir / 'liballeg.a'
    report = read_json(adir / 'build.json')
    if identity(library) != report['archive']:
        raise ValueError('Library differs from build report')
    xdir = ROOT / 'build' / 'xiph' / compiler
    xiph = read_json(xdir / 'build.json')
    for name, archive in xiph['archives'].items():
        if identity(xdir / name) != archive['identity']:
            raise ValueError('Xiph archive differs from build report: ' + name)

    archive_inputs = {library: identity(library), adir / 'build.json': identity(adir / 'build.json'),
                      xdir / 'build.json': identity(xdir / 'build.json')}
    archive_inputs.update({xdir / name: identity(xdir / name) for name in xiph['archives']})

    out = ROOT / 'build' / 'recovered-game' / compiler
    out.mkdir(parents=True, exist_ok=True)
    exe = out / ('diagnostic-game.exe' if diagnostic else 'recovered-game.exe')
    link_map = out / ('diagnostic-game.map' if diagnostic else 'recovered-game.map')
    (out / 'link.json').unlink(missing_ok=True)
    exe.unlink(missing_ok=True)
    link_map.unlink(missing_ok=True)
    cache_receipts = {}
    objects = []
    object_reports = []
    for target in GAME_TARGETS:
        obj, build, cache_receipts[target] = obtain(target, out / target, compiler)
        objects.append(obj)
        object_reports.append(build)
    logg_object, logg_report, cache_receipts['allegro-logg'] = obtain(
        'allegro-logg', out / 'allegro-logg', compiler)

    args = [
        tc / 'bin/gcc.exe', '-O2', '-g', '-mfpmath=387', '-DALLEGRO_STATICLINK',
        '-Iinclude', '-Ithird_party/allegro-4.4.1/include', '-mwindows', *objects,
        logg_object, xdir / 'libvorbisfile.a', xdir / 'libvorbis.a', xdir / 'libogg.a',
        library, '-lkernel32', '-luser32', '-lgdi32', '-lcomdlg32', '-lole32',
        '-ldinput', '-lddraw', '-ldxguid', '-lwinmm', '-ldsound', '-lws2_32', '-lpthread',
        '-Lthird_party/libpng-1.2.34', '-lpng3', '-lm',
        '-Wl,-Map,' + str(link_map), '-Wl,--cref', '-o', exe,
    ]
    env = os.environ.copy()
    env['PATH'] = str(tc / 'bin') + os.pathsep + env.get('PATH', '')
    result = subprocess.run([str(x) for x in args], cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    verify_inputs(compiler)
    for path, expected in archive_inputs.items():
        if identity(path) != expected:
            raise ValueError("Link archive input changed: " + str(path))
    for target, receipt in cache_receipts.items():
        verify(target, out / target, receipt, compiler)
    stderr = result.stderr.decode('utf-8', errors='replace')
    output = result.stdout.decode('utf-8', errors='replace')
    record = {
        'scope': 'Incomplete diagnostic source link' if diagnostic else 'Recovered game source link',
        'provenance': provenance,
        'compiler': compiler,
        'command': [str(x) for x in args],
        'allegro_report': identity(adir / 'build.json'),
        'xiph_report': identity(xdir / 'build.json'),
        'logg_object': logg_report,
        'game_objects': object_reports,
        'object_reuse': {t: r['state'] for t, r in cache_receipts.items()},
        'returncode': result.returncode,
        'linked': result.returncode == 0,
        'executed': False,
        'unresolved_symbols': unresolved_symbols(stderr),
        'stdout': output,
        'stderr': stderr,
    }
    if exe.exists():
        record['executable'] = identity(exe)
    if link_map.exists():
        record['link_map'] = identity(link_map)
    write_json(out / 'link.json', record)
    if result.returncode:
        print('Recorded unresolved game-link frontier:', ', '.join(record['unresolved_symbols']))
    else:
        print('Linked', exe, '(diagnostic; not executed)' if diagnostic else '(not executed)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', default='tdm-2')
    parser.add_argument('--diagnostic', action='store_true', help='permit and label incomplete source-link closure')
    args = parser.parse_args()
    try:
        main(args.compiler, args.diagnostic)
    except RuntimeError as exc:
        raise SystemExit(str(exc))
