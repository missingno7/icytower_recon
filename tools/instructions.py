"""Decode with the identified objdump; never scan operand bytes as opcodes."""
import re
from common import run, sha


def decode(path, objdump, start=None, stop=None):
    args = [objdump, '-d', '-w']
    if start is not None:
        args += ['--start-address=%d' % start, '--stop-address=%d' % stop]
    args.append(path)
    rows = []
    section = None
    for line in run(args).splitlines():
        if line.startswith('Disassembly of section '):
            section = line.split('section ', 1)[1].rstrip(':')
        match = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s)+)\s*(.*)', line)
        if match and section == '.text':
            raw = bytes.fromhex(match[2])
            asm = match[3].strip()
            rows.append({'address': int(match[1], 16), 'bytes': raw.hex(),
                         'mnemonic': asm.split()[0] if asm else '', 'assembly': asm})
    return rows


def window(rows, address, radius=4):
    if not rows:
        return []
    nearest = min(range(len(rows)), key=lambda i: abs(rows[i]['address'] - address))
    return rows[max(0, nearest-radius):nearest+radius+1]


def affected_instructions(row):
    differences=set(row.get('difference_offsets',[]))
    base=row.get('candidate_offset',0)
    return [i for i in row.get('instructions',[]) if any(p in differences for p in range(
        i['address']-base,i['address']-base+len(bytes.fromhex(i['bytes']))))]


def zero_clear_projection(raw, rows, protected_targets=(), forbidden_ranges=()):
    """Candidate-to-candidate scheduling evidence, NEVER original matching.

    Canonicalize only adjacent, independent XOR r32,r32 clears, excluding ESP/EBP,
    internal CFG entry points, relocation targets and functions with indirect jumps.
    All other bytes, including padding and operands, remain in the fingerprint.
    """
    targets=set(protected_targets)
    for row in rows:
        if row['mnemonic'].startswith(('j','call','loop')):
            m=re.match(r'\S+\s+([0-9a-f]+)(?:\s|$)',row['assembly'])
            if m: targets.add(int(m[1],16))
    def clear(row):
        code=bytes.fromhex(row['bytes']); off=row['address']
        if any(a<=off<b for a,b in forbidden_ranges): return False
        return (len(code)==2 and raw[off:off+2]==code and code[0]==0x31 and code[1]>=0xc0
                and (code[1]&7)==((code[1]>>3)&7) and (code[1]&7) not in (4,5))
    canonical=bytearray(raw); blocks=[]; pos=0
    while pos<len(rows):
        if not clear(rows[pos]): pos+=1; continue
        run_=[rows[pos]]; pos+=1
        while pos<len(rows) and clear(rows[pos]) and rows[pos]['address']==run_[-1]['address']+2:
            run_.append(rows[pos]); pos+=1
        start=run_[0]['address']; end=run_[-1]['address']+2
        if len(run_)<2 or any(start<t<end for t in targets): continue
        codes=[bytes.fromhex(i['bytes']) for i in run_]
        if len(set(codes))!=len(codes): continue
        canonical[start:end]=b''.join(sorted(codes))
        blocks.append({'start':start,'end':end,'original_bytes':raw[start:end].hex(),
                       'canonical_bytes':bytes(canonical[start:end]).hex(),'instructions':run_})
    return {'sha256':sha(canonical),'blocks':blocks,
            'scope':'Only candidate scheduling preservation; never FUNCTION_MATCH evidence.'}
