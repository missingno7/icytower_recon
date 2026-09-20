"""Serialized publication with exception rollback and durable interruption recovery."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED


def durable_snapshot(backup,tree,journal,root):
    if journal.exists(): raise ValueError('Unrecovered publication journal: '+str(journal))
    root=root.resolve(); tree=tree.resolve()
    manifest={'root':str(root),'tree':tree.relative_to(root).as_posix(),'files':[]}
    pending=journal.with_suffix('.pending')
    journal.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(pending,'w',compression=ZIP_STORED) as archive:
        for index,(path,data) in enumerate(backup.items()):
            relative=path.resolve().relative_to(root).as_posix(); key='files/'+str(index)
            manifest['files'].append({'path':relative,'entry':key})
            archive.writestr(key,data)
        archive.writestr('manifest.json',json.dumps(manifest))
    with pending.open('r+b') as stream: os.fsync(stream.fileno())
    os.replace(pending,journal)


def restore_journal(journal,root,tree,allowed_files):
    root=root.resolve(); tree=tree.resolve()
    allowed={p.resolve() for p in allowed_files}
    with ZipFile(journal) as archive:
        manifest=json.loads(archive.read('manifest.json'))
        if Path(manifest['root']).resolve()!=root or (root/manifest['tree']).resolve()!=tree:
            raise ValueError('Journal belongs to a different workspace')
        backup={}
        for row in manifest['files']:
            path=(root/row['path']).resolve()
            if not path.is_relative_to(root) or not (path in allowed or path.is_relative_to(tree)):
                raise ValueError('Journal path is outside publication scope')
            if path in backup: raise ValueError('Duplicate journal path')
            backup[path]=archive.read(row['entry'])
    # Validate and load the entire archive before touching any destination.
    restore(backup,tree)
    journal.unlink()


def restore(backup,tree):
    for p in tree.rglob('*'):
        if p.is_file() and p.resolve() not in backup: p.unlink()
    for p,data in backup.items():
        p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)


@contextmanager
def publication(paths,tree,journal=None,root=None):
    backup={p.resolve():p.read_bytes() for p in paths if p.is_file()}
    if journal is not None: durable_snapshot(backup,tree,journal,root)
    try:
        yield
    except BaseException:
        restore(backup,tree)
        if journal is not None: journal.unlink()
        raise
    else:
        if journal is not None: journal.unlink()
