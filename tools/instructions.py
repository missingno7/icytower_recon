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


def independent_write(raw, row, forbidden_ranges=()):
    """Decode one adjacent-run candidate from its verified bytes.

    Returns (destination, flag_writer) or None. Accepted encodings only:
      31 /r        xor r32,r32 with identical operands (register clear; writes flags)
      B8+r imm32   mov $imm32,r32
      C7 45 d8 imm32 / C7 85 d32 imm32   movl $imm32,disp(%ebp)
      C6 45 d8 imm8  / C6 85 d32 imm8    movb $imm8,disp(%ebp)
      66 C7 45 d8 imm16 / 66 C7 85 d32 imm16   movw $imm16,disp(%ebp)
    Every form writes exactly one destination with an immediate, reads only EBP as a
    base, and (except xor) leaves flags untouched. ESP/EBP are never destinations.
    """
    code=bytes.fromhex(row['bytes']); off=row['address']
    if any(a<=off<b for a,b in forbidden_ranges) or raw[off:off+len(code)]!=code: return None
    if len(code)==2 and code[0]==0x31 and code[1]>=0xc0 and (code[1]&7)==((code[1]>>3)&7):
        reg=code[1]&7
        return (('reg',reg),True) if reg not in (4,5) else None
    if len(code)==5 and 0xb8<=code[0]<=0xbf:
        reg=code[0]-0xb8
        return (('reg',reg),False) if reg not in (4,5) else None
    body=code[1:] if code[:1]==b'\x66' else code; width=2 if code[:1]==b'\x66' else None
    if body[:1]==b'\xc7': width=width or 4
    elif body[:1]==b'\xc6' and width is None: width=1
    else: return None
    if len(body)<2: return None
    if body[1]==0x45 and len(body)==3+width: disp=int.from_bytes(body[2:3],'little',signed=True)
    elif body[1]==0x85 and len(body)==6+width: disp=int.from_bytes(body[2:6],'little',signed=True)
    else: return None
    return (('ebp',disp,width),False)


def _disjoint(destinations):
    regs=[d for d in destinations if d[0]=='reg']; slots=[d for d in destinations if d[0]=='ebp']
    if len(set(regs))!=len(regs): return False
    spans=sorted((d[1],d[1]+d[2]) for d in slots)
    return all(a[1]<=b[0] for a,b in zip(spans,spans[1:]))


SWAP_CC={0x2:0x7,0x7:0x2,0x3:0x6,0x6:0x3,0xc:0xf,0xf:0xc,0xd:0xe,0xe:0xd,0x4:0x4,0x5:0x5}


def flag_reader(code):
    """Conservative: any instruction that may read EFLAGS (jcc, setcc, cmovcc, adc, sbb, rotates, pushf, lahf)."""
    if not code: return True
    b=code[0]
    if 0x70<=b<=0x7f or 0x10<=b<=0x15 or 0x18<=b<=0x1d or b in (0x9c,0x9f,0xd0,0xd1,0xd2,0xd3,0xe3): return True
    if b==0x0f and len(code)>1 and (0x40<=code[1]<=0x4f or 0x80<=code[1]<=0x8f or 0x90<=code[1]<=0x9f): return True
    if b in (0x80,0x81,0x83) and len(code)>1 and ((code[1]>>3)&7) in (2,3): return True
    return False


def compare_jump(raw, rows, index, targets_by_address):
    """Decode `cmp r/m32,r32` or `cmp r32,r/m32` followed by a swappable jcc whose flags die there.

    Returns (start, end, canonical_bytes) or None. Semantics: 39 /r computes rm-reg, 3b /r
    computes reg-rm; swapping the operands of the subtraction inverts a signed/unsigned
    ordering condition, so the pair is canonicalized to a fixed operand order.
    """
    cmp_row=rows[index]; code=bytes.fromhex(cmp_row['bytes']); off=cmp_row['address']
    if raw[off:off+len(code)]!=code or len(code)<2 or code[0] not in (0x39,0x3b): return None
    if index+1>=len(rows): return None
    jcc=rows[index+1]; jcode=bytes.fromhex(jcc['bytes'])
    if jcc['address']!=off+len(code) or raw[jcc['address']:jcc['address']+len(jcode)]!=jcode: return None
    if len(jcode)==2 and 0x70<=jcode[0]<=0x7f: cc=jcode[0]&0xf; rel=int.from_bytes(jcode[1:2],'little',signed=True)
    elif len(jcode)==6 and jcode[0]==0x0f and 0x80<=jcode[1]<=0x8f: cc=jcode[1]&0xf; rel=int.from_bytes(jcode[2:6],'little',signed=True)
    else: return None
    if cc not in SWAP_CC: return None
    end=jcc['address']+len(jcode); target=end+rel
    # Flags must die at this jump: neither the fall-through nor the target instruction reads them.
    following=rows[index+2] if index+2<len(rows) else None
    if following is None or following['address']!=end or flag_reader(bytes.fromhex(following['bytes'])): return None
    target_row=targets_by_address.get(target)
    if target_row is None or flag_reader(bytes.fromhex(target_row['bytes'])): return None
    modrm=code[1]; mod=modrm>>6; reg=(modrm>>3)&7; rm=modrm&7
    if code[0]==0x39: a,b=('rm',rm),('reg',reg)   # rm - reg
    else: a,b=('reg',reg),('rm',rm)                # reg - rm
    if mod==3:
        # register-register: canonical order is (smaller register) - (larger register)
        ra=a[1]; rb=b[1]
        if ra<=rb: canonical=bytes([0x39,0xc0|(rb<<3)|ra])+code[2:]; new_cc=cc
        else: canonical=bytes([0x39,0xc0|(ra<<3)|rb])+code[2:]; new_cc=SWAP_CC[cc]
    else:
        # memory-register: canonical form is 39 (memory - register)
        if code[0]==0x39: canonical=code; new_cc=cc
        else: canonical=bytes([0x39])+code[1:]; new_cc=SWAP_CC[cc]
    if len(jcode)==2: jnew=bytes([0x70|new_cc])+jcode[1:]
    else: jnew=bytes([0x0f,0x80|new_cc])+jcode[2:]
    return off,end,canonical+jnew


