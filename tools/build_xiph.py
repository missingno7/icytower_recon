"""Build the 22 observed Xiph CUs from locked source, without verifier inputs."""
import argparse
from common import ROOT, identity, read_json, run, write_json
from build import COMPILERS, verify_inputs

def build_library(compiler='tdm-2'):
    verify_inputs(compiler)
    tc=COMPILERS[compiler]
    plan=read_json(ROOT/'third_party/xiph-build.json')
    out=ROOT/'build/xiph'/compiler
    out.mkdir(parents=True,exist_ok=True)
    (out/'build.json').unlink(missing_ok=True)
    for name in {u['archive'] for u in plan['units']}:
        (out/name).unlink(missing_ok=True)
    records=[]
    for unit in plan['units']:
        obj=out/unit['object']
        obj.unlink(missing_ok=True)
        args=[tc/'bin/gcc.exe',*plan['configuration'],
              '-Ithird_party/libvorbis-1.2.0/include','-Ithird_party/libogg-1.1.3/include',
              '-c',unit['source'],'-o',obj]
        try:
            run(args,toolchain=tc)
        except RuntimeError as error:
            write_json(out/'failure.json',{'unit':unit,'error':str(error),'completed':records})
            raise
        records.append({**unit,'source_identity':identity(ROOT/unit['source']),
                        'object_path':obj.relative_to(ROOT).as_posix(),
                        'object_identity':identity(obj),'command':[str(a) for a in args]})
        print('Compiled',unit['historical_cu'],flush=True)
    archives={}
    for name in sorted({u['archive'] for u in records}):
        args=[tc/'bin/ar.exe','rcs',out/name,*[ROOT/u['object_path'] for u in records if u['archive']==name]]
        run(args,toolchain=tc)
        run([tc/'bin/ar.exe','t',out/name],out/(name+'.members.txt'),toolchain=tc)
        archives[name]={'identity':identity(out/name),'command':[str(a) for a in args]}
    report={'scope':'Candidate archives, not proven historical object or text equality',
            'compiler':compiler,'plan':identity(ROOT/'third_party/xiph-build.json'),
            'source_lock':identity(ROOT/'third_party/xiph-lock.json'),
            'toolchain_lock':identity(ROOT/'toolchain/lock.json'),
            'candidate_toolchain_lock':identity(ROOT/'toolchain'/f'{compiler}-lock.json') if compiler!='tdm-1' else None,
            'units':records,'archives':archives}
    write_json(out/'build.json',report)
    (out/'failure.json').unlink(missing_ok=True)
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiler',choices=list(COMPILERS),default='tdm-2')
    build_library(ap.parse_args().compiler)
