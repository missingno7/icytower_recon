"""Compact source-bound canonicalization trials for type task cards."""
from common import ROOT,read_json,identity


def summaries(card):
    result=[]
    for target in card.get('affected_targets',[]):
        path=ROOT/'docs/attempts/type-context-probes'/target/(card['function']+'.json')
        if not path.exists():continue
        record=read_json(path)
        if (record.get('target'),record.get('task'))!=(target,card['function']):continue
        report=read_json(ROOT/'docs/current/reports'/(target+'.json'));build=report['build'];saved=record.get('compiler',{})
        inputs=record.get('source_inputs',{});tools=record.get('probe_tools',{})
        required={'tools/type_context_probe.py','tools/type_tasks.py','tools/type_views.py','tools/interface_tasks.py'}
        def agrees(path,value):
            p=ROOT/path
            return p.resolve().is_relative_to(ROOT.resolve()) and p.is_file() and identity(p)==value
        current=(bool(inputs) and all(agrees(p,v) for p,v in inputs.items()) and set(tools)==required and all(agrees(p,v) for p,v in tools.items())
            and record.get('fixture')==report.get('fixture') and record.get('verifier')==report.get('verifier')
            and all(saved.get(k)==build.get(k) and build.get(k) is not None for k in ('compiler','config','flags','candidate_toolchain_lock','local_inputs')))
        variants=[]
        for variant in record.get('variants',[])[:4]:
            diagnostics=variant.get('contribution_diagnostics',{});changed=diagnostics.get('changed_functions',[])
            variants.append({'variant':variant['variant'],'raw_baseline_equal':variant.get('raw_baseline_equal'),
                'preservation_fingerprint_equal':diagnostics.get('preservation_fingerprint_equal'),'compile_failed':'error' in variant,
                'changed_function_count':len(changed),'changed_functions':[{k:f.get(k) for k in ('function','observation','size_before','size_after','status_before','status_after')} for f in changed[:4]],'omitted_changed_functions':max(0,len(changed)-4)})
        result.append({'target':target,'baseline_state':'CURRENT_INPUTS' if current else 'HISTORICAL_REQUIRES_REFRESH',
            'evidence':path.relative_to(ROOT).as_posix(),'outcome':record.get('outcome'),'variants':variants,
            'omitted_variants':max(0,len(record.get('variants',[]))-4),
            'limit':'Diagnostic variants only. Assertion suppression is not a production option; raw preservation, type proof and normal promotion remain required.'})
    return result