def zero_clear_projection(raw, rows, protected_targets=(), forbidden_ranges=()):
    """Candidate-to-candidate scheduling evidence, NEVER original matching.

    Canonicalize only adjacent runs of independent immediate writes: XOR r32,r32
    clears, mov $imm,r32 and mov $imm,disp(%ebp) stores with pairwise disjoint
    destinations, excluding ESP/EBP, internal CFG entry points, relocation fields and
    functions with indirect jumps. Within such a run no instruction reads another's
    destination and flags depend only on whether any clear is present, so every
    permutation leaves identical machine state. All other bytes, including padding
    and operands, remain in the fingerprint.
    """
    targets=set(protected_targets)
    for row in rows:
        if row['mnemonic'].startswith(('j','call','loop')):
            m=re.match(r'\S+\s+([0-9a-f]+)(?:\s|$)',row['assembly'])
            if m: targets.add(int(m[1],16))
    canonical=bytearray(raw); blocks=[]; pos=0
    while pos<len(rows):
        first=independent_write(raw,rows[pos],forbidden_ranges)
        if first is None: pos+=1; continue
        run_=[(rows[pos],first)]; pos+=1
        while pos<len(rows):
            nxt=independent_write(raw,rows[pos],forbidden_ranges); prev=run_[-1][0]
            if nxt is None or rows[pos]['address']!=prev['address']+len(bytes.fromhex(prev['bytes'])): break
            run_.append((rows[pos],nxt)); pos+=1
        start=run_[0][0]['address']; last=run_[-1][0]; end=last['address']+len(bytes.fromhex(last['bytes']))
        if len(run_)<2 or any(start<t<end for t in targets): continue
        if not _disjoint([d for _,(d,_) in run_]): continue
        codes=[bytes.fromhex(i['bytes']) for i,_ in run_]
        if len(set(codes))!=len(codes): continue
        canonical[start:end]=b''.join(sorted(codes))
        blocks.append({'start':start,'end':end,'original_bytes':raw[start:end].hex(),
                       'canonical_bytes':bytes(canonical[start:end]).hex(),'instructions':[i for i,_ in run_]})
    # Operand-swapped compares with inverted ordering conditions whose flags die at the jump.
    by_address={row['address']:row for row in rows}
    for index,row in enumerate(rows):
        if row['mnemonic']!='cmp': continue
        if any(a<=row['address']<b for a,b in forbidden_ranges): continue
        pair=compare_jump(raw,rows,index,by_address)
        if pair is None: continue
        start,end,code=pair
        changed={start+i for i,(x,y) in enumerate(zip(bytes(canonical[start:end]),code)) if x!=y}
        # Nothing may jump directly to the jcc (its condition changes), and no protected byte
        # (relocation field or entry) may change; an untouched displacement field is fine.
        jcc_start=rows[index+1]['address']
        # A jump to the compare itself executes the whole pair and is fine; the opcode byte may change there.
        if jcc_start in targets or any(t in changed and t!=start for t in targets): continue
        if changed:
            blocks.append({'start':start,'end':end,'original_bytes':raw[start:end].hex(),'canonical_bytes':code.hex(),'instructions':[row,rows[index+1]],
                           'kind':'compare_operand_order'})
            canonical[start:end]=code
    return {'sha256':sha(canonical),'blocks':blocks,
            'scope':'Only candidate scheduling preservation of adjacent independent immediate writes and operand-swapped compare/jump pairs whose flags die at the jump; never FUNCTION_MATCH evidence.'}
