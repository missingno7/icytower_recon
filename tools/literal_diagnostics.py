"""Operand-aligned literal content diagnostics; never relocation ownership proof."""
import re
from source_scope import function_span

LIMIT=4096


def c_string(data,offset):
    if not 0<=offset<len(data): return None
    end=data.find(b'\0',offset,min(len(data),offset+LIMIT))
    if end<0: return None
    raw=data[offset:end]
    if any(c not in (9,10,13) and not 32<=c<=126 for c in raw): return None
    return raw


def operand_kind(raw,p):
    # Immediate pointers, not arbitrary memory loads that happen to address ASCII.
    if p==1 and len(raw)==5 and (raw[0]==0x68 or 0xb8<=raw[0]<=0xbf): return 'C_STRING'
    if raw[:1]==b'\xc7' and len(raw)>=6 and (raw[1]>>3)&7==0 and p==len(raw)-4: return 'C_STRING'
    if p==2 and len(raw)==6 and raw[1]&0xc7==5:
        if raw[0] in (0xd8,0xdc) or raw[0] in (0xd9,0xdd) and (raw[1]>>3)&7 in (0,2,3):
            return 'FLOAT32' if raw[0] in (0xd8,0xd9) else 'FLOAT64'
    return None


def placement_evidence(payload, kind, relocation, exe):
    """Search candidate payload only; never consume the tested original operand."""
    result={'resolved_target':relocation.get('target_va'),
        'resolution':relocation.get('resolution'),
        'limit':'Independent content locations are diagnostic only. They do not override an existing section/object binding, establish literal identity, or authorize promotion.'}
    if not payload:
        return result|{'state':'EMPTY_PAYLOAD_NOT_IDENTIFYING','occurrence_count':None,'locations':[]}
    needle=payload+(b'\0' if kind=='C_STRING' else b'')
    locations=[]
    for section in exe.sections:
        if section['name']!='.rdata': continue
        data=exe.section_bytes(section);start=0
        while len(locations)<9:
            offset=data.find(needle,start)
            if offset<0: break
            locations.append(exe.image_base+section['rva']+offset);start=offset+1
        if len(locations)>=9: break
    truncated=len(locations)>=9
    result.update(locations=locations[:8],occurrence_count=None if truncated else len(locations),
                  occurrence_count_lower_bound=len(locations),locations_truncated=truncated)
    if not locations: state='CONTENT_NOT_FOUND'
    elif len(locations)!=1: state='CONTENT_LOCATION_AMBIGUOUS'
    elif result['resolved_target'] is None: state='UNIQUE_CONTENT_WITHOUT_RESOLVED_OWNER'
    elif locations[0]==result['resolved_target']: state='UNIQUE_CONTENT_AGREES_WITH_RESOLVED_PLACEMENT'
    else:
        state='UNIQUE_CONTENT_DISAGREES_WITH_RESOLVED_PLACEMENT'
        result['content_minus_resolved_target']=locations[0]-result['resolved_target']
    result['state']=state
    return result


def diagnose(row,original,snapshot,sections,exe,line_mappings=(),source=None):
    observations=[]; old_by_offset={i['address']-row['va']:i for i in original}
    candidates=row.get('instructions',[]); base=row.get('candidate_offset',0)
    data_sections=[s for s in sections if s['name']=='.rdata']
    for r in row.get('relocations',[]):
        if r.get('symbol')!='.rdata' or r.get('equal'): continue
        offset=r['function_offset']; item={'function_offset':offset,'candidate_addend':r['addend'],
            'classification':'UNALIGNED_OR_UNTYPED','content_equal':None,
            'limit':'Original operand supplies diagnostic comparison only, never an independent target binding.'}
        observations.append(item)
        hits=[i for i in candidates if i['address']-base<=offset and offset+4<=i['address']-base+len(bytes.fromhex(i['bytes']))]
        if len(hits)!=1 or r['type']!=6 or len(data_sections)!=1: continue
        ins=hits[0]; at=ins['address']-base; before=old_by_offset.get(at)
        if not before: continue
        new=bytes.fromhex(ins['bytes']); old=bytes.fromhex(before['bytes']); p=offset-at
        if len(new)!=len(old) or new[:p]+new[p+4:]!=old[:p]+old[p+4:]: continue
        if any(x is not r and x['function_offset']<offset+4 and offset<x['function_offset']+4 for x in row.get('relocations',[])): continue
        kind=operand_kind(new,p)
        if not kind: continue
        value=int.from_bytes(old[p:p+4],'little')
        if value!=r['original_value']: continue
        old_sections=[s for s in exe.sections if s['name']=='.rdata' and exe.image_base+s['rva']<=value<exe.image_base+s['rva']+s['raw_size']]
        if len(old_sections)!=1: continue
        data=bytes.fromhex(snapshot['sections'][str(data_sections[0]['index'])]); addend=r['addend']
        if int.from_bytes(new[p:p+4],'little')!=addend: continue
        section=old_sections[0]; old_data=exe.section_bytes(section); old_offset=value-exe.image_base-section['rva']
        if kind=='C_STRING':
            a=c_string(data,addend); b=c_string(old_data,old_offset)
        else:
            width=4 if kind=='FLOAT32' else 8
            a=data[addend:addend+width] if 0<=addend and addend+width<=len(data) else None
            b=old_data[old_offset:old_offset+width] if old_offset+width<=len(old_data) else None
        if a is None or b is None: continue
        # Embedded relocations are pointers/tables, not raw literal payloads.
        n=len(a)+(kind=='C_STRING')
        if any(x['section']==data_sections[0]['index'] and x['offset']<addend+n and addend<x['offset']+4 for x in snapshot.get('relocations',[])): continue
        item.update(kind=kind,historical_operand_va=value,candidate_hex=a.hex(),original_hex=b.hex(),content_equal=a==b,
                    classification='CONTENT_EQUAL_OWNER_UNPROVEN' if a==b else 'LITERAL_CONTENT_DIFFERENCE',
                    candidate_instruction=ins,original_instruction=before)
        item['placement_evidence']=placement_evidence(a,kind,r,exe)
        if kind=='C_STRING': item.update(candidate_text=a.decode('ascii'),original_text=b.decode('ascii'))
        if source:
            from scheduling_diagnostics import source_rows
            item['candidate_source_lines']=source_rows([ins],line_mappings,source)
    return observations


