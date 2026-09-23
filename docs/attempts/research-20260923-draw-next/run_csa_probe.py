from pathlib import Path
import json, os, subprocess, sys

ROOT = Path.cwd()
OUT = ROOT / 'docs/attempts/research-20260923-draw-next'
sys.path.insert(0, str(ROOT / 'tools'))
from common import read_json, identity
from build import COMPILERS
from experiment import compare
from recovery_pipeline import OBJDUMP

source_in = OUT / 'height-before-pim/overlay/src/main.c'
ledger = read_json(ROOT / 'src/recovery.json')
ref = read_json(ROOT / ledger['src/main.c']['verified_report'])
build = ref['build']
out = OUT / 'passes-csa'
source = out / 'overlay' / 'src' / 'main.c'
source.parent.mkdir(parents=True, exist_ok=True)
source.write_bytes(source_in.read_bytes())
args = list(build['command'])
for flag, val in [('-MF', out/'unit.d'), ('-aux-info', out/'interfaces.aux'),
                  ('-c', source), ('-o', out/'unit.o')]:
    args[args.index(flag)+1] = str(val)
args[1:1] = ['-I' + str(ROOT/'src'), '-fdump-rtl-csa']
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
(out/'summary.json').write_text(json.dumps({'command':args, 'object':identity(out/'unit.o'),
    'functions':len(report['functions']), 'status_counts':{
        state:sum(f['status']==state for f in report['functions'])
        for state in sorted(set(f['status'] for f in report['functions']))},
    'draw_frame':next(f for f in report['functions'] if f['name']=='draw_frame')}, indent=2), encoding='utf-8')
base=json.load(open(OUT/'passes-baseline/comparison.json'))
def code_projection(rep):
    return [(f['name'], [(i['bytes'], i['mnemonic']) for i in f.get('instructions',[])]) for f in rep['functions']]
summary=json.load(open(out/'summary.json'))
summary['matches_baseline_instruction_projection']=code_projection(report)==code_projection(base)
summary['relocations_match_baseline']=report.get('relocations')==base.get('relocations')
(out/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps({k:summary[k] for k in ['object','functions','status_counts','matches_baseline_instruction_projection','relocations_match_baseline']},indent=2))
