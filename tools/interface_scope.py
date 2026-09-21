"""Scope queue prerequisites to compiled CU evidence, retaining remote conflicts."""


def assess(conflict,source):
    historical=conflict.get('historical',[])
    expected={(d['return_type'],tuple(d['parameter_types'])+(('...',) if d.get('variadic') else ())) for d in historical}
    result={'function':conflict['function'],'source':source,'blocking':True,'state':'LOCAL_INTERFACE_UNPROVEN'}
    if len(expected)!=1 or any(d.get('calling_convention') is not None for d in historical):
        return result|{'reason':'Historical signature or calling convention is ambiguous.'}
    declarations=conflict.get('candidate_declarations',[])
    if any(not d.get('cu') for d in declarations) or any(not d.get('cu') for d in conflict.get('type_layout_issues',[])):
        return result|{'reason':'Declaration or layout evidence has unknown CU ownership.'}
    local=[d for d in declarations if d['cu']==source]
    if not local: return result|{'reason':'No compiled declaration evidence for this CU.'}
    expected=next(iter(expected))
    for d in local:
        actual=(d.get('canonical_return_type',d['return_type']),tuple(d.get('canonical_parameter_types',d['parameter_types'])))
        if actual!=expected or 'game_type_layouts' not in d or any(x['status']!='AGREE' for x in d['game_type_layouts']):
            return result|{'state':'LOCAL_INTERFACE_CONFLICT','reason':'A declaration compiled in this CU differs or lacks complete game-type evidence.'}
    if any(d['cu']==source for d in conflict.get('type_layout_issues',[])):
        return result|{'state':'LOCAL_INTERFACE_CONFLICT','reason':'This CU has a recorded aggregate-layout issue.'}
    return result|{'blocking':False,'state':'LOCAL_AGREEMENT_REMOTE_CONFLICT',
                   'reason':'All compiled declarations and checked game layouts in this CU agree; retain the cross-CU repair separately.'}


def partition(conflicts,source):
    assessments=[assess(c,source) for c in conflicts]
    return [c for c,a in zip(conflicts,assessments) if a['blocking']],assessments


def callees(calls,index,source):
    """Surface known direct-callee conflicts in the caller's compiled CU."""
    grouped={}
    for call in calls:
        name=call.get('function')
        if name in index:grouped.setdefault(name,[]).append(call['function_offset'])
    observations=[]
    for name,offsets in sorted(grouped.items()):
        for conflict in index[name]:
            local=[d for d in conflict.get('candidate_declarations',[]) if d.get('cu')==source]
            observations.append({**assess(conflict,source),'call_offsets':sorted(set(offsets)),
                'candidate_card':'docs/current/interfaces/'+name+'.json',
                'local_declarations':[{k:d[k] for k in ('return_type','parameter_types','canonical_return_type','canonical_parameter_types') if k in d} for d in local],
                'layout_issues':[x for d in local for x in d.get('game_type_layouts',[]) if x['status']!='AGREE']})
    return {'observations':observations,'blocking_functions':sorted({r['function'] for r in observations if r['blocking']}),
            'limit':'Known direct-callee conflicts only. Verified call addresses do not prove declaration/type compatibility. Remote-only conflicts remain visible but do not block a proven local interface; unknown indirect targets are not inferred.'}
