from pathlib import Path
import hashlib, json, os, subprocess, sys

ROOT = Path.cwd()
OUT = ROOT / 'docs/attempts/research-20260923-draw-next'
sys.path.insert(0, str(ROOT / 'tools'))
from common import read_json, identity
from build import COMPILERS
from experiment import compare
from recovery_pipeline import OBJDUMP

baseline_source = OUT / 'height-before-pim/overlay/src/main.c'
ledger = read_json(ROOT / 'src/recovery.json')
ref = read_json(ROOT / ledger['src/main.c']['verified_report'])
build = ref['build']
unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == 'src/main.c')

def compile_one(label, extra_flags=()):
    out = OUT / ('passes-' + label)
    ov = out / 'overlay' / 'src'
    ov.mkdir(parents=True, exist_ok=True)
    source = ov / 'main.c'
    source.write_bytes(baseline_source.read_bytes())
    args = list(build['command'])
    for flag, val in [('-MF', out/'unit.d'), ('-aux-info', out/'interfaces.aux'),
                      ('-c', source), ('-o', out/'unit.o')]:
        args[args.index(flag)+1] = str(val)
    args[1:1] = ['-I' + str(ROOT/'src')]
    args[1:1] = list(extra_flags)
    args = [a if not (isinstance(a, str) and a.startswith('-I') and not os.path.isabs(a[2:]))
            else '-I' + str(ROOT/a[2:]) for a in args]
    env = os.environ.copy()
    env['PATH'] = str(COMPILERS[build['compiler']]/'bin') + os.pathsep + env['PATH']
    r = subprocess.run([str(x) for x in args], cwd=out, env=env, capture_output=True, text=True)
    (out/'compiler.stdout.txt').write_text(r.stdout, encoding='utf-8')
    (out/'compiler.stderr.txt').write_text(r.stderr, encoding='utf-8')
    if r.returncode:
        raise SystemExit('compile failed ' + str(r.returncode))
    report = compare(out/'unit.o', ref['historical_cu'], ROOT/'assets/icytower15.exe', OBJDUMP)
    (out/'comparison.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    focus = next(f for f in report['functions'] if f['name'] == 'draw_frame')
    result = {'label': label, 'args': args, 'object': identity(out/'unit.o'),
              'body_size': focus['candidate_size'], 'instruction_bytes': ''.join(i['bytes'] for i in focus['instructions']),
              'relocations': focus.get('relocations'), 'direct_transfers': focus.get('direct_transfers'),
              'first_difference': focus.get('first_difference')}
    (out/'summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['label','object','body_size','first_difference']}, indent=2))

compile_one('baseline')
compile_one('tree-all', ['-fdump-tree-all'])
compile_one('tree-rtl-all', ['-fdump-tree-all', '-fdump-rtl-all'])
