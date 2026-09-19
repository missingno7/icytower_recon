"""Fetch exact historical Xiph source releases and validate publisher hashes."""
import io
import tarfile
import urllib.request
from common import ROOT, identity, read_json, sha, write_json

def fetch(url):
    with urllib.request.urlopen(url,timeout=45) as response:
        return response.read(),response.url

def main():
    archives=ROOT/'third_party/archives'
    archives.mkdir(parents=True,exist_ok=True)
    records=[]
    for family,release in [('vorbis','libvorbis-1.2.0'),('ogg','libogg-1.1.3')]:
        base=f'https://downloads.xiph.org/releases/{family}/'
        filename=release+'.tar.gz'
        sums,sums_url=fetch(base+'SHA256SUMS')
        expected=next(line.split()[0] for line in sums.decode().splitlines() if line.split()[-1].lstrip('*')==filename)
        archive=archives/filename
        if archive.exists():
            data=archive.read_bytes()
            final_url=base+filename
        else:
            data,final_url=fetch(base+filename)
        if sha(data)!=expected: raise ValueError('Publisher SHA-256 mismatch: '+filename)
        archive.write_bytes(data)
        sums_path=archives/(family+'-SHA256SUMS')
        sums_path.write_bytes(sums)
        files=[]
        with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.isdir(): continue
                if not member.isfile(): raise ValueError('Nonregular tar entry: '+member.name)
                dest=(ROOT/'third_party'/member.name).resolve()
                dest.relative_to((ROOT/'third_party'/release).resolve())
                contents=tar.extractfile(member).read()
                if dest.exists() and dest.read_bytes()!=contents:
                    raise ValueError('Existing source differs: '+str(dest))
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(contents)
                files.append({'path':dest.relative_to(ROOT).as_posix(),**identity(dest)})
        records.append({'name':release,'requested_url':base+filename,'resolved_url':final_url,
                        'archive':identity(archive),'publisher_sha256':expected,'checksum_url':sums_url,
                        'license':release+'/COPYING','files':files})
        print(release,expected,len(files),'files')
    lock=ROOT/'third_party/xiph-lock.json'
    if lock.exists():
        # Redirect hosts may change; never silently accept changed contents.
        previous=read_json(lock)
        for old,new in zip(previous['dependencies'],records):
            if old['archive']!=new['archive'] or old['files']!=new['files']:
                raise ValueError('Xiph input lock changed')
        return
    write_json(lock,{'dependencies':records,'libogg_status':'1.1.3 candidate; original objects used GCC 4.2.1-sjlj (mingw32-2), not the primary toolchain'})

if __name__=='__main__': main()
