"""Import pinned PNG development headers and derive a runtime import library.

The game uses the user-supplied GnuWin32 libpng3.dll at runtime.  The
original import archive has not been recovered, so this tool derives a
candidate MinGW archive from that DLL's named export table.  It never uses the
original game executable and records that limitation in png-lock.json.
"""
import struct
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

from common import ROOT, identity, run, write_json
from build import COMPILERS


DEPENDENCIES = (
    {
        'name': 'libpng-1.2.34',
        'archive': ROOT / 'third_party/archives/lpng1234.zip',
        'url': 'https://downloads.sourceforge.net/project/libpng/libpng12/older-releases/1.2.34/lpng1234.zip',
        'sha256': 'd9678327a122b0bf1f0dfa664982e8545226a78add5ffbf6e669431ce7e19e9c',
        'destination': ROOT / 'third_party/libpng-1.2.34',
        'root': 'lpng1234',
        'kind': 'zip',
    },
    {
        'name': 'zlib-1.2.3',
        'archive': ROOT / 'third_party/archives/zlib-1.2.3.tar.gz',
        'url': 'https://zlib.net/fossils/zlib-1.2.3.tar.gz',
        'sha256': '1795c7d067a43174113fdf03447532f373e1c6c57c08d61d9e4e9be5e244b05e',
        'destination': ROOT / 'third_party/zlib-1.2.3',
        'root': 'zlib-1.2.3',
        'kind': 'tar',
    },
)


def checked_members(dep):
    archive = dep['archive']
    actual = identity(archive)
    if actual['sha256'] != dep['sha256']:
        raise ValueError('Unexpected archive hash: ' + str(archive))
    if dep['kind'] == 'zip':
        with zipfile.ZipFile(archive) as z:
            return [(PurePosixPath(member.filename), z.read(member))
                    for member in z.infolist() if not member.is_dir()]
    with tarfile.open(archive, 'r:gz') as t:
        return [(PurePosixPath(member.name), t.extractfile(member).read())
                for member in t.getmembers() if member.isfile()]


def import_source(dep):
    files = []
    for member, data in checked_members(dep):
        if member.is_absolute() or '..' in member.parts or ':' in str(member):
            raise ValueError('Unsafe archive path: ' + str(member))
        if not member.parts or member.parts[0] != dep['root']:
            raise ValueError('Unexpected archive root: ' + str(member))
        relative = Path(*member.parts[1:])
        if not relative.parts:
            continue
        target = dep['destination'] / relative
        if target.exists() and target.read_bytes() != data:
            raise ValueError('Existing imported source differs: ' + str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({'path': target.relative_to(ROOT).as_posix(), **identity(target)})
    return {'name': dep['name'], 'url': dep['url'], 'archive': identity(dep['archive']),
            'archive_sha256_expected': dep['sha256'],
            'hash_status': 'Observed publisher download hash; no publisher checksum found.',
            'files': sorted(files, key=lambda row: row['path'])}


def rva_offset(data, pe, rva):
    sections = struct.unpack_from('<H', data, pe + 6)[0]
    optional_size = struct.unpack_from('<H', data, pe + 20)[0]
    section = pe + 24 + optional_size
    for _ in range(sections):
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from('<IIII', data, section + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_offset + rva - virtual_address
        section += 40
    raise ValueError('RVA is outside every PE section: %#x' % rva)


def dll_exports(dll):
    data = dll.read_bytes()
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('Not a PE file: ' + str(dll))
    optional = pe + 24
    magic = struct.unpack_from('<H', data, optional)[0]
    directory = optional + (96 if magic == 0x10b else 112)
    export_rva = struct.unpack_from('<I', data, directory)[0]
    export = rva_offset(data, pe, export_rva)
    number_names = struct.unpack_from('<I', data, export + 24)[0]
    names_rva = struct.unpack_from('<I', data, export + 32)[0]
    names = []
    for index in range(number_names):
        name_rva = struct.unpack_from('<I', data, rva_offset(data, pe, names_rva) + 4 * index)[0]
        start = rva_offset(data, pe, name_rva)
        end = data.index(b'\0', start)
        names.append(data[start:end].decode('ascii'))
    if not names or any(not name.isidentifier() for name in names):
        raise ValueError('Unexpected DLL export names')
    return names


def make_import_library(compiler='tdm-2'):
    dll = ROOT / 'assets/libpng3.dll'
    names = dll_exports(dll)
    out = ROOT / 'third_party/libpng-1.2.34'
    definition = out / 'libpng3-derived.def'
    library = out / 'libpng3.a'
    definition.write_text('LIBRARY libpng3.dll\nEXPORTS\n' + ''.join('    ' + name + '\n' for name in names),
                          encoding='ascii')
    library.unlink(missing_ok=True)
    tc = COMPILERS[compiler]
    run([tc / 'bin/dlltool.exe', '--input-def', definition, '--output-lib', library], toolchain=tc)
    return {'runtime_dll': identity(dll), 'exports': names,
            'definition': identity(definition), 'import_library': identity(library),
            'scope': 'Candidate link input derived from the user-supplied runtime DLL; original import archive identity remains unresolved.'}


def main():
    dependencies = [import_source(dep) for dep in DEPENDENCIES]
    candidate = make_import_library()
    write_json(ROOT / 'third_party/png-lock.json', {
        'schema': 1,
        'dependencies': dependencies,
        'link_candidate': candidate,
        'scope': 'Historical libpng/zlib headers plus a runtime-derived import candidate. This does not establish original libpng or import-archive identity.',
    })
    print('Imported libpng 1.2.34 and zlib 1.2.3; derived libpng3.a with', len(candidate['exports']), 'named exports')


if __name__ == '__main__':
    main()