TOKEN=re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|\'(?:\\.|[^\'\\\r\n])*\'|"(?:\\.|[^"\\\r\n])*"')


def decode_string(token):
    out=bytearray(); i=1
    escapes={'a':7,'b':8,'f':12,'n':10,'r':13,'t':9,'v':11,'\\':92,'"':34,"'":39,'?':63}
    while i<len(token)-1:
        c=token[i]; i+=1
        if c!='\\':
            if not 32<=ord(c)<=126: return None
            out.append(ord(c)); continue
        c=token[i]; i+=1
        if c in escapes: out.append(escapes[c])
        elif c in '01234567':
            match=re.match('[0-7]{0,2}',token[i:]); digits=c+match[0]; i+=len(match[0]); value=int(digits,8)
            if value>255: return None
            out.append(value)
        elif c=='x':
            match=re.match('[0-9a-fA-F]+',token[i:])
            if not match or int(match[0],16)>255: return None
            out.append(int(match[0],16)); i+=len(match[0])
        else: return None
    return bytes(out) if 0 not in out else None


def quote(raw):
    escapes={9:'\\t',10:'\\n',13:'\\r',34:'\\"',92:'\\\\'}
    return '"'+''.join(escapes.get(c,chr(c)) for c in raw)+'"'


def patterns(row,text):
    if row['status']=='FUNCTION_MATCH' or not row.get('body_shape_equal',row.get('masked_equal')): return []
    differences=[d for d in row.get('literal_diagnostics',[]) if d['classification']=='LITERAL_CONTENT_DIFFERENCE']
    if not differences or any(d.get('kind')!='C_STRING' for d in differences): return []
    try: lo,hi=function_span(text,row['name'])
    except ValueError: return []
    tokens=list(TOKEN.finditer(text,lo,hi)); changes=[]; selected={}
    for d in differences:
        a=bytes.fromhex(d['candidate_hex']); b=bytes.fromhex(d['original_hex'])
        if not a: return []
        hits=[m for m in tokens if m[0].startswith('"') and decode_string(m[0])==a]
        lines={r['line'] for r in d.get('candidate_source_lines',[]) if r.get('line')}
        if lines: hits=[m for m in hits if text[:m.start()].count('\n')+1 in lines]
        if len(hits)!=1: return []
        m=hits[0]
        if m.start() in selected and selected[m.start()][1]!=b: return []
        selected[m.start()]=(m,b)
    for m,b in selected.values():
        if m.start()>0 and (text[m.start()-1].isalnum() or text[m.start()-1]=='_'): return []
        # Adjacent string concatenation and macro substitutions need richer provenance.
        others=[t for t in tokens if t[0].startswith('"') and t!=m]
        for t in others:
            left,right=(t,m) if t.start()<m.start() else (m,t)
            gap=re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text[left.end():right.start()])
            if not gap.strip(): return []
        changes.append({'start':m.start(),'end':m.end(),'before':m[0],'after':quote(b),
                        'reason':'Correct the unique explicit string token from aligned original/candidate operand content; fresh independent verification required.'})
    return [{'id':'repair_literal_content','changes':sorted(changes,key=lambda x:x['start']),
             'reason':'Aligned instructions expose different string payloads; this is a source experiment, not ownership or equality proof.'}]
