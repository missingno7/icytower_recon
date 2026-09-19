"""Build every historical Allegro core CU, including data-only driver tables."""
import argparse
from common import ROOT, identity, read_json, run, write_json
from build import COMPILERS, verify_inputs

def build_library(compiler):
    verify_inputs(compiler)
    tc=COMPILERS[compiler]
    plan=read_json(ROOT/'third_party/allegro-build.json')
    out=ROOT/'build/allegro'/compiler
    out.mkdir(parents=True,exist_ok=True)
    archive=out/'liballeg.a'
    archive.unlink(missing_ok=True)
    (out/'build.json').unlink(missing_ok=True)
    records=[]
    for i,unit in enumerate(plan['units']):
        obj=out/unit['object']
        obj.unlink(missing_ok=True)
        args=[tc/'bin/gcc.exe',*plan['configuration'],'-Iinclude','-Ithird_party/allegro-4.4.1/include','-Ithird_party/dx80_mgw/include',
              '-c',unit['source'],'-o',obj]
        try:
            run(args,toolchain=tc)
        except RuntimeError as error:
            write_json(out/'failure.json',{'unit':unit,'command':[str(x) for x in args],'error':str(error),'completed':records})
            raise
        records.append({**unit,'object_path':obj.relative_to(ROOT).as_posix(),'object_identity':identity(obj),
                        'source_identity':identity(ROOT/unit['source']),'command':[str(x) for x in args]})
        if (i+1)%20==0: print(f'Compiled {i+1}/{len(plan["units"])} Allegro CUs',flush=True)
    command=[tc/'bin/ar.exe','rcs',archive,*[ROOT/r['object_path'] for r in records]]
    run(command,toolchain=tc)
    run([tc/'bin/ar.exe','t',archive],out/'archive-members.txt',toolchain=tc)
    write_json(out/'build.json',{'compiler':compiler,'plan':identity(ROOT/'third_party/allegro-build.json'),
               'toolchain_lock':identity(ROOT/'toolchain/lock.json'),
               'candidate_toolchain_lock':identity(ROOT/'toolchain'/f'{compiler}-lock.json') if compiler!='tdm-1' else None,
               'platform_header':identity(ROOT/'include/allegro/platform/alplatf.h'),
               'directx_lock':identity(ROOT/'third_party/directx-lock.json'),
               'units':records,'archive':identity(archive),'archive_command':[str(x) for x in command]})
    (out/'failure.json').unlink(missing_ok=True)
    print('Built',archive,flush=True)
    return archive

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiler',choices=list(COMPILERS),default='tdm-2')
    build_library(ap.parse_args().compiler)
