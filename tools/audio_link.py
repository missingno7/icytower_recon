"""Link reconstructed logg and real Xiph/Allegro archives; do not execute."""
from common import ROOT, identity, read_json, run, write_json
from build import COMPILERS, compile_target, verify_inputs

def main():
    compiler='tdm-2'
    verify_inputs(compiler)
    tc=COMPILERS[compiler]
    xdir=ROOT/'build/xiph'/compiler
    x=read_json(xdir/'build.json')
    adir=ROOT/'build/allegro'/compiler
    a=read_json(adir/'build.json')
    checks=[(x['plan'],ROOT/'third_party/xiph-build.json'),
            (x['source_lock'],ROOT/'third_party/xiph-lock.json'),
            (a['plan'],ROOT/'third_party/allegro-build.json'),
            (a['platform_header'],ROOT/'include/allegro/platform/alplatf.h'),
            (a['directx_lock'],ROOT/'third_party/directx-lock.json'),
            (a['archive'],adir/'liballeg.a')]
    for r in [x,a]:
        checks.extend([(r['toolchain_lock'],ROOT/'toolchain/lock.json'),
                       (r['candidate_toolchain_lock'],ROOT/'toolchain/tdm-2-lock.json')])
    checks.extend((r['identity'],xdir/name) for name,r in x['archives'].items())
    for expected,path in checks:
        if identity(path)!=expected: raise ValueError('Stale audio dependency: '+str(path))
    out=ROOT/'build/audio'/compiler
    out.mkdir(parents=True,exist_ok=True)
    exe=out/'audio-probe.exe'
    exe.unlink(missing_ok=True)
    (out/'build.json').unlink(missing_ok=True)
    obj,logg=compile_target('allegro-logg',dest=out/'logg',compiler=compiler)
    args=[tc/'bin/gcc.exe','-O2','-g','-mfpmath=387','-mwindows',
          'tools/audio_probe.c',obj,xdir/'libvorbisfile.a',xdir/'libvorbis.a',xdir/'libogg.a',adir/'liballeg.a',
          '-lkernel32','-luser32','-lgdi32','-lcomdlg32','-lole32','-ldinput','-lddraw',
          '-ldxguid','-lwinmm','-ldsound','-lm','-Wl,-Map,'+str(out/'link.map'),'-o',exe]
    run(args,toolchain=tc)
    write_json(out/'build.json',{'scope':'Synthetic audio link only; no game, layout or byte-equality claim',
               'executed':False,'executable':identity(exe),'source':identity(ROOT/'tools/audio_probe.c'),
               'xiph_report':identity(xdir/'build.json'),'allegro_report':identity(adir/'build.json'),
               'logg':logg,'command':[str(v) for v in args]})
    print('Linked',exe,'(not executed)')

if __name__=='__main__': main()
