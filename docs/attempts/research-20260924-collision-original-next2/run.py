import hashlib, json, subprocess, sys
from pathlib import Path

root=Path(__file__).resolve().parents[3]
here=Path(__file__).resolve().parent
name='handle_player_collision_original'
src=(root/'src/main.c').read_text(encoding='utf-8')
start=src.index(f'void {name}(int lastX, int lastY)\n{{')
end=src.index('\nvoid fadeIn(',start)
body=src[start:end]
old='''    int solid1;\n    int solid2;\n\n    solid1=is_solid(&map,(int)ply[player_id]->x-11,(int)ply[player_id]->y);\n    solid2=is_solid(&map,(int)ply[player_id]->x+11,(int)ply[player_id]->y);'''
assert body.count(old)==1
forms={
'reverse':'''    int solid2;\n    int solid1;\n\n    solid1=is_solid(&map,(int)ply[player_id]->x-11,(int)ply[player_id]->y);\n    solid2=is_solid(&map,(int)ply[player_id]->x+11,(int)ply[player_id]->y);''',
'combined':'''    int solid1, solid2;\n\n    solid1=is_solid(&map,(int)ply[player_id]->x-11,(int)ply[player_id]->y);\n    solid2=is_solid(&map,(int)ply[player_id]->x+11,(int)ply[player_id]->y);''',
'initialized':'''    int solid1=is_solid(&map,(int)ply[player_id]->x-11,(int)ply[player_id]->y);\n    int solid2=is_solid(&map,(int)ply[player_id]->x+11,(int)ply[player_id]->y);''',
'late_solid2':'''    int solid1;\n\n    solid1=is_solid(&map,(int)ply[player_id]->x-11,(int)ply[player_id]->y);\n    int solid2;\n    solid2=is_solid(&map,(int)ply[player_id]->x+11,(int)ply[player_id]->y);'''}
labels=[]
for key,repl in forms.items():
 p=here/f'{key}.c'; p.write_text(body.replace(old,repl),encoding='utf-8',newline='')
 labels.append((key,p))
manifest={'head':subprocess.check_output(['git','-c','safe.directory=D:/Prog/icytower_recon','rev-parse','HEAD'],cwd=root,text=True).strip(),'source_sha256':hashlib.sha256(src.encode()).hexdigest(),'order':'historical','prototypes':'none','compiler':'tdm-2 GCC 4.4.1 -O2','prediction_before_compile':{'question':'Does function-scope local declaration identity/order/start change EAX/EDX ownership at target +0xcd and preserve 64 exact peers?','if_match':'Declaration liveness/order is causal; investigate the first pass and strict function outcome.','if_collapse':'This declaration family does not explain the residue; stop spelling edits and escalate to GCC pass/context evidence.'},'variants':{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in labels}}
(here/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
probe_dir=root/'docs/attempts/tu-context/game-main'
all_labels=['research-collision-original-decl-control-20260924']+[f'research-collision-original-decl-{k}-20260924' for k,_ in labels]
for i,label in enumerate(all_labels):
 receipt=probe_dir/f'{label}.json'
 if not receipt.exists():
  cmd=[sys.executable,'tools/tu_context_probe.py','game-main','src/main.c',label,'--order','historical','--no-prototypes','--no-dumps','--focus',name]
  if i: cmd += ['--body',f'{name}={labels[i-1][1].relative_to(root).as_posix()}']
  r=subprocess.run(cmd,cwd=root,text=True,capture_output=True)
  (here/f'{label}.log').write_text(r.stdout+r.stderr,encoding='utf-8')
  if r.returncode: raise SystemExit(f'{label}: exit {r.returncode}')
print(json.dumps({'labels':all_labels,'probe_dir':str(probe_dir)},indent=2))
