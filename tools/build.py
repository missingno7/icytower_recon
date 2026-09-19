"""Compile real historical COFF objects without the original EXE or oracle.

The selected sources are complete CUs; unknown skeletons cannot be targets.
"""
import argparse
from pathlib import Path
from common import ROOT, TC, identity, read_json, run, write_json

TARGETS={
    'game-control': {'source':'src/control.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\control.c','default':'-O2'},
    'game-timer': {'source':'src/timer.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\timer.c','default':'-O2'},
    'allegro-timer': {'source':'third_party/allegro-4.4.1/src/timer.c','historical_cu':'C:\\Lib\\allegro4\\src\\timer.c','default':'-O2'},
    'allegro-color': {'source':'third_party/allegro-4.4.1/src/color.c','historical_cu':'C:\\Lib\\allegro4\\src\\color.c','default':'-O2'},
    'allegro-blit': {'source':'third_party/allegro-4.4.1/src/blit.c','historical_cu':'C:\\Lib\\allegro4\\src\\blit.c','default':'-O2'},
}
COMPILERS={'tdm-1':TC,'tdm-2':ROOT/'toolchain/tdm-gcc-4.4.1-tdm-2'}

def verify_inputs(compiler='tdm-1'):
    lock=read_json(ROOT/'toolchain/lock.json')
    for row in lock['inputs']:
        # Runtime assets do not participate in object generation.
        if row['path'].startswith('assets/'): continue
        actual=identity(ROOT/row['path'])
        if actual!={k:row[k] for k in ['size','sha256']}:
            raise ValueError('Build input hash differs: '+row['path'])
    xiph=ROOT/'third_party/xiph-lock.json'
    if xiph.exists():
        for dependency in read_json(xiph)['dependencies']:
            for row in dependency['files']:
                if identity(ROOT/row['path'])!={k:row[k] for k in ['size','sha256']}:
                    raise ValueError('Xiph input hash differs: '+row['path'])
    if compiler!='tdm-1':
        for row in read_json(ROOT/'toolchain'/f'{compiler}-lock.json')['inputs']:
            if identity(ROOT/row['path'])!={k:row[k] for k in ['size','sha256']}:
                raise ValueError('Candidate toolchain input differs: '+row['path'])
    dx=ROOT/'third_party/directx-lock.json'
    if dx.exists():
        for row in read_json(dx)['files']:
            if identity(ROOT/row['path'])!={k:row[k] for k in ['size','sha256']}:
                raise ValueError('DirectX input differs: '+row['path'])

def compile_target(target,flags=None,dest=None,compiler='tdm-1'):
    tc=COMPILERS[compiler]
    config=TARGETS[target]
    flags=flags or [config['default']]
    out=dest or ROOT/'build/objects'/compiler/target
    out.mkdir(parents=True,exist_ok=True)
    obj=out/'unit.o'
    # Remove the old object before invoking the compiler: failed builds must
    # not leave a stale successful object in the expected output location.
    obj.unlink(missing_ok=True)
    (out/'build.json').unlink(missing_ok=True)
    args=[tc/'bin/gcc.exe',*flags,'-g','-mfpmath=387','-DALLEGRO_STATICLINK',
          '-Iinclude','-Ithird_party/allegro-4.4.1/include','-MMD','-MF',out/'unit.d',
          '-c',config['source'],'-o',obj]
    run(args,toolchain=tc)
    run([tc/'bin/objdump.exe','-drt',obj],out/'object.txt',toolchain=tc)
    # Record every directly maintained source/config header too. Toolchain
    # and upstream files are individually pinned by toolchain/lock.json.
    local_files=[ROOT/config['source'],*sorted((ROOT/'include').rglob('*.h'))]
    report={'target':target,'historical_cu':config['historical_cu'],'flags':flags,'compiler':compiler,
            'command':[str(x) for x in args],'object':identity(obj),
            'toolchain_lock':identity(ROOT/'toolchain/lock.json'),
            'local_inputs':{p.relative_to(ROOT).as_posix():identity(p) for p in local_files}}
    if compiler!='tdm-1': report['candidate_toolchain_lock']=identity(ROOT/'toolchain'/f'{compiler}-lock.json')
    write_json(out/'build.json',report)
    return obj,report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('targets',nargs='*',choices=list(TARGETS),default=['game-timer'])
    ap.add_argument('--opt',default=None)
    ap.add_argument('--compiler',choices=list(COMPILERS),default='tdm-1')
    a=ap.parse_args()
    verify_inputs(a.compiler)
    for target in a.targets:
        obj,_=compile_target(target,[a.opt] if a.opt else None,compiler=a.compiler)
        print(obj)

if __name__=='__main__': main()
