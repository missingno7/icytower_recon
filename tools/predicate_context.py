"""Source-bound memory for isolated truth-test experiments; never proof."""
from common import ROOT,read_json,identity


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
    return {'baseline_state':'CURRENT_INPUTS' if current else 'HISTORICAL_REQUIRES_REFRESH',
        'expression':record.get('expression'),'outcome':record.get('outcome'),
        'evidence':path.relative_to(ROOT).as_posix(),
        'variants':[{'variant':v['variant'],'target_result':v.get('target_result'),'compile_failed':'error' in v} for v in record.get('variants',[])[:2]],
        'omitted_variants':max(0,len(record.get('variants',[]))-2),
        'limit':'Diagnostic only. A partial improvement does not prove the source cause, grant admission, or establish exact recovery.'}
