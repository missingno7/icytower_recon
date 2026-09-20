"""Only explicit, compiled aliases to generated canonical layouts normalize interfaces."""
import re
from collections import defaultdict
from common import ROOT,identity
from type_graph import graph
from dwarf_layout import layout
from type_views import shape_key


def canonical_aliases(report):
    g=graph(); types=defaultdict(list)
    for t in report.get('candidate_debug',{}).get('typedefs',[]): types[t['name']].append(t)
    aliases={}
    for name,rows in types.items():
        if len(rows)!=1 or not rows[0].get('alias_of'): continue
        chain=[name]; target=rows[0]['alias_of']
        while target not in chain and len(types.get(target,[]))==1:
            chain.append(target); node=types[target][0]
            header='include/recovered/'+target+'.h'
            if target in g.game_types and header in report['build']['local_inputs']:
                if identity(ROOT/header)!=report['build']['local_inputs'][header]: break
                expected=[layout(g,d['type_ref']) for d in g.game_types[target]]
                if all(shape_key(rows[0]['layout'])==shape_key(x)==shape_key(node['layout']) for x in expected): aliases[name]=target
                break
            target=node.get('alias_of')
    return aliases


def canonical_type(text,aliases):
    # Deliberately avoid rewriting tokens inside tags, anonymous structs or callbacks.
    simple=re.fullmatch(r'(?:(?:const|volatile)\s+)*(?P<name>[A-Za-z_]\w*)(?:(?:\s*\*\s*(?:(?:const|volatile)\s*)*)|(?:\s*\[\d*\]))*',text)
    if not simple: return text
    start,end=simple.span('name')
    return text[:start]+aliases.get(simple['name'],simple['name'])+text[end:]


def annotate_declaration(row,aliases):
    return {**row,'canonical_return_type':canonical_type(row['return_type'],aliases),
            'canonical_parameter_types':[canonical_type(p,aliases) for p in row['parameter_types']]}

def layout_checks(declaration,original,report):
    """Compare game aggregate definitions, even when declarations use the same name."""
    g=graph(); types=defaultdict(list)
    for t in report.get('candidate_debug',{}).get('typedefs',[]): types[t['name']].append(t)
    pairs=[('return',original['return_type'],declaration['return_type'])]
    pairs += [('parameter '+str(i+1),a,b) for i,(a,b) in enumerate(zip(original['parameter_types'],declaration['parameter_types']))]
    result=[]
    for position,old_text,new_text in pairs:
        a=re.fullmatch(r'(?:(?:const|volatile)\s+)*(\w+)(?:\s*\*\s*(?:(?:const|volatile)\s*)*)*',old_text)
        b=re.fullmatch(r'(?:(?:const|volatile)\s+)*(\w+)(?:\s*\*\s*(?:(?:const|volatile)\s*)*)*',new_text)
        if not a or a[1] not in g.game_types: continue
        expected=[layout(g,d['type_ref']) for d in g.game_types[a[1]]]
        item={'position':position,'historical_type':a[1],'candidate_type':b[1] if b else new_text,
              'header':'include/recovered/'+a[1]+'.h','status':'UNAVAILABLE'}
        if not b or len(types[b[1]])!=1:
            item['reason']='Candidate named type layout is missing or ambiguous'; result.append(item); continue
        current=types[b[1]][0]['layout']
        if not current.get('size'):
            item['reason']='Candidate type is incomplete'; result.append(item); continue
        if all(shape_key(current)==shape_key(e) for e in expected):
            item['status']='AGREE'; result.append(item); continue
        item['status']='MISMATCH'; item['historical_size']=expected[0].get('size'); item['candidate_size']=current.get('size')
        old_members={m['name']:m for m in expected[0].get('members',[])}; new_members={m['name']:m for m in current.get('members',[])}
        diffs=[]
        for name in sorted(old_members.keys()|new_members.keys()):
            old=old_members.get(name); new=new_members.get(name)
            if old and new and old['offset']==new['offset'] and old['bitfield']==new['bitfield'] and shape_key(old['layout'])==shape_key(new['layout']): continue
            def concise(member):
                if not member: return None
                return {'offset':member['offset'],'size':member['layout'].get('size'),'type':member['layout'].get('type'),
                        'qualifiers':member['layout'].get('qualifiers',[]),'bitfield':member['bitfield']}
            diffs.append({'member':name,'historical':concise(old),'candidate':concise(new)})
        item.update(member_difference_count=len(diffs),first_member_differences=diffs[:6],reason='Complete aggregate layout/type differs despite any matching declaration spelling')
        result.append(item)
    return result
