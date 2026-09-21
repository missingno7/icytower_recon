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


def variant_difference(baseline, variant):
    """Bounded candidate-context delta, including length changes and unavailable bytes."""
    a_size,b_size=baseline.get('candidate_size'),variant.get('candidate_size')
    sizes=all(isinstance(x,int) and not isinstance(x,bool) and x>=0 for x in (a_size,b_size))
    a,b=baseline.get('resolved_code'),variant.get('resolved_code')
    a=bytes.fromhex(a) if isinstance(a,str) else None
    b=bytes.fromhex(b) if isinstance(b,str) else None
    comparable=a is not None and b is not None
    if comparable and sizes and (len(a)!=a_size or len(b)!=b_size): comparable=False
    offsets=([i for i,(x,y) in enumerate(zip(a,b)) if x!=y]+list(range(min(len(a),len(b)),max(len(a),len(b))))) if comparable else None
    return {'baseline_size':a_size,'candidate_size':b_size,'size_delta':b_size-a_size if sizes else None,
            'extent_changed':sizes and a_size!=b_size,'resolved_bytes_comparable':comparable,
            'changed_byte_count':len(offsets) if offsets is not None else None,
            'first_changed_offsets':offsets[:16] if offsets is not None else None,
            'limit':'Candidate trial observation, not production body or layout equality. An extent change alone does not establish its source, padding or branch-layout cause.'}


def dependencies(record):
    baseline=next((v for v in record.get('variants',[]) if v['variant']=='baseline'),{})
    found=[]
    for variant in record.get('variants',[]):
        if not variant['variant'].startswith('omit-') or variant.get('target_body_sha256')!=record.get('target_body_sha256'): continue
        difference=variant_difference(baseline,variant)
        if difference['extent_changed'] or difference['changed_byte_count'] or variant.get('context_changed_offsets'):
            found.append((variant,difference))
    return found


def load_context(target,name,row,source_inputs):
    path=ROOT/'docs/attempts/compiler-context'/target/(name+'.json')
    if not path.exists(): return None
    records=[read_json(path)]
    archive=path.with_suffix('.jsonl')
    if archive.exists(): records.extend(reversed([json.loads(line) for line in archive.read_text().splitlines() if line.strip()]))
    record=next((r for r in records if r.get('target_body_sha256')==row.get('source_body_sha256') and dependencies(r)),None)
    if record is None: return None
    baseline=next((v for v in record['variants'] if v['variant']=='baseline'),None)
    if baseline is None: return None
    changes=dependencies(record)
    if not changes: return None
    fresh=(record.get('probe_tool')==identity(ROOT/'tools/compiler_probe.py') and record['source_inputs']==source_inputs
           and record['toolchain_lock']==identity(ROOT/'toolchain/tdm-2-lock.json') and baseline.get('resolved_code') is not None and baseline.get('resolved_code')==resolved_candidate(row))
    return {'state':'CONFIRMED_CONTEXT_DEPENDENCY' if fresh else 'CONTEXT_EVIDENCE_NEEDS_REFRESH',
            'confidence':'MECHANICALLY_OBSERVED' if fresh else 'HISTORICAL_OBSERVATION',
            'dependencies':[{'omitted_function':v['variant'].removeprefix('omit-'),'changed_offsets':difference['first_changed_offsets'] if difference['first_changed_offsets'] is not None else v.get('context_changed_offsets'),'context_difference':difference,
                             'target_body_unchanged':v['target_body_sha256']==record['target_body_sha256']} for v,difference in changes],
            'evidence':(path if record is records[0] else archive).relative_to(ROOT).as_posix(),'reason':'An isolated peer-definition change altered target machine bytes without editing the target body. This is not an original byte-match proof.',
            'verification_command':'python tools/compiler_probe.py '+target+' '+name+' '+' '.join('--omit-earlier '+v['variant'].removeprefix('omit-') for v,difference in changes)}


def load_trials(target,name,row,source_inputs):
    """Keep the newest result per experiment, including archived negative trials."""
    path=ROOT/'docs/attempts/compiler-context'/target/(name+'.json')
    if not path.exists(): return None
    record=read_json(path)
    baseline=next((v for v in record.get('variants',[]) if v['variant']=='baseline'),None)
    if baseline is None:return None
    tool=identity(ROOT/'tools/compiler_probe.py');lock=identity(ROOT/'toolchain/tdm-2-lock.json')
    resolved=resolved_candidate(row)
    def fresh(item,base):
        return (item.get('probe_tool')==tool and item.get('source_inputs')==source_inputs
                and item.get('toolchain_lock')==lock and item.get('target_body_sha256')==row.get('source_body_sha256')
                and base.get('resolved_code') is not None and base.get('resolved_code')==resolved)
    current=fresh(record,baseline);archive=path.with_suffix('.jsonl')
    records=[(record,path,None)]
    if archive.exists():
        records.extend((json.loads(line),archive,n) for n,line in reversed(list(enumerate(archive.read_text(encoding='utf8').splitlines(),1))) if line.strip())
    trials=[];seen=set()
    for item,evidence,line in records:
        base=next((v for v in item.get('variants',[]) if v['variant']=='baseline'),None)
        if base is None:continue
        for v in item['variants']:
            if v['variant']=='baseline' or v['variant'] in seen:continue
            seen.add(v['variant'])
            trials.append({'variant':v['variant'],'target_body_unchanged':v.get('target_body_sha256')==item.get('target_body_sha256'),
                'baseline_state':'CURRENT_BASELINE' if fresh(item,base) else 'BASELINE_REQUIRES_REVIEW',
                'evidence':evidence.relative_to(ROOT).as_posix(),'archive_line':line,
                'difference':variant_difference(base,v),
                'diagnostic_original_comparison':{'verdict':v.get('comparison_verdict'),'mismatch_count':len(v['difference_offsets']) if 'difference_offsets' in v else None,'acceptance_input':False}})
    return {'state':'CURRENT_BASELINE' if current else 'BASELINE_REQUIRES_REVIEW','evidence':path.relative_to(ROOT).as_posix(),
            'trial_count':len(trials),'trials':trials[:3],'omitted_trial_count':max(0,len(trials)-3),
            'records_considered':len(records),'history_evidence':archive.relative_to(ROOT).as_posix() if archive.exists() else None,
            'rtl_evidence':record.get('rtl_evidence'),
            'limit':'Newest result per experiment name, latest record first; archived trials retain their own baseline freshness and line number. No-change results apply only to the recorded input snapshot. Diagnostic memory grants no original-match or edit permission.'}
