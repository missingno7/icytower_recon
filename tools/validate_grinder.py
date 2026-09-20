"""Real acceptance examples; no game function bodies are manually solved here."""
import json
import subprocess
import sys
import time
from common import ROOT, identity, read_json, write_json, run
from build import COMPILERS, verify_inputs
from recovery_pipeline import CURRENT


def main():
    results=[]
    def command(args,expected):
        before=identity(ROOT/'src/recovery.json'); start=time.perf_counter()
        result=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True)
        row={'command':'python '+' '.join(args),'returncode':result.returncode,'expected_returncode':expected,
             'seconds':round(time.perf_counter()-start,3),'stdout':result.stdout,'stderr':result.stderr,
             'ledger_before':before,'ledger_after':identity(ROOT/'src/recovery.json')}
        results.append(row)
        history=ROOT/'docs/attempts/workflow-validation.jsonl'
        history.parent.mkdir(parents=True,exist_ok=True)
        with history.open('a',encoding='utf-8') as stream: stream.write(json.dumps(row,separators=(',',':'))+'\n')
        if result.returncode!=expected: raise RuntimeError(json.dumps(row,indent=2))
        if expected and row['ledger_before']!=row['ledger_after']: raise ValueError('Rejected operation changed ledger')
        print(row['command'],'=>',result.returncode,flush=True)
    ledger=read_json(ROOT/'src/recovery.json')
    examples=[('game-scroller','src/scroller.c','draw_scroller'),('game-map','src/map.c','add_floor'),('game-profile','src/profile.c','create_profile')]
    for target,source,name in examples:
        command(['tools/check_function.py',target,name],0 if ledger[source]['functions'][name]=='FUNCTION_MATCH' else 1)
    command(['tools/check_function.py','game-main','play_jump_sound'],0)
    command(['tools/grinder_task.py','begin','game-main','play_jump_sound'],1)
    unresolved=next(((target,name) for target,source,name in examples if ledger[source]['functions'][name]!='FUNCTION_MATCH'),None)
    if unresolved:
        command(['tools/promote_function.py',*unresolved],1)
    else:
        results.append({'check':'All example bodies have recovered; synthetic false-claim controls remain in test_grinder.py'})
    command(['tools/grinder_task.py','begin','game-map','getFloorData','--verify-only'],0)
    command(['tools/promote_function.py','game-map','getFloorData'],0)
    claim=ledger['src/main.c']['workflow']['play_jump_sound']['state']
    command(['tools/promote_function.py','game-main','play_jump_sound','--claim',claim],0)
    verify_inputs('tdm-2')
    headers=sorted((ROOT/'include/recovered').glob('*.h'))
    source=ROOT/'build/type-layout-check.c'
    source.write_text('\n'.join('#include "recovered/'+p.name+'"' for p in headers)+'\n')
    run([COMPILERS['tdm-2']/'bin/gcc.exe','-O2','-g','-DALLEGRO_STATICLINK','-Iinclude',
         '-Ithird_party/allegro-4.4.1/include','-c',source,'-o',ROOT/'build/type-layout-check.o'],toolchain=COMPILERS['tdm-2'])
    results.append({'check':'All generated headers compiled together with historical GCC; every layout assertion active','headers':len(headers),
                    'header_identities':{p.relative_to(ROOT).as_posix():identity(p) for p in headers}})
    write_json(CURRENT/'validation.json',{'scope':'Real FAST, exact gate, layout protection and rejected promotion. No additional function recovery claimed.', 'results':results})
    print('PASS: real grinder workflow validation')


if __name__=='__main__': main()
