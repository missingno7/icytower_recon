"""Bounded pointee field correspondence; diagnostic only, never type identity."""
import re
from type_views import shape_key


def correspondence(candidate,historical):
    result={'candidate_size':candidate.get('size'),'historical_size':historical.get('size'),
            'state':'UNPROVEN','members':[],
            'limit':'Offsets and field shapes are diagnostic correspondence only. Renames, filler removal and aliasing require typed use-site evidence and strict contribution verification.'}
    if candidate.get('kind')!='structure_type' or historical.get('kind')!='structure_type':return result
    def valid(node):
        occupied=set()
        if not isinstance(node.get('size'),int) or node['size']<=0:return False
        for m in node.get('members',[]):
            offset=m.get('offset');size=m.get('layout',{}).get('size')
            if m.get('bitfield') or not isinstance(offset,int) or not isinstance(size,int) or size<=0 or offset<0 or offset+size>node['size']:return False
            extent=set(range(offset,offset+size))
            if extent&occupied:return False
            occupied.update(extent)
        return True
    if not valid(candidate) or not valid(historical):return result
    rows=[];matched=set()
    for old in historical['members']:
        hits=[m for m in candidate['members'] if m['offset']==old['offset'] and shape_key(m['layout'])==shape_key(old['layout'])]
        if len(hits)==1:
            new=hits[0];matched.add(new['name'])
            rows.append({'historical_member':old['name'],'candidate_member':new['name'],'offset':old['offset'],'size':old['layout']['size'],'state':'SAME_FIELD_SHAPE' if new['name']==old['name'] else 'RENAMED_FIELD_SHAPE'})
        else:rows.append({'historical_member':old['name'],'offset':old['offset'],'state':'NO_UNIQUE_CORRESPONDENCE'})
    extras=[{'member':m['name'],'offset':m['offset'],'size':m['layout']['size'],'type':m['layout'].get('type')} for m in candidate['members'] if m['name'] not in matched]
    result.update(state='FIELD_CORRESPONDENCE_ONLY',members=rows[:8],member_count=len(rows),omitted_members=max(0,len(rows)-8),
                  unmatched_candidate_members=extras[:8],unmatched_candidate_count=len(extras),omitted_unmatched=max(0,len(extras)-8))
    return result


def pointer_names(candidate,historical):
    if candidate.get('kind')!=historical.get('kind') or candidate.get('kind')!='pointer_type':return None
    if candidate.get('size')!=historical.get('size') or candidate.get('qualifiers') or historical.get('qualifiers'):return None
    names=[re.fullmatch(r'(\w+)\s*\*',n.get('type','')) for n in (candidate,historical)]
    return tuple(n[1] for n in names) if all(names) else None
