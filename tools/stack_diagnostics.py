"""Recognize differing constant prologue allocations without guessing their source cause."""
import re
from collections import defaultdict
from type_graph import graph


def allocation(instructions):
    if not instructions: return None
    base=instructions[0]['address']
    for i in instructions:
        if i['address']-base>=64: break
        mnemonic=i['mnemonic']
        if mnemonic.startswith(('j','call','ret','loop')): break
        m=re.fullmatch(r'sub[l]?\s+\$(0x[0-9a-f]+|\d+),\s*%esp',i['assembly'])
        if m:
            size=int(m[1],0)
            if not 0<=size<0x1000000: return None
            return {'function_offset':i['address']-base,'reserved_bytes':size,'instruction':i}
    return None


def local_widths(original,candidate):
    g=graph(); a=defaultdict(list); b=defaultdict(list)
    for v in original:
        if v.get('name') and g.dies[v['die']]['tag']=='DW_TAG_variable' and v.get('address') is None: a[v['name']].append(v)
    for v in candidate:
        if v.get('name') and v.get('role')=='DW_TAG_variable' and v.get('address') is None: b[v['name']].append(v)
    rows=[]
    for name in sorted(a.keys()&b.keys()):
        if len(a[name])!=1 or len(b[name])!=1: continue
        old=a[name][0]; new=b[name][0]; old_size=g.size(old.get('type_die')); new_size=new.get('byte_size')
        if old_size is not None and new_size is not None and old_size!=new_size:
            rows.append({'variable':name,'original_type':old['type'],'candidate_type':new['type'],
                         'original_bytes':old_size,'candidate_bytes':new_size,'candidate_minus_original':new_size-old_size,
                         'candidate_source_line':new.get('declaration_line')})
    return rows


def local_inventory(original,candidate):
    """Describe declaration evidence, never infer stack occupancy from type sizes."""
    g=graph(); sides={'original':defaultdict(list),'candidate':defaultdict(list)}
    for side,variables in [('original',original),('candidate',candidate)]:
        for v in variables:
            role=g.dies[v['die']]['tag'] if side=='original' else v.get('role')
            if role!='DW_TAG_variable' or v.get('address') is not None or not v.get('name'): continue
            sides[side][v['name']].append(v)
    rows=[]
    for name in sorted(sides['original'].keys()|sides['candidate'].keys()):
        a,b=sides['original'][name],sides['candidate'][name]
        if len(a)>1 or len(b)>1: state='AMBIGUOUS_NAME'
        elif not b: state='ORIGINAL_ONLY_DEBUG_DECLARATION'
        elif not a: state='CANDIDATE_ONLY_DEBUG_DECLARATION'
        else: state='UNIQUE_NAME_PAIR'
        def view(v,side):
            return {'die':v['die'],'type':v['type'],'scope':v.get('scope'),
                    'byte_size':g.size(v.get('type_die')) if side=='original' else v.get('byte_size'),
                    'location':v.get('location'),'declaration_line':v.get('declaration_line')}
        rows.append({'variable':name,'state':state,'original':[view(v,'original') for v in a],
                     'candidate':[view(v,'candidate') for v in b]})
    return {'declarations':rows,'counts':{state:sum(r['state']==state for r in rows) for state in
            ('UNIQUE_NAME_PAIR','ORIGINAL_ONLY_DEBUG_DECLARATION','CANDIDATE_ONLY_DEBUG_DECLARATION','AMBIGUOUS_NAME')},
            'limit':'Names are diagnostic correspondence only. Missing debug declarations may reflect optimization, renaming or source omissions. Shadowed names are not paired. Type sizes do not prove stack allocation: registers, lifetime reuse, spills, alignment and outgoing arguments require separate evidence.'}


def analyze(row,original,variables,candidate_variables):
    old=allocation(original); new=allocation(row.get('instructions',[]))
    if not old or not new or old['reserved_bytes']==new['reserved_bytes']: return None
    pair=row.get('first_instruction_pair',{})
    first=bool(pair.get('original') and pair.get('candidate') and
               pair['original']['address']==old['instruction']['address'] and pair['candidate']['address']==new['instruction']['address'])
    return {'original':old,'candidate':new,'candidate_minus_original':new['reserved_bytes']-old['reserved_bytes'],
            'first_mismatch_is_frame_allocation':first,'local_width_differences':local_widths(variables,candidate_variables),
            'local_inventory':local_inventory(variables,candidate_variables),
            'proof':'Decoded constant SUB ESP in the straight-line entry prefix; no branches/calls crossed.',
            'limit':'Local widths are unique-name DWARF evidence, not complete frame accounting. Spill slots, outgoing call arguments, alignment and lifetime reuse also affect allocation. This never proves body or layout-only equality.'}
