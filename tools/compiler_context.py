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
    """Expose negative as well as positive trials without changing work eligibility."""
    path=ROOT/'docs/attempts/compiler-context'/target/(name+'.json')
    if not path.exists(): return None
    record=read_json(path)
    baseline=next((v for v in record.get('variants',[]) if v['variant']=='baseline'),None)
    if baseline is None:return None
    current=(record.get('probe_tool')==identity(ROOT/'tools/compiler_probe.py') and record.get('source_inputs')==source_inputs
             and record.get('toolchain_lock')==identity(ROOT/'toolchain/tdm-2-lock.json')
             and record.get('target_body_sha256')==row.get('source_body_sha256')
             and baseline.get('resolved_code') is not None and baseline.get('resolved_code')==resolved_candidate(row))
    trials=[{'variant':v['variant'],'target_body_unchanged':v.get('target_body_sha256')==record.get('target_body_sha256'),
             'difference':variant_difference(baseline,v),
             'diagnostic_original_comparison':{'verdict':v.get('comparison_verdict'),'mismatch_count':len(v['difference_offsets']) if 'difference_offsets' in v else None,'acceptance_input':False}} for v in record['variants'] if v['variant']!='baseline']
    return {'state':'CURRENT_BASELINE' if current else 'BASELINE_REQUIRES_REVIEW','evidence':path.relative_to(ROOT).as_posix(),
            'trial_count':len(trials),'trials':trials[:3],'rtl_evidence':record.get('rtl_evidence'),
            'limit':'Diagnostic trial memory only. A no-change result applies to this input snapshot and experiment, not every possible compiler context; stale or unresolvable baselines are explicit. No original-match or edit-permission claim.'}
