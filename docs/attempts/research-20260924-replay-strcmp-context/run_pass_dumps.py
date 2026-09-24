import hashlib, json, sys
from pathlib import Path
ROOT=Path.cwd(); sys.path.insert(0,str(ROOT/'tools'))
import tu_context_probe as ctx
from common import read_json, write_json, identity
from experiment import compare
from recovery_pipeline import OBJDUMP
from effective_outcomes import effective_identity
research=ROOT/'docs/attempts/research-20260924-replay-strcmp-context'
base='build/tu-context/game-replay/treplay-post-generated-header-20260924/overlay/src/replay.c'
order=read_json(research/'accepted-emission-order.json')
variants={'baseline':'my-strcmp-baseline.c','outer_equal_switch':'my-strcmp-outer-equal-switch.c'}
flags=['-fdump-tree-cfg','-fdump-tree-optimized','-fdump-rtl-expand','-fdump-rtl-bbro','-fdump-rtl-peephole2']
summary={'scope':'Byte-neutral pass diagnostics on accepted Treplay_post-header TU; diagnostic dump flags only.', 'base_sha256':identity(ROOT/base)['sha256'],'diagnostic_flags':flags,'variants':[]}
for name,body in variants.items():
 label='replay-strcmp-pass-'+name
 spec={'research_base':base,'order':order,'bodies':{'my_strcmp':f'docs/attempts/research-20260924-replay-strcmp-context/{body}'},'prototypes':'none'}
 text,edits,headers=ctx.build_text('game-replay','src/replay.c',spec)
 out,ref,build,proc=ctx.compile_overlay('game-replay','src/replay.c',text,label,dumps=True,headers=headers,extra_flags=flags)
 if proc.returncode: raise RuntimeError(proc.stderr)
 report=compare(out/'unit.o',ref['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
 write_json(out/'comparison.json',report)
 function=next(x for x in report['functions'] if x['name']=='my_strcmp')
 dump_files=sorted(p.name for p in out.glob('replay.c.*') if p.suffix not in ('.o',))
 summary['variants'].append({'name':name,'label':label,'object':identity(out/'unit.o'),'strict_status':function['status'],'size':function.get('candidate_size'),'first_difference':function.get('first_difference'),'effective_identity':effective_identity(function),'peer_matches':report.get('function_matches'),'dump_files':dump_files,'compile_flags':build['flags'],'compile_command':build['command']})
write_json(research/'pass-dump-summary.json',summary)
print(json.dumps(summary,indent=2))

