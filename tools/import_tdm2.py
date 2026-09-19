"""Export the already-archived second toolchain without replacing tdm-1."""
import argparse
from common import ROOT, identity, read_json, run, write_json
from bootstrap import copy_checked
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--research',type=Path,required=True)
    a=ap.parse_args()
    archived=a.research/'third_party/tdm-gcc-4.4.1-tdm-2'
    dest=ROOT/'toolchain/tdm-gcc-4.4.1-tdm-2'
    manifest=read_json(ROOT/'evidence/research/third_party/MANIFEST.json')
    dep=next(d for d in manifest['dependencies'] if d['name']=='tdm-gcc-4.4.1-tdm-2')
    archives=[]
    for entry in dep['files']:
        matches=list(archived.rglob(entry['name']))
        if not matches: raise ValueError('Archive missing: '+entry['name'])
        if any(identity(p)['sha256']!=entry['sha256'] for p in matches): raise ValueError('Archive copies disagree')
        actual=identity(matches[0])
        if actual['sha256']!=entry['sha256']: raise ValueError('Archive hash differs')
        archives.append({'source':str(matches[0]),**actual})
    files=[]
    for path in sorted((archived/'mingw32').rglob('*')):
        if not path.is_file(): continue
        output=dest/path.relative_to(archived/'mingw32')
        copy_checked(path,output)
        files.append({'path':output.relative_to(ROOT).as_posix(),'source':str(path),**identity(output)})
    lock={'name':'tdm-2','archives':archives,'inputs':files,
          'gcc_version':run([dest/'bin/gcc.exe','--version'],toolchain=dest).splitlines()[0],
          'provenance':'Existing research archive, independently hash-verified; distinct candidate, not a replacement for tdm-1'}
    target=ROOT/'toolchain/tdm-2-lock.json'
    if target.exists() and read_json(target)!=lock: raise ValueError('Existing tdm-2 lock differs')
    write_json(target,lock)
    print(lock['gcc_version'],len(files),'files pinned')

if __name__=='__main__': main()
