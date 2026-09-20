"""Shared anonymous literal consumers, diagnostic only; never a binding oracle."""
from collections import defaultdict


def groups(report):
    sections=[s for s in report.get('object_sections',[]) if s['name']=='.rdata']
    if len(sections)!=1: return []
    target=report['build']['target']; source=report['build']['config']['source']
    references=defaultdict(list); observations=defaultdict(list)
    for row in report['functions']:
        diagnostics={d['function_offset']:d for d in row.get('literal_diagnostics',[])}
        for r in row.get('relocations',[]):
            if r.get('type')!=6 or r.get('symbol')!='.rdata': continue
            addend=r['addend']; d=diagnostics.get(r['function_offset'])
            alignment='UNPROVEN'
            if d and d.get('kind') in ('C_STRING','FLOAT32','FLOAT64') and d.get('historical_operand_va')==r.get('original_value') and r.get('original_value') is not None:
                alignment='ALIGNED_LITERAL_OPERAND'
            elif not d and row.get('body_shape_equal',row.get('masked_equal')) and row.get('instruction_boundaries_verified'):
                alignment='WHOLE_BODY_INSTRUCTION_CORRESPONDENCE'
            references[addend].append({'function':row['name'],'function_offset':r['function_offset'],
                'historical_operand_va':r.get('original_value') if alignment!='UNPROVEN' else None,
                'historical_operand_alignment':alignment,
                'unaligned_original_field_value':r.get('original_value') if alignment=='UNPROVEN' else None,
                'independently_resolved_va':r.get('target_va'),
                'relocation_equal':r.get('equal',False),'resolution':r.get('resolution'),
                'candidate_source_lines':d.get('candidate_source_lines',[]) if d else []})
            if d and d.get('kind') in ('C_STRING','FLOAT32','FLOAT64'):
                observations[addend].append(d)
    result=[]
    for addend,observed in sorted(observations.items()):
        consumers=references[addend]; addresses=sorted({r['historical_operand_va'] for r in consumers if r['historical_operand_va'] is not None})
        payloads=sorted({(d['kind'],d['candidate_hex']) for d in observed})
        path='docs/current/literals/'+target+'/'+format(addend,'x')+'.json'
        result.append({'state':'UNRESOLVED_LITERAL_EVIDENCE','source':source,'target':target,
            'candidate_section':'.rdata','candidate_section_index':sections[0]['index'],'candidate_addend':addend,
            'candidate_card':path,'source_identity':report['build'].get('local_inputs',{}).get(source),'consumers':consumers,'consumer_functions':sorted({r['function'] for r in consumers}),
            'historical_observed_addresses':addresses,'multiple_historical_addresses':len(addresses)>1,
            'candidate_payloads':[{'kind':kind,'hex':payload,'bytes':len(bytes.fromhex(payload))+(kind=='C_STRING')} for kind,payload in payloads],
            'observations':observed,'placement_confidence':'UNPROVEN',
            'limit':'Candidate COFF addend sharing only. Only aligned historical operands are addresses; bytes at unaligned candidate offsets remain uninterpreted values. Historical operands are observations, not independent owner bindings. Equal contents, peer references and a single observed address cannot establish placement, source causality, body equality or promotion.'})
    return result


def for_function(groups_,name):
    result=[]
    for group in groups_:
        own=[r for r in group['consumers'] if r['function']==name and not r['relocation_equal']]
        if not own: continue
        peers=[n for n in group['consumer_functions'] if n!=name]
        result.append({k:group[k] for k in ('candidate_section','candidate_addend','candidate_card','placement_confidence','multiple_historical_addresses')} |
            {'function_offsets':[r['function_offset'] for r in own],'peer_function_count':len(peers),'peer_functions':peers[:6],
             'historical_address_count':len(group['historical_observed_addresses']),
             'unaligned_reference_count':sum(r['historical_operand_alignment']=='UNPROVEN' for r in group['consumers']),
             'limit':'Shared pool evidence only. Do not edit peer functions or infer an owner binding from these references.'})
    return result


def publish(report,root,emit):
    active=set()
    for group in groups(report):
        path=root/group['candidate_card']; active.add(path); emit(path,group)
    directory=root/'docs/current/literals'/report['build']['target']
    for path in directory.glob('*.json'):
        if path not in active: emit(path,{'state':'NO_CURRENT_UNRESOLVED_LITERAL','placement_confidence':'NOT_APPLICABLE'})


def publish_function(report,name,root,directory,emit):
    """FAST artifacts must not point at a possibly older canonical literal pool."""
    selected=[]
    for group in groups(report):
        if not any(r['function']==name and not r['relocation_equal'] for r in group['consumers']): continue
        group['candidate_card']=directory+'/'+format(group['candidate_addend'],'x')+'.json'
        emit(root/group['candidate_card'],group); selected.append(group)
    return for_function(selected,name)


def pattern_prerequisites(row,patterns):
    """Name unresolved relocations which the generated source recipe does not fix."""
    if not patterns: return []
    ids={p['id'] for p in patterns}; covered=set()
    if ids & {'repair_literal_content','repair_symbolic_assignment'}:
        covered.update(d['function_offset'] for d in row.get('literal_diagnostics',[]) if d['classification']=='LITERAL_CONTENT_DIFFERENCE' and d.get('kind')=='C_STRING')
    if 'repair_symbolic_assignment' in ids:
        covered.update(d['function_offset'] for d in row.get('reference_diagnostics',[]) if d['classification']=='SYMBOLIC_REFERENCE_DIFFERENCE' and d['prerequisite']=='SOURCE_REFERENCE_REPAIR')
    observations={d['function_offset']:d['classification'] for d in row.get('literal_diagnostics',[])}
    return [{'function_offset':r['function_offset'],'symbol':r['symbol'],
             'reason':observations.get(r['function_offset'],r.get('resolution','Unresolved relocation')),
             'limit':'The generated source recipe does not repair this independent binding; owner/interface evidence is still required.'}
            for r in row.get('relocations',[]) if not r.get('equal') and r['function_offset'] not in covered]
