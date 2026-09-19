"""Import a pinned local copy of Allegro's historical MinGW DirectX SDK."""
import zipfile
from pathlib import PurePosixPath
from common import ROOT, identity, write_json

archive=ROOT/'third_party/dx80_mgw.zip'
expected='4300411c0acd06f3ed7571d25e5e2a228a879e661a6569ee431343007a07f98e'
if identity(archive)['sha256']!=expected:
    raise ValueError('Unexpected DirectX archive hash')
destination=ROOT/'third_party/dx80_mgw'
files=[]
with zipfile.ZipFile(archive) as z:
    for member in z.infolist():
        name=PurePosixPath(member.filename)
        if name.is_absolute() or '..' in name.parts or ':' in member.filename or '\\' in member.filename:
            raise ValueError('Unsafe archive path')
        if member.is_dir(): continue
        target=destination.joinpath(*name.parts)
        data=z.read(member)
        if target.exists() and target.read_bytes()!=data:
            raise ValueError('Existing DirectX input differs: '+str(target))
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        files.append({'path':target.relative_to(ROOT).as_posix(),**identity(target)})
write_json(ROOT/'third_party/directx-lock.json',{
    'url':'https://liballeg.org/files/dx80_mgw.zip',
    'listing':'https://liballeg.org/old.html',
    'archive':identity(archive),'hash_status':'Observed download hash, not a publisher checksum',
    'scope':'Candidate historical headers; original SDK identity unproven. Bundled libraries are not used.',
    'files':files})
print('Imported',len(files),'DirectX files')
