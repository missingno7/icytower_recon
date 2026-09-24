import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_context import resolved_candidate
D=ROOT/'docs/attempts/research-20260924-fldads-threadmain'
files={'baseline':'docs/current/reports/game-fld-adspot.json','base-control':'docs/attempts/research-20260924-fldads-threadmain/base-control-comparison.json','httpresponse-dwarf-types':'docs/attempts/research-20260924-fldads-threadmain/httpresponse-dwarf-types-comparison.json','update-cache-size_t':'docs/attempts/research-20260924-fldads-threadmain/update-cache-size_t-comparison.json','start-after-threadmain':'docs/attempts/research-20260924-fldads-threadmain/start-after-threadmain-comparison.json','start-after-no-forward-decls':'docs/attempts/research-20260924-fldads-threadmain/start-after-threadmain-no-forward-decls-comparison.json','update-local-random-after':'docs/attempts/research-20260924-fldads-threadmain/update-local-before-csv-random-after-threadmain-comparison.json'}
rows=[]
for label,rel in files.items():
 p=ROOT/rel
 if not p.exists(): continue
 d=json.loads(p.read_text()); fs={x['name']:x for x in d['functions']}; row={'label':label}
 for name in ['fldads_threadmain','fldads_get_random_ad']:
  f=fs[name]; b=resolved_candidate(f)
  row[name]={'status':f['status'],'candidate_size':f.get('candidate_size'),'resolved_sha256':hashlib.sha256(b.encode() if isinstance(b,str) else b).hexdigest() if b is not None else None,'resolved_size':len(b) if b is not None else None}
 rows.append(row)
(D/'effective-output-hashes.json').write_text(json.dumps(rows,indent=2)); print(json.dumps(rows,indent=2))
