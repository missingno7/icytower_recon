"""Focused before/after candidate evidence. Never an acceptance predicate."""
from collections import Counter
from instructions import window
from scheduling_diagnostics import byte_stream


def function_change(old,new):
    if old is None or new is None:
        return {'function':(old or new)['name'],'observation':'FUNCTION_INVENTORY_CHANGED'}
    a=old.get('instructions',[]); b=new.get('instructions',[])
    placement=(old.get('candidate_offset'),old.get('candidate_size'))!=(new.get('candidate_offset'),new.get('candidate_size'))
    same_bytes=[r['bytes'] for r in a]==[r['bytes'] for r in b]
    if same_bytes and not placement and old['status']==new['status']: return None
    result={'function':old['name'],'status_before':old['status'],'status_after':new['status'],
            'workflow_before':old.get('workflow',{}).get('state'),'workflow_after':new.get('workflow',{}).get('state'),
            'offset_before':old.get('candidate_offset'),'offset_after':new.get('candidate_offset'),
            'size_before':old.get('candidate_size'),'size_after':new.get('candidate_size'),
            'emitted_instruction_bytes_equal':same_bytes,
            'source_body_unchanged':bool(old.get('source_body_sha256') and old.get('source_body_sha256')==new.get('source_body_sha256'))}
    raw_a=byte_stream(a,old.get('candidate_offset',0),old.get('candidate_size',0))
    raw_b=byte_stream(b,new.get('candidate_offset',0),new.get('candidate_size',0))
    if raw_a is None or raw_b is None:
        result['observation']='INCOMPLETE_INSTRUCTION_STREAM';return result
    differences=[i for i,(x,y) in enumerate(zip(raw_a,raw_b)) if x!=y]
    if len(raw_a)!=len(raw_b): differences.append(min(len(raw_a),len(raw_b)))
    result['first_difference']=differences[0] if differences else None
    result['differing_byte_count']=sum(x!=y for x,y in zip(raw_a,raw_b))+abs(len(raw_a)-len(raw_b))
    result['difference_offsets']=differences[:16]
    first=differences[0] if differences else 0
    result['disassembly']={'before':window(a,old.get('candidate_offset',0)+first,2),
                           'after':window(b,new.get('candidate_offset',0)+first,2)}
    result['observation']='CANDIDATE_BYTES_OR_PLACEMENT_CHANGED'
    if differences and len(raw_a)==len(raw_b):
        bases=(old['candidate_offset'],new['candidate_offset'])
        boundaries=[]
        for rows,base in zip((a,b),bases):
            boundaries.append({r['address']-base for r in rows}|{len(raw_a)})
        shared=boundaries[0]&boundaries[1]
        start=max((p for p in shared if p<=differences[0]),default=None)
        end=min((p for p in shared if p>differences[-1]),default=None)
        if start is not None and end is not None and end-start<=64:
            slices=[[r for r in rows if start<=r['address']-base<end] for rows,base in zip((a,b),bases)]
            if 2<=len(slices[0])<=8 and len(slices[0])==len(slices[1]) and Counter(r['bytes'] for r in slices[0])==Counter(r['bytes'] for r in slices[1]):
                result.update(observation='INSTRUCTION_PERMUTATION_OBSERVED',permutation_window={'start':start,'end':end,'before':slices[0],'after':slices[1],
                    'limit':'Same instruction bytes in a different order. Data/flag dependencies, entry points, aliasing and observability are not proven safe; this never permits acceptance.'})
    return result


def compare(before,after):
    def sections(report):
        result={}
        for s in report['object_sections']:
            if not s['name'].startswith('.debug'):
                result.setdefault(s['name'],[]).append({k:s.get(k) for k in ('virtual_size','raw_size','characteristics','sha256')})
        return result
    a,b=sections(before),sections(after)
    section_changes=[{'section':name,'before':a.get(name),'after':b.get(name)} for name in sorted(a.keys()|b.keys()) if a.get(name)!=b.get(name)]
    a={r['name']:r for r in before['functions']};b={r['name']:r for r in after['functions']}
    changes=[change for name in sorted(a.keys()|b.keys()) if (change:=function_change(a.get(name),b.get(name))) is not None]
    from interface_tasks import contribution_fingerprint
    old_fp,new_fp=contribution_fingerprint(before),contribution_fingerprint(after)
    metadata=[]
    for key in ('relocations','defined','common'):
        if old_fp[key]!=new_fp[key]:
            old_only=[r for r in old_fp[key] if r not in new_fp[key]]
            new_only=[r for r in new_fp[key] if r not in old_fp[key]]
            metadata.append({'kind':key,'before_only_count':len(old_only),'after_only_count':len(new_only),'before_examples':old_only[:4],'after_examples':new_only[:4]})
    return {'scope':'Candidate-to-candidate diagnostics only; never original matching or permission to bypass a gate.',
            'changed_sections':section_changes,'changed_functions':changes,
            'metadata_changes':metadata,'preservation_fingerprint_equal':old_fp==new_fp}
