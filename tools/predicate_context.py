"""Source-bound memory for isolated truth-test experiments; never proof."""
from common import ROOT,read_json,identity
import json


def load(target,function,build,fixture,verifier):
    path=ROOT/'docs/attempts/predicate-probes'/target/(function+'.json')
    if not path.exists():return None
    record=read_json(path)
    if (record.get('target'),record.get('function'))!=(target,function):return None
    saved=record.get('compiler',{});tools=record.get('probe_tools',{})
    required={'tools/predicate_probe.py','tools/source_scope.py'}
    current=(record.get('source_inputs')==build.get('local_inputs') and bool(build.get('local_inputs'))
        and all(saved.get(k)==build.get(k) and build.get(k) is not None for k in ('compiler','config','flags','candidate_toolchain_lock'))
        and record.get('fixture')==fixture and record.get('verifier')==verifier and bool(fixture) and bool(verifier)
        and set(tools)==required and all((ROOT/p).is_file() and identity(ROOT/p)==v for p,v in tools.items()))
    prior=[];seen={v['variant'] for v in record.get('variants',[])};archive=path.with_suffix('.jsonl')
    lines=archive.read_text(encoding='utf-8').splitlines() if archive.exists() else []
    for index in range(len(lines)-1,-1,-1):
        previous=json.loads(lines[index])
        if (previous.get('target'),previous.get('function'))!=(target,function):continue
        for variant in previous.get('variants',[]):
            label=variant['variant']
            if label in seen:continue
            seen.add(label)
            prior.append({'variant':label,'target_result':variant.get('target_result'),
                'state':'HISTORICAL_REQUIRES_REFRESH','same_source_inputs':previous.get('source_inputs')==build.get('local_inputs'),
                'evidence':archive.relative_to(ROOT).as_posix(),'record_line':index+1})
    return {'baseline_state':'CURRENT_INPUTS' if current else 'HISTORICAL_REQUIRES_REFRESH',
        'prior_trials':prior[:4],'omitted_prior_trials':max(0,len(prior)-4),'switch_interval':record.get('switch_interval'),'expression':record.get('expression'),'invert_guard':record.get('invert_guard'),'outcome':record.get('outcome'),
        'evidence':path.relative_to(ROOT).as_posix(),
        'variants':[{'variant':v['variant'],'target_result':v.get('target_result'),'compile_failed':'error' in v} for v in record.get('variants',[])[:4]],
        'omitted_variants':max(0,len(record.get('variants',[]))-4),
        'limit':'Diagnostic only. A partial improvement does not prove the source cause, grant admission, or establish exact recovery.'}
