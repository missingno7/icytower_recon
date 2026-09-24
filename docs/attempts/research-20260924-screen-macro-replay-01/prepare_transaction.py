import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from tu_context_probe import build_text,islands
here=Path(__file__).parent
overlay=ROOT/'build/tu-context/game-main/research-20260924-screen-macro-replay-01/overlay/src/main.c'
text=overlay.read_bytes().decode('cp1252')
item=next(i for i in islands(text) if i['name']=='force_create_profile')
body_path=here/'force_create_profile_screen_macro_replay.c'
body_path.write_text(text[item['def_start']:item['end']]+'\n',encoding='utf-8')
spec={'target':'game-main','source':'src/main.c','order':'historical','prototypes':'none','bodies':{'force_create_profile':body_path.relative_to(ROOT).as_posix()},'evidence':'Original force_create_profile null branches 0x40d904 and 0x40d8fc pass zero dimensions into the corresponding blit and rectfill calls; SCREEN_W/H in Allegro gfx.h:304-305 have this behavior. The locked full-TU probe from current source retained all 64 exact function peers; see research-20260924-screen-macro-replay-01/receipt.json and focused CFG captures.'}
spec_path=here/'tu-context-spec.json'
spec_path.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
rebuilt,edits,headers=build_text('game-main','src/main.c',spec)
result={'body':body_path.relative_to(ROOT).as_posix(),'spec':spec_path.relative_to(ROOT).as_posix(),'body_sha256':hashlib.sha256(body_path.read_bytes()).hexdigest(),'candidate_overlay_sha256':hashlib.sha256(overlay.read_bytes()).hexdigest(),'rebuilt_overlay_sha256':hashlib.sha256(rebuilt.encode('cp1252')).hexdigest(),'build_text_byte_identical':rebuilt==text,'header_edits':sorted(headers),'body_count':len(edits['bodies']),'historical_order_count':len(edits['order'])}
(here/'tu-context-reproduction.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
