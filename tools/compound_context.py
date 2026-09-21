"""Bounded memory of source-bound compound experiments, never proof or admission."""
from common import ROOT,read_json,identity


def load(target,function,build,fixture,verifier):
    path=ROOT/'docs/attempts/compound-probes'/target/(function+'.json')
    if not path.exists():return None
    record=read_json(path)
    if record.get('target')!=target or record.get('function')!=function:return None
    probe=ROOT/'tools/compound_probe.py'
    complete=all(record.get(k) is not None for k in ('source_inputs','toolchain_lock','compiler','compiler_config','compiler_flags','fixture','verifier','probe_tool'))
    current=(complete and record.get('source_inputs')==build.get('local_inputs')
        and record.get('toolchain_lock')==build.get('candidate_toolchain_lock')
        and record.get('compiler')==build.get('compiler')
        and record.get('compiler_config')==build.get('config')
        and record.get('compiler_flags')==build.get('flags')
        and record.get('fixture')==fixture and record.get('verifier')==verifier
        and probe.is_file() and record.get('probe_tool')==identity(probe))
    return {'baseline_state':'CURRENT_INPUTS' if current else 'HISTORICAL_REQUIRES_REFRESH',
        'outcome':record.get('outcome','LEGACY_RECORD'),'evidence':path.relative_to(ROOT).as_posix(),
        'interface':record.get('interface'),'condition':record.get('condition'),
        'variants':[{k:r[k] for k in ('variant','status','candidate_size','original_size','body_shape_equal','first_difference','function_matches') if k in r} |
                    {'compile_failed':'compile_error' in r} for r in record.get('variants',[])[:3]],
        'omitted_variants':max(0,len(record.get('variants',[]))-3),
        'limit':'Diagnostic scratch experiments only. Matching shape or a diagnostic verdict is not a promoted result; source and tool changes require refresh.'}
