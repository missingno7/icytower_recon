"""Bounded instruction-sequence diagnostics, never equality or work-admission proof."""
from difflib import SequenceMatcher
from control_transfers import relative
from scheduling_diagnostics import byte_stream

LIMIT=4000


def keys(row,rows,original=False):
    base=row['va'] if original else row['candidate_offset']
    boundaries={i['address']:n for n,i in enumerate(rows)}
    result=[]
    for instruction in rows:
        raw=bytes.fromhex(instruction['bytes']);at=instruction['address']-base
        transfer=relative(instruction)
        fields=[] if original else [r for r in row.get('relocations',[]) if at<=r['function_offset']<at+len(raw)]
        if transfer:
            operand=at+transfer['operand_offset'];target=transfer['target'];kind='absolute'
            if fields:
                if len(fields)!=1 or fields[0]['function_offset']!=operand or fields[0].get('type')!=20 or fields[0].get('target_va') is None:
                    result.append(('unresolved-transfer',at,raw.hex()));continue
                target=fields[0]['target_va']
            elif not original:
                external=[t for t in row.get('direct_transfers',[]) if t['function_offset']==operand]
                if external:
                    if len(external)!=1 or not external[0].get('equal') or external[0].get('target_va') is None:
                        result.append(('unresolved-transfer',at,raw.hex()));continue
                    target=external[0]['target_va']
                elif target in boundaries:
                    kind='instruction-index';target=boundaries[target]
                else:
                    result.append(('unresolved-transfer',at,raw.hex()));continue
            elif target in boundaries:
                kind='instruction-index';target=boundaries[target]
            result.append(('transfer',instruction['mnemonic'],kind,target));continue
        if fields:
            valid=True;covered=set();patched=bytearray(raw)
            for field in fields:
                p=field['function_offset']-at
                if field.get('type')!=6 or field.get('resolved_value') is None or p<1 or p+4>len(raw) or covered.intersection(range(p,p+4)):
                    valid=False;break
                covered.update(range(p,p+4))
                patched[p:p+4]=(field['resolved_value']&0xffffffff).to_bytes(4,'little')
            result.append(('bytes',patched.hex()) if valid else ('unresolved-field',at,raw.hex()))
        else:result.append(('bytes',raw.hex()))
    return result


def analyze(row,original):
    candidate=row.get('instructions',[])
    if row.get('status')=='FUNCTION_MATCH':return None
    if not original or not candidate:return None
    if max(len(original),len(candidate))>LIMIT:
        return {'state':'SIZE_LIMIT','limit_instructions':LIMIT,'original_instruction_count':len(original),'candidate_instruction_count':len(candidate)}
    if byte_stream(original,row['va'],row['original_size']) is None or byte_stream(candidate,row['candidate_offset'],row['candidate_size']) is None:
        return {'state':'INCOMPLETE_DECODE','reason':'Complete contiguous function extents are required for sequence diagnostics.'}
    a,b=keys(row,original,True),keys(row,candidate)
    groups=SequenceMatcher(None,a,b,autojunk=False).get_opcodes()
    changes=[g for g in groups if g[0]!='equal'];hunks=[]
    def excerpt(rows,start,end,base):
        return {'instruction_start':start,'instruction_end':end,'function_offset':rows[start]['address']-base if start<len(rows) else sum(len(bytes.fromhex(r['bytes'])) for r in rows),
                'instructions':rows[start:min(end,start+4)],'omitted_instructions':max(0,end-start-4)}
    for tag,i,j,k,l in changes[:3]:
        hunks.append({'kind':tag,'original':excerpt(original,i,j,row['va']),'candidate':excerpt(candidate,k,l,row['candidate_offset'])})
    return {'state':'DIAGNOSTIC_SEQUENCE_ALIGNMENT','original_instruction_count':len(a),'candidate_instruction_count':len(b),
            'changed_group_count':len(changes),'shown_group_count':len(hunks),'hunks':hunks,
            'normalization':'Candidate absolute fields use independent resolved values; external transfers use independent targets; intra-function transfers use decoded instruction indices. Unresolved fields never align with original bytes.',
            'limit':'Sequence alignment is heuristic and may be ambiguous in repeated code. Equal groups are not body/semantic/layout proof. Never changes status, routing, edit permission or promotion.'}
