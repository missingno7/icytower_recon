"""Real link of recovered game CUs plus historical Allegro, no original input."""
import argparse
from common import ROOT, identity, read_json, run, write_json
from build import COMPILERS, verify_inputs, compile_target

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiler',choices=list(COMPILERS),default='tdm-2')
    a=ap.parse_args()
    verify_inputs(a.compiler)
    tc=COMPILERS[a.compiler]
    libdir=ROOT/'build/allegro'/a.compiler
    library=libdir/'liballeg.a'
    lb=read_json(libdir/'build.json')
    if identity(library)!=lb['archive']: raise ValueError('Library differs from build report')
    if lb['plan']!=identity(ROOT/'third_party/allegro-build.json'): raise ValueError('Stale library plan')
    if lb['platform_header']!=identity(ROOT/'include/allegro/platform/alplatf.h'): raise ValueError('Stale platform header')
    if lb['directx_lock']!=identity(ROOT/'third_party/directx-lock.json'): raise ValueError('Stale DirectX lock')
    if lb['toolchain_lock']!=identity(ROOT/'toolchain/lock.json'): raise ValueError('Stale toolchain lock')
    if a.compiler!='tdm-1' and lb['candidate_toolchain_lock']!=identity(ROOT/'toolchain'/f'{a.compiler}-lock.json'):
        raise ValueError('Stale candidate toolchain lock')
    out=ROOT/'build/integration'/a.compiler
    out.mkdir(parents=True,exist_ok=True)
    exe=out/'integration-probe.exe'
    exe.unlink(missing_ok=True)
    (out/'build.json').unlink(missing_ok=True)
    objects=[]
    reports=[]
    for target in ['game-beta','game-control','game-csv','game-directories','game-timer','game-stars']:
        obj,report=compile_target(target,dest=out/target,compiler=a.compiler)
        objects.append(obj)
        reports.append(report)
    args=[tc/'bin/gcc.exe','-O2','-g','-mfpmath=387','-DALLEGRO_STATICLINK',
          '-Iinclude','-Ithird_party/allegro-4.4.1/include','-mwindows',*objects,
          'tools/integration_probe.c',library,'-lkernel32','-luser32','-lgdi32','-lcomdlg32',
          '-lole32','-ldinput','-lddraw','-ldxguid','-lwinmm','-ldsound',
          '-Wl,-Map,'+str(out/'link.map'),'-Wl,--cref','-o',exe]
    run(args,toolchain=tc)
    run([tc/'bin/objdump.exe','-x',exe],out/'pe.txt',toolchain=tc)
    write_json(out/'build.json',{'scope':'Synthetic main; recovered beta/control/csv/directories/timer CUs and upstream library; NOT icytower15.exe',
               'compiler':a.compiler,'command':[str(x) for x in args], 'executable':identity(exe),
               'library_report':identity(libdir/'build.json'),'source':identity(ROOT/'tools/integration_probe.c'),
               'game_objects':reports,'executed':False})
    print('Linked',exe,'(not executed)')

if __name__=='__main__': main()
