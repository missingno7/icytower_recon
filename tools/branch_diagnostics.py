"""Bounded guard-condition diagnostics. These never participate in match acceptance."""
import re

CONDITIONS={'je':'zero/equal','jne':'nonzero/not equal','jg':'signed greater','jge':'signed greater or equal',
            'jl':'signed less','jle':'signed less or equal','ja':'unsigned above','jae':'unsigned above or equal',
            'jb':'unsigned below','jbe':'unsigned below or equal','js':'negative sign','jns':'nonnegative sign',
            'jo':'overflow','jno':'no overflow','jp':'even parity','jnp':'odd parity'}


def branch_target(instruction,base):
    match=re.fullmatch(r'\S+\s+([0-9a-f]+)(?:\s+<[^>]+>)?',instruction['assembly'].strip())
    return int(match[1],16)-base if match else None


def localized_guards(row,original):
    differences=set(row.get('difference_offsets',[])); candidate=row.get('instructions',[])
    if (not differences or len(differences)>4 or not original or not candidate or
        row.get('candidate_size')!=row.get('original_size') or not row.get('instruction_boundaries_verified') or
        any(not r.get('equal') for r in row.get('relocations',[])+row.get('direct_transfers',[]))): return None
    old_base=original[0]['address']; new_base=row['candidate_offset']
    old={i['address']-old_base:i for i in original}; new={i['address']-new_base:i for i in candidate}
    if set(old)!=set(new): return None
    previous=None; covered=set(); guards=[]
    for offset,before in old.items():
        after=new[offset]; old_bytes=bytes.fromhex(before['bytes']); new_bytes=bytes.fromhex(after['bytes'])
        if len(old_bytes)!=len(new_bytes): return None
        changed=differences.intersection(range(offset,offset+len(old_bytes)))
        if not changed: previous=before; continue
        if before['mnemonic'] not in CONDITIONS or after['mnemonic'] not in CONDITIONS: return None
        # Jcc short (7x rel8) or near (0f 8x rel32); only its condition nibble may differ.
        opcode=0 if len(old_bytes)==2 and 0x70<=old_bytes[0]<=0x7f and 0x70<=new_bytes[0]<=0x7f else 1 if len(old_bytes)==6 and old_bytes[0]==new_bytes[0]==0x0f and 0x80<=old_bytes[1]<=0x8f and 0x80<=new_bytes[1]<=0x8f else None
        if opcode is None or changed!={offset+opcode} or old_bytes[opcode+1:]!=new_bytes[opcode+1:]: return None
        target=branch_target(before,old_base)
        if target is None or target not in old or target!=branch_target(after,new_base): return None
        if previous is None or not previous['mnemonic'].startswith(('test','cmp')): return None
        guards.append({'function_offset':offset,'target_offset':target,'original_condition':CONDITIONS[before['mnemonic']],
                       'candidate_condition':CONDITIONS[after['mnemonic']],'original_instruction':before,
                       'candidate_instruction':after,'flags_producer':previous})
        covered.update(changed); previous=before
    if covered!=differences: return None
    return {'confidence':'DECODED_LOCAL_GUARD_DIFFERENCES','guards':guards,
            'all_other_resolved_bytes_equal':True,'indirect_calls_unchanged':True,
            'limit':'A work-routing diagnostic, not body equality. The different guard conditions still require source repair and fresh strict acceptance.'}
