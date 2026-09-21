"""Select codegen guidance by observable symptoms; never infer a source fix or proof."""
import re
from control_transfers import relative


def features(row,evidence,original):
    variables=evidence.get('parameters',[])+evidence.get('locals',[])
    branches=[(i,relative(i)) for i in original if i.get('mnemonic','').startswith(('j','loop'))]
    branches=[(i,t) for i,t in branches if t]
    base=row.get('va',0);end=base+row.get('original_size',0)
    guards=[(i,t) for i,t in branches if t['kind']=='conditional']
    tail={i['address'] for i in original[-3:]}
    first=row.get('first_instruction_pair',{})
    pair=[first.get(side,{}).get('mnemonic') if first.get(side) else None for side in ('original','candidate')]
    float_width=any(set(pair)==set(p) for p in [('flds','fldl'),('fsts','fstl'),('fstps','fstpl'),('fadds','faddl'),('fmuls','fmull'),('fsubs','fsubl'),('fdivs','fdivl')])
    return {
        'has_loop':any(base<=t['target']<i['address']<end for i,t in branches),
        'has_multiple_guards':len(guards)>=2,
        'has_guarded_return':bool(original and original[-1].get('mnemonic')=='ret' and any(t['target'] in tail for _,t in guards)),
        'has_pointer_variable':any('*' in v.get('type','') for v in variables),
        'has_integer_variable':any(re.fullmatch(r'(?:(?:const|volatile|unsigned|signed)\s+)*(?:char|short|int|long)(?:\s+(?:int|long))?',v.get('type','').strip()) for v in variables),
        'has_locals':bool(evidence.get('locals')),
        'same_size':row.get('candidate_size')==row.get('original_size') and row.get('candidate_size') is not None,
        'register_only_shape':bool(row.get('register_only_instruction_shape')),
        'first_instruction_is_lea':any(i and i.get('mnemonic')=='lea' for i in first.values()),
        'has_compiler_context':bool(row.get('compiler_context')),
        'first_float_width_diff':float_width,
        'has_static_local':any(v.get('address') is not None for v in evidence.get('locals',[])),
        'emission_predecessor_differs':bool(row.get('emission_order')) and not row['emission_order'].get('predecessor_same',True),
    }


def select_rules(rules,row,evidence,workflow,original,build=None):
    observed=features(row,evidence,original);selected=[]
    for rule in rules:
        example=row['name'] in rule.get('example_functions',[])
        required=rule.get('required_evidence');filters=rule.get('required_features',[])
        scope=rule.get('compiler_scope',{})
        scope_matches=bool(build and build.get('compiler') in scope.get('compiler_ids',[]) and set(scope.get('required_flags',[]))<=set(build.get('flags',[])))
        supported=bool(required or filters) and not rule.get('historical_only') and scope_matches
        supported=supported and (not required or bool(evidence.get(required))) and all(observed.get(f,False) for f in filters)
        applicable=rule['difference_class']==workflow['difference_class'] and supported
        if not applicable and not example:continue
        selected.append({**rule,'applicability':{
            'basis':'CURRENT_SYMPTOM_EVIDENCE' if applicable else 'HISTORICAL_EXAMPLE_ONLY',
            'observed_features':[f for f in filters if observed.get(f)],
            'evidence_field':required if required and evidence.get(required) else None,
            'priority_bonus_eligible':bool(applicable),'compiler_scope_matches':scope_matches,
            'limit':'Symptom filtering narrows hypotheses; it does not prove the source cause or authorize a repair. Historical example membership alone is not current applicability.'}})
    return selected
