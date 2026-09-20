"""Stage an independently linked game executable with verified runtime assets.

The executable comes from ``recovered_game_link.py``.  Resources are copied
from the fixture's asset directory; the original executable is never a stage
input.  The stage manifest records exact file identities for review.
"""
import shutil
from pathlib import Path

from common import ROOT, identity, write_json


COMPILER = 'tdm-2'
RUNTIME_FILES = ('gamepad.txt', 'tower.cfg', 'pthreadGC2.dll', 'libpng3.dll')
RUNTIME_TREES = ('data', 'characters', 'profiles')


def copy_file(source, destination, stage, manifest):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    actual = identity(destination)
    if actual != identity(source):
        raise ValueError('staged identity differs: ' + str(destination))
    manifest[destination.relative_to(stage).as_posix()] = actual


def main():
    linked = ROOT / 'build' / 'recovered-game' / COMPILER / 'recovered-game.exe'
    if not linked.exists():
        raise FileNotFoundError('build the recovered game before staging: ' + str(linked))
    assets = ROOT / 'assets'
    stage = ROOT / 'build' / 'recovered-game' / COMPILER / 'runtime'
    stage.mkdir(parents=True, exist_ok=True)
    manifest = {}
    copy_file(linked, stage / linked.name, stage, manifest)
    for name in RUNTIME_FILES:
        copy_file(assets / name, stage / name, stage, manifest)
    for name in RUNTIME_TREES:
        source = assets / name
        for path in source.rglob('*'):
            if path.is_file():
                copy_file(path, stage / path.relative_to(assets), stage, manifest)
    write_json(stage / 'stage.json', {
        'scope': 'Source-linked recovered-game executable plus asset fixture resources; original executable excluded.',
        'executable': 'recovered-game.exe',
        'files': dict(sorted(manifest.items())),
        'executed': False,
    })
    print('Staged', stage)


if __name__ == '__main__':
    main()
