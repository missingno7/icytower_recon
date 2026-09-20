"""Compact typed byte paths for diagnostics. Padding/overlap is never guessed."""
import math


def layout(graph,offset,seen=()):
    if offset is None or offset in seen: return {'kind':'unknown','size':None}
    d=graph.dies[offset]; tag=d['tag'].removeprefix('DW_TAG_'); ref=d.get('type_ref')
    if tag=='typedef': return layout(graph,ref,(*seen,offset))
    if tag in ('const_type','volatile_type'):
        node=dict(layout(graph,ref,(*seen,offset)))
        node['qualifiers']=sorted(set(node.get('qualifiers',[]))|{tag.removesuffix('_type')})
        return node
    try: spelling=graph.declaration(offset)
    except ValueError: spelling=d.get('name') or tag
    node={'kind':tag,'size':graph.size(offset),'type':spelling}
    if tag=='array_type':
        node.update(dimensions=graph.dimensions(offset),element=layout(graph,ref,(*seen,offset)))
    elif tag=='structure_type':
        node['members']=[]
        for member in graph.children[offset]:
            if member['tag']!='DW_TAG_member': continue
            node['members'].append({'name':member.get('name'),'offset':graph.member_offset(member),
                                    'bitfield':'DW_AT_bit_size' in member['resolved'],
                                    'layout':layout(graph,member.get('type_ref'),(*seen,offset))})
    elif tag=='base_type': node['encoding']=d['resolved'].get('DW_AT_encoding')
    return node


def locate(node,offset,expression='',base=0,steps=()):
    size=node.get('size')
    if not size or not 0<=offset<size: return None
    if node['kind']=='array_type':
        dimensions=node['dimensions']; element=node['element']; stride=element.get('size')
        if not stride or not dimensions or any(n is None or n<=0 for n in dimensions): return None
        path=list(steps); text=expression; delta=0
        for pos,count in enumerate(dimensions):
            width=stride*math.prod(dimensions[pos+1:]); index=offset//width
            if index>=count: return None
            path.append({'index':index}); text+='[%d]'%index; delta+=index*width; offset%=width
        return locate(element,offset,text,base+delta,tuple(path))
    if node['kind']=='structure_type':
        hits=[]
        for index,member in enumerate(node['members']):
            start=member['offset']; width=member['layout'].get('size')
            if start is None or not width: continue
            if start<=offset<start+width:
                if member['bitfield'] or not member['name']: return None
                hit=locate(member['layout'],offset-start,expression+'.'+member['name'],base+start,
                           (*steps,{'member':member['name'],'index':index}))
                if hit: hits.append(hit)
        return hits[0] if len(hits)==1 else None
    if node['kind'] not in ('base_type','pointer_type','enumeration_type'): return None
    return {'expression':expression,'offset':base,'size':size,'kind':node['kind'],'type':node['type'],
            'encoding':node.get('encoding'),'steps':list(steps)}


def reference(node,offset,name):
    if offset==0 and node.get('size'):
        return {'expression':name,'offset':0,'size':node['size'],'kind':node['kind'],'type':node['type'],'steps':[]}
    field=locate(node,offset,name)
    return field if field and field['offset']==offset else None
