import json, sys
from pathlib import Path
sys.path.insert(0, 'tools')
from effective_outcomes import effective_identity
root=Path('docs/attempts/tu-context/game-main')
labels=['init-decl-count-control-20260924','init-game-scope-gp-i-dwarf-20260924']
rows={}
for label in labels:
 r=json.loads((root/(label+'.json')).read_text())
 report=json.loads(Path(r['report_path']).read_text())
 fs={f['name']:f for f in report['functions']}
 exact={f['name'] for f in report['functions'] if f['status']=='FUNCTION_MATCH'}
 target=fs['init_game']
 rows[label]={'source_sha256':r['source_identity']['sha256'],'overlay_sha256':r['overlay_identity'],'object_sha256':r['compiled_object_identity']['sha256'],'effective_sha256':effective_identity(target),'exact_count':len(exact),'exact_peers':sorted(exact),'init_game':{'status':target['status'],'size':target['candidate_size'],'original_size':target['original_size'],'first_difference':target.get('first_difference'),'diff_bytes':len(target.get('difference_offsets',[])),'unequal_relocations':sum(not x.get('equal',False) for x in target['relocations']),'candidate_instructions':len(target['instructions']),'relocations':len(target['relocations'])}}
base=rows[labels[0]]['exact_peers']; variant=rows[labels[1]]['exact_peers']
rows['peer_delta']={'gained':sorted(set(variant)-set(base)),'lost':sorted(set(base)-set(variant))}
Path('docs/attempts/research-20260924-init-game-scope-next/results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({k:v for k,v in rows.items() if k!='init-decl-count-control-20260924' or True},indent=2))
