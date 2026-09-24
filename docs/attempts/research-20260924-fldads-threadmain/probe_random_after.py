import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from tu_context_probe import build_text,compile_overlay,islands
from experiment import compare
from recovery_pipeline import OBJDUMP
src='src/fld_adspot.c'; target='game-fld-adspot'; outdir=ROOT/'docs/attempts/research-20260924-fldads-threadmain'
text=(ROOT/src).read_text(encoding='cp1252'); order=[i['name'] for i in islands(text)]
order.remove('fldads_update_local_adimg'); order.insert(order.index('fldads_get_local_filename_from_url')+1,'fldads_update_local_adimg')
order.remove('fldads_get_random_ad'); order.insert(order.index('fldads_threadmain')+1,'fldads_get_random_ad')
new,edits,headers=build_text(target,src,{'order':order,'prototypes':'none'})
(outdir/'update-local-before-csv-random-after-threadmain.c').write_text(new,encoding='cp1252')
out,ref,build,r=compile_overlay(target,src,new,'fldads-threadmain-20260924-update-local-random-after-threadmain',dumps=True,headers=headers)
if r.returncode: raise SystemExit(r.stderr)
report=compare(out/'unit.o',ref['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
(outdir/'update-local-before-csv-random-after-threadmain-comparison.json').write_text(json.dumps(report,indent=2))
fs={f['name']:f for f in report['functions']}
summary={'order':order,'overlay_sha256':hashlib.sha256(new.encode('cp1252')).hexdigest(),'object_sha256':hashlib.sha256((out/'unit.o').read_bytes()).hexdigest(),'function_matches':report.get('function_matches'),'whole_text_contribution_equal':report.get('whole_text_contribution_equal'),'object_match':report.get('object_match'),'cu_match':report.get('cu_match'),'target':{k:fs['fldads_threadmain'].get(k) for k in ['status','candidate_size','original_size','first_difference']},'random':{k:fs['fldads_get_random_ad'].get(k) for k in ['status','candidate_size','original_size','first_difference']},'statuses':{n:f['status'] for n,f in fs.items()},'build_output':str(out.relative_to(ROOT))}
(outdir/'update-local-before-csv-random-after-threadmain-summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
