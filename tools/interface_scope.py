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
