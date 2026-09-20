"""Link all recovered game CUs without fallback code.

This deliberately unexecuted candidate uses main-partial's historical WinMain
wrapper, so no synthetic entrypoint, original code, or undefined-symbol
suppression is involved. A successful link establishes ordinary source-link
closure only; per-function and CU fidelity still require oracle verification.
A linker failure records the next genuine dependency frontier.
"""
import os
import re
import subprocess

from common import ROOT, identity, read_json, write_json
from build import COMPILERS, compile_target, verify_inputs


GAME_TARGETS = [
    'game-beta', 'game-control', 'game-csv', 'game-httpget', 'game-directories', 'game-timer',
    'game-stars', 'game-options', 'game-replay', 'game-main-partial',
    'game-map', 'game-scroller', 'game-particle', 'game-player', 'game-fld-adspot',
    'game-hisc', 'game-menu', 'game-game-data', 'game-profile', 'game-custom',
    'game-loadpng', 'game-savepng', 'game-regpng',
    'game-strptime', 'game-timecompat',
]


def unresolved_symbols(stderr):
    names = re.findall(r"undefined reference to [`']([^`']+)[`']", stderr)
    return list(dict.fromkeys(names))


def main(compiler='tdm-2'):
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

    out = ROOT / 'build' / 'recovered-game' / compiler
    out.mkdir(parents=True, exist_ok=True)
    exe = out / 'recovered-game.exe'
    link_map = out / 'recovered-game.map'
    exe.unlink(missing_ok=True)
    link_map.unlink(missing_ok=True)
    objects = []
    object_reports = []
    for target in GAME_TARGETS:
        obj, build = compile_target(target, dest=out / target, compiler=compiler)
        objects.append(obj)
        object_reports.append(build)
    logg_object, logg_report = compile_target(
        'allegro-logg', dest=out / 'allegro-logg', compiler=compiler)

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
    stderr = result.stderr.decode('utf-8', errors='replace')
    output = result.stdout.decode('utf-8', errors='replace')
    record = {
        'scope': 'Ordinary recovered game-object link; no synthetic entrypoint, stubs, original-code input, or execution.',
        'compiler': compiler,
        'command': [str(x) for x in args],
        'allegro_report': identity(adir / 'build.json'),
        'xiph_report': identity(xdir / 'build.json'),
        'logg_object': logg_report,
        'game_objects': object_reports,
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
        print('Linked', exe, '(not executed)')


if __name__ == '__main__':
    main()
