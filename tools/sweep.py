"""Run a bounded, explicit compiler-flag sweep for one recovered CU."""
import argparse
import hashlib

from common import ROOT, identity, write_json
from build import COMPILERS, TARGETS, compile_target, verify_inputs
from experiment import compare


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target', choices=sorted(TARGETS))
    ap.add_argument('--flag', action='append', default=[], help='One additional compiler flag; repeat at most three times.')
    ap.add_argument('--compiler', choices=sorted(COMPILERS), default='tdm-2')
    ap.add_argument('--objdump', default='C:/msys64/mingw64/bin/objdump.exe')
    a = ap.parse_args()
    if len(a.flag) > 3:
        raise ValueError('Sweep is bounded to three explicit flags')
    verify_inputs(a.compiler)
    token = hashlib.sha256('\0'.join(a.flag).encode('utf-8')).hexdigest()[:12]
    dest = ROOT / 'build/sweeps' / a.compiler / a.target / token
    obj, build = compile_target(a.target, [TARGETS[a.target]['default'], *a.flag], dest, compiler=a.compiler)
    result = compare(obj, TARGETS[a.target]['historical_cu'], ROOT / 'assets/icytower15.exe', a.objdump)
    result.update(build=build, fixture=identity(ROOT / 'assets/icytower15.exe'),
                  sweep={'target': a.target, 'flags': a.flag, 'bounded': True})
    write_json(dest / 'comparison.json', result)
    print(dest / 'comparison.json')


if __name__ == '__main__':
    main()
