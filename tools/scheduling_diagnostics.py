"""Small decoded instruction permutations; diagnostics never participate in matching."""
import re,struct
from collections import Counter
from bisect import bisect_right
from pathlib import Path
from common import ROOT


def byte_stream(rows,base,size):
    out=bytearray(); expected=base
    for row in rows:
        raw=bytes.fromhex(row['bytes'])
        if row['address']!=expected or not raw: return None
        out.extend(raw); expected+=len(raw)
    return bytes(out) if len(out)==size else None


def permitted(instruction):
    # Keep control flow, x87, stack adjustment and arbitrary flag operations out.
    if instruction['mnemonic'] in ('mov','movl','movb','movw','movzbl','movsbl','movzwl','movswl'): return True
    if instruction['mnemonic']=='xor':
        m=re.fullmatch(r'xor\s+%([a-z]+),%([a-z]+)',instruction['assembly'])
        return bool(m and m[1]==m[2] and m[1] not in ('esp','ebp','sp','bp'))
    return False


def source_rows(instructions,lines,source):
    ordered=sorted(enumerate(lines),key=lambda pair:(pair[1]['address'],pair[0])); addresses=[r['address'] for _,r in ordered]; result=[]
    content=(ROOT/source).read_bytes().decode('cp1252').splitlines() if source else []
    for instruction in instructions:
        index=bisect_right(addresses,instruction['address'])-1
        if index<0: continue
        row=ordered[index][1]; context=row.get('context'); line=row.get('line')
        if row.get('end_sequence') or not context or not isinstance(line,int): continue
        # A header line must never be presented as a maintained-source edit location.
        if (ROOT/context).resolve()!=(ROOT/source).resolve() or not 1<=line<=len(content): continue
        item={'file':source,'line':line,'text':content[line-1]}
        if item not in result: result.append(item)
    return result


def analyze(row,original,lines=(),source=None):
    candidate=row.get('instructions',[]); size=row.get('candidate_size')
    if not size or size!=row.get('original_size') or not original or not candidate or not row.get('instruction_boundaries_verified'): return None
    ob=row['va']; cb=row['candidate_offset']; old=byte_stream(original,ob,size); raw=byte_stream(candidate,cb,size)
    if old is None or raw is None: return None
    new=bytearray(raw); fields=set(); unresolved=[]
    for field in row.get('relocations',[])+row.get('direct_transfers',[]):
        offset=field['function_offset']; width=field.get('operand_size',4); positions=set(range(offset,offset+width))
        if width not in (1,4) or offset<0 or offset+width>size or fields&positions: return None
        fields.update(positions)
        if field.get('resolved_value') is None: unresolved.append(offset)
        else: new[offset:offset+width]=(field['resolved_value']&((1<<(8*width))-1)).to_bytes(width,'little')
    differing={i for i,(a,b) in enumerate(zip(old,new)) if a!=b}; windows=[]; covered=set()
    old_index={r['address']-ob:i for i,r in enumerate(original)}; new_index={r['address']-cb:i for i,r in enumerate(candidate)}
    entries=set()
    indirect_jump=any(r['mnemonic'].startswith('j') and '*' in r['assembly'] for r in original+candidate)
    for instructions,base in ((original,ob),(candidate,cb)):
        for r in instructions:
            if not r['mnemonic'].startswith(('j','call','loop')): continue
            m=re.fullmatch(r'\S+\s+([0-9a-f]+)(?:\s+<[^>]+>)?',r['assembly'])
            if m: entries.add(int(m[1],16)-base)
    end_of_window=0
    for offset in sorted(set(old_index)&set(new_index)):
        if offset<end_of_window: continue
        oi=old_index[offset]; ni=new_index[offset]
        before=original[oi]; after=candidate[ni]
        if before['bytes']==after['bytes']: continue
        for count in range(2,5):
            a=original[oi:oi+count]; b=candidate[ni:ni+count]
            if len(a)!=count or len(b)!=count or not all(permitted(r) for r in a+b): continue
            ae=a[-1]['address']-ob+len(bytes.fromhex(a[-1]['bytes'])); be=b[-1]['address']-cb+len(bytes.fromhex(b[-1]['bytes']))
            if ae!=be or ae-offset>32 or any(offset<x<ae for x in entries): continue
            positions=set(range(offset,ae))
            if fields&positions or not differing&positions: continue
            if Counter(r['bytes'] for r in a)!=Counter(r['bytes'] for r in b): continue
            windows.append({'function_offset':offset,'byte_length':ae-offset,'original':a,'candidate':b,
                            'candidate_source_lines':source_rows(b,lines,source) if source else [],
                            'observation':'Same decoded instructions occur in a different order; source cause and semantic independence are not inferred.'})
            covered.update(positions&differing); end_of_window=ae; break
    if not windows: return None
    remaining=sorted(differing-covered)
    complete=not remaining and not unresolved and all(f.get('equal') for f in row.get('relocations',[])+row.get('direct_transfers',[]))
    return {'confidence':'DECODED_INSTRUCTION_PERMUTATIONS','windows':windows,'all_other_resolved_bytes_equal':complete,
            'remaining_difference_count':len(remaining),'remaining_difference_offsets':remaining[:16],
            'unresolved_relocation_offsets':unresolved,'indirect_jump_present':indirect_jump,
            'cheap_routing_eligible':complete and not indirect_jump and len(windows)<=3,
            'limit':'Routing and source-experiment evidence only. Neither instruction reordering nor equality after reordering proves FUNCTION_MATCH or a layout-only body.'}


def assignment_patterns(diagnostic,text):
    """Only adjacent full assignment lines identified by the emitted line program."""
    from source_scope import sanitized
    if not diagnostic or not diagnostic['cheap_routing_eligible']: return []
    lines=text.splitlines(keepends=True); clean=sanitized(text).splitlines(keepends=True); patterns=[]
    for window in diagnostic['windows']:
        rows=window['candidate_source_lines']
        if len(rows)!=2: continue
        first,second=sorted(r['line'] for r in rows)
        if second!=first+1 or first<1 or second>len(lines): continue
        assignments=[]
        for number in (first,second):
            m=re.fullmatch(r'\s*([A-Za-z_]\w*)\s*=\s*([^;{}]+);\s*',clean[number-1])
            if not m or re.search(r'\b(?:return|if|while|for|goto)\b',m[2]): break
            assignments.append(m.groups())
        if len(assignments)!=2 or assignments[0][0]==assignments[1][0]: continue
        # Avoid assignment dependencies, calls, writes through pointers and increments.
        if any(re.search(r'\b'+re.escape(lhs)+r'\b',re.sub(r'(?:->|\.)\s*[A-Za-z_]\w*','',rhs)) for lhs,_ in assignments for _,rhs in assignments): continue
        if any(re.search(r'\(|\+\+|--|(?<![=!<>])=(?!=)',rhs) for _,rhs in assignments): continue
        start=sum(map(len,lines[:first-1])); end=start+len(lines[first-1])+len(lines[second-1])
        patterns.append({'id':'swap-adjacent-assignments-%d-%d'%(first,second),'source_lines':[first,second],
                         'function_offset':window['function_offset'],'changes':[{'start':start,'end':end,'before':text[start:end],
                         'after':lines[second-1]+lines[first-1]}],
                         'reason':'The decoded mismatch is an instruction-order window sourced from these two adjacent assignments. This is a bounded hypothesis; fresh exact acceptance remains mandatory.'})
    return patterns
