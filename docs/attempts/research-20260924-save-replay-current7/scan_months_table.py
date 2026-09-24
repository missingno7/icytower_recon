from pathlib import Path
import struct

MONTHS = [b'Jan', b'Feb', b'Mar', b'Apr', b'May', b'Jun',
          b'Jul', b'Aug', b'Sep', b'Oct', b'Nov', b'Dec']

def scan(blob, off, size, base, name):
    hits = []
    sec = blob[off:off + size]
    for at in range(0, size - 48 + 1, 4):
        vals = struct.unpack_from('<12I', sec, at)
        names = []
        ok = True
        for value in vals:
            rel = value - base
            if rel < 0 or rel >= size:
                ok = False
                break
            end = sec.find(b'\0', rel, min(size, rel + 16))
            if end < 0:
                ok = False
                break
            names.append(sec[rel:end])
        if ok and names == MONTHS:
            hits.append({'offset': at, 'values': [hex(v) for v in vals]})
    print(name, 'months-table hits:', hits)

exe = Path('assets/icytower15.exe').read_bytes()
scan(exe, 0xD1E00, 0x8984, 0x4D4000, 'original PE .rdata (full-section scan; no code operand used)')
obj = Path('build/tu-context/game-replay/save-replay-current-typed-handle-20260924/unit.o').read_bytes()
scan(obj, 0x7604, 0x3C0, 0, 'candidate COFF .rdata (relocation addends are section-relative)')
