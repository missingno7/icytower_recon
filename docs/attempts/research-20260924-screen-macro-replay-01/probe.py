import difflib, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from common import read_json
from experiment import compare
from recovery_pipeline import OBJDUMP
from tu_context_probe import compile_overlay, peephole_finds
SOURCE=ROOT/'src/main.c'
text=SOURCE.read_bytes().decode('cp1252')
replacements=[
('        blit(bg,screen,0,0,0,0,gfx_driver->w,gfx_driver->h);','        blit(bg,screen,0,0,0,0,SCREEN_W,SCREEN_H);'),
('        rectfill(screen,0,0,gfx_driver->w,gfx_driver->h,makecol(0,0,0));','        rectfill(screen,0,0,SCREEN_W,SCREEN_H,makecol(0,0,0));')]
for a,b in replacements: assert text.count(a)==1,(a,text.count(a))
probe=text
for a,b in replacements: probe=probe.replace(a,b)
here=Path(__file__).parent
(here/'source.diff').write_text(''.join(difflib.unified_diff(text.splitlines(keepends=True),probe.splitlines(keepends=True),fromfile='src/main.c baseline',tofile='force_create_profile remaining screen macro calls')),encoding='utf-8')
out,ref,build,result=compile_overlay('game-main','src/main.c',probe,'research-20260924-screen-macro-replay-01',dumps=True)
if result.returncode: raise SystemExit(result.stderr)
report=compare(out/'unit.o',ref['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
def exact(r): return {f['name'] for f in r['functions'] if f['status']=='FUNCTION_MATCH'}
focus=['force_create_profile','draw_results','log2file','testWindowResolution','new_game','uninit_game','check_beta_tester']
functions={f['name']:f for f in report['functions']}
compact={'variant':'Only the two remaining direct gfx_driver width/height call argument pairs inside force_create_profile replaced by SCREEN_W/SCREEN_H; baseline already has first two SCREEN_W/H pairs.','baseline_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'historical_cu':ref['historical_cu'],'baseline_function_matches':ref['function_matches'],'candidate_function_matches':report['function_matches'],'exact_gains':sorted(exact(report)-exact(ref)),'exact_losses':sorted(exact(ref)-exact(report)),'focus':{n:{'status':functions[n]['status'],'candidate_size':functions[n]['candidate_size'],'historical_size':functions[n]['original_size']} for n in focus},'scratch':{x['function']:x['scratch'] for x in peephole_finds(out) if x['function'] in focus},'output':str(out.relative_to(ROOT)).replace('\\','/')}
(here/'receipt.json').write_text(json.dumps(compact,indent=2)+'\n',encoding='utf-8')
print(here/'receipt.json')
