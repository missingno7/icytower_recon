"""Compact task cards with function-only drill-down; never discard archived evidence."""
import copy
from pathlib import Path


def detail_path(card):
    return 'docs/current/function-evidence/'+Path(card['source']).stem+'/'+card['function']+'.json'


def compact_card(full,details=None):
    card=copy.deepcopy(full); details=details or detail_path(full)
    card['detailed_evidence']=details; card['evidence_counts']={}
    for key in ('parameters','locals'):
        card[key]=[{k:v for k,v in variable.items() if k!='location_list'} for variable in card[key]]
    card['lexical_blocks']=[{k:v for k,v in block.items() if k!='range_list'} for block in card['lexical_blocks']]
    card['signedness']['variables']=[{k:v for k,v in variable.items() if k not in ('location_list','location')} for variable in card['signedness']['variables']]
    inventory=(card.get('frame_layout') or {}).get('local_inventory')
    if inventory:
        rows=inventory['declarations']
        # Keep mismatched/missing/ambiguous declarations ahead of routine pairs.
        def rank(row):
            if row['state']!='UNIQUE_NAME_PAIR': return 0
            a,b=row['original'][0],row['candidate'][0]
            return 1 if (a['type'],a['byte_size'])!=(b['type'],b['byte_size']) else 2
        inventory['declarations']=sorted(rows,key=rank)[:8]
        inventory['omitted_declarations']=max(0,len(rows)-8)
        card['evidence_counts']['frame_local_declarations']=len(rows)
    offset=(card.get('first_difference') or {}).get('offset',0)
    for key in ('relocation_mismatches','direct_transfer_mismatches'):
        rows=card[key]; card['evidence_counts'][key]=len(rows)
        if len(rows)>8: card[key]=sorted(rows,key=lambda r:abs(r['function_offset']-offset))[:8]
    callee_scope=card.get('callee_interface_scope')
    if callee_scope:
        observations=callee_scope['observations']
        card['evidence_counts']['callee_interface_observations']=len(observations)
        callee_scope['omitted_observations']=max(0,len(observations)-8)
        callee_scope['observations']=sorted(observations,key=lambda r:(not r['blocking'],min((abs(n-offset) for n in r['call_offsets']),default=float('inf'))))[:8]
        for observation in callee_scope['observations']:
            observation['call_offset_count']=len(observation['call_offsets'])
            observation['call_offsets']=sorted(observation['call_offsets'],key=lambda n:abs(n-offset))[:8]
    if 'ownership_prerequisites' in card:
        card['evidence_counts']['ownership_prerequisites']=len(card['ownership_prerequisites'])
        card['ownership_prerequisites']=sorted(card['ownership_prerequisites'],key=lambda r:abs(r['function_offset']-offset))[:8]
    if 'reference_diagnostics' in card:
        card['evidence_counts']['reference_diagnostics']=len(card['reference_diagnostics'])
        card['reference_diagnostics']=sorted(card['reference_diagnostics'],key=lambda r:abs(r['function_offset']-offset))[:8]
    if 'literal_diagnostics' in card:
        card['evidence_counts']['literal_diagnostics']=len(card['literal_diagnostics'])
        card['literal_diagnostics']=sorted(card['literal_diagnostics'],key=lambda r:abs(r['function_offset']-offset))[:8]
    if 'literal_dependencies' in card:
        card['evidence_counts']['literal_dependencies']=len(card['literal_dependencies'])
        card['literal_dependencies']=card['literal_dependencies'][:8]
    card['evidence_counts']['original_calls']=len(card['original_calls'])
    card['original_calls']=sorted(card['original_calls'],key=lambda r:abs(r['address']-int(card['historical_va'],16)-offset))[:8]
    for key in ('calls','referenced_globals'):
        rows=card[key]; grouped={}
        for row in rows:
            address=row.get('historical_address',row.get('target_va'))
            identity=(row.get('symbol'),address,row.get('candidate_addend') if address is None else None)
            if identity not in grouped:
                grouped[identity]={k:v for k,v in row.items() if k not in ('coff_symbols','original_coff_symbols','coff_contribution_evidence','object_owners')}
                grouped[identity]['reference_count']=0
                grouped[identity]['function_offsets']=[]
            item=grouped[identity]
            item['reference_count']+=len(row.get('references',[None]))
            positions=row.get('references',[row.get('function_offset')])
            item['function_offsets'].extend(p for p in positions if isinstance(p,int))
        card['evidence_counts'][key]=len(rows)
        for item in grouped.values():
            item['function_offsets']=sorted(item['function_offsets'],key=lambda n:abs(n-offset))[:8]
            item.pop('references',None)
        groups=list(grouped.values())
        card['evidence_counts'][key+'_groups']=len(groups)
        # Unknown positions sort last, not as if they occurred at offset zero.
        def distance(item):
            return min((abs(p-offset) for p in item['function_offsets']),default=float('inf'))
        card[key]=sorted(groups,key=distance)[:8]
        card['evidence_counts'][key+'_omitted_groups']=max(0,len(groups)-8)
    card['evidence_note']='Lists with counts may show only the nearest eight entries. Complete target-only evidence, locations and ownership are in detailed_evidence.'
    return card
