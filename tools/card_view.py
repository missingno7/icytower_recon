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
    offset=(card.get('first_difference') or {}).get('offset',0)
    for key in ('relocation_mismatches','direct_transfer_mismatches'):
        rows=card[key]; card['evidence_counts'][key]=len(rows)
        if len(rows)>8: card[key]=sorted(rows,key=lambda r:abs(r['function_offset']-offset))[:8]
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
        card[key]=list(grouped.values())
    card['evidence_note']='Lists with counts may show only the nearest eight entries. Complete target-only evidence, locations and ownership are in detailed_evidence.'
    return card
