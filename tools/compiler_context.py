"""Candidate context diagnostics remain separate from all original match verdicts."""
import struct
import json
from common import ROOT,identity,read_json


def resolved_candidate(row):
    fields=row.get('relocations',[])+row.get('direct_transfers',[])
    if not row.get('candidate_size') or any(r.get('resolved_value') is None for r in fields): return None
    code=bytearray(row['candidate_size']); covered=set()
    for instruction in row.get('instructions',[]):
        start=instruction['address']-row['candidate_offset']; raw=bytes.fromhex(instruction['bytes'])
        if start<0 or start+len(raw)>len(code): return None
        if covered.intersection(range(start,start+len(raw))): return None
        code[start:start+len(raw)]=raw; covered.update(range(start,start+len(raw)))
    if len(covered)!=len(code): return None
    patched=set()
    for field in fields:
        offset=field['function_offset']
        width=field.get('operand_size',4)
        if width not in (1,4) or not 0<=offset<=len(code)-width: return None
        if patched.intersection(range(offset,offset+width)): return None
        patched.update(range(offset,offset+width))
        code[offset:offset+width]=(field['resolved_value']&((1<<(8*width))-1)).to_bytes(width,'little')
    return code.hex()


def load_context(target,name,row,source_inputs):
    path=ROOT/'docs/attempts/compiler-context'/target/(name+'.json')
    if not path.exists(): return None
    records=[read_json(path)]
    archive=path.with_suffix('.jsonl')
    if archive.exists(): records.extend(reversed([json.loads(line) for line in archive.read_text().splitlines() if line.strip()]))
    record=next((r for r in records if r.get('target_body_sha256')==row.get('source_body_sha256') and any(v['variant'].startswith('omit-') and v.get('context_changed_offsets') and v.get('target_body_sha256')==r.get('target_body_sha256') for v in r['variants'])),None)
    if record is None: return None
    baseline=next((v for v in record['variants'] if v['variant']=='baseline'),None)
    if baseline is None: return None
    dependencies=[v for v in record['variants'] if v['variant'].startswith('omit-') and v.get('context_changed_offsets') and v.get('target_body_sha256')==record.get('target_body_sha256')]
    if not dependencies: return None
    fresh=(record.get('probe_tool')==identity(ROOT/'tools/compiler_probe.py') and record['source_inputs']==source_inputs
           and record['toolchain_lock']==identity(ROOT/'toolchain/tdm-2-lock.json') and baseline.get('resolved_code')==resolved_candidate(row))
    return {'state':'CONFIRMED_CONTEXT_DEPENDENCY' if fresh else 'CONTEXT_EVIDENCE_NEEDS_REFRESH',
            'confidence':'MECHANICALLY_OBSERVED' if fresh else 'HISTORICAL_OBSERVATION',
            'dependencies':[{'omitted_function':v['variant'].removeprefix('omit-'),'changed_offsets':v['context_changed_offsets'],
                             'target_body_unchanged':v['target_body_sha256']==record['target_body_sha256']} for v in dependencies],
            'evidence':(path if record is records[0] else archive).relative_to(ROOT).as_posix(),'reason':'An isolated peer-definition change altered target machine bytes without editing the target body. This is not an original byte-match proof.',
            'verification_command':'python tools/compiler_probe.py '+target+' '+name+' '+' '.join('--omit-earlier '+v['variant'].removeprefix('omit-') for v in dependencies)}
