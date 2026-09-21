"""Conservative scratch-only renamed-pointee recipe. Not grinder admission."""
import re
from interface_type_probe import interface_typedefs
from type_graph import graph
from dwarf_layout import layout
from type_views import STRUCT,shape_key
from pointee_diagnostics import correspondence,pointer_names
from source_scope import sanitized
from source_order import definition_spans
from interface_tasks import patch_text


def plan(report,text,parent,member):
    types=interface_typedefs(report);g=graph()
    def one(name):
        rows=[t for t in types if t['name']==name]
        if len(rows)!=1:raise ValueError('Missing or ambiguous compiled type: '+name)
        return rows[0]['layout']
    historical=[layout(g,d['type_ref']) for d in g.game_types.get(parent,[])]
    if not historical or any(shape_key(h)!=shape_key(historical[0]) for h in historical):raise ValueError('Ambiguous historical parent')
    def field(node):
        rows=[m for m in node.get('members',[]) if m['name']==member]
        if len(rows)!=1 or rows[0]['bitfield']:raise ValueError('Parent field missing or ambiguous')
        return rows[0]
    a,b=field(one(parent)),field(historical[0]);names=pointer_names(a['layout'],b['layout'])
    if not names or a['offset']!=b['offset']:raise ValueError('Unsupported parent pointer')
    alias,canonical=names
    if alias==canonical:raise ValueError('No renamed pointee')
    expected=[layout(g,d['type_ref']) for d in g.game_types.get(canonical,[])]
    if not expected or any(shape_key(h)!=shape_key(expected[0]) for h in expected):raise ValueError('Ambiguous historical pointee')
    evidence=correspondence(one(alias),expected[0])
    if evidence['state']!='FIELD_CORRESPONDENCE_ONLY' or evidence['candidate_size']!=evidence['historical_size'] or evidence['omitted_members'] or evidence['omitted_unmatched']:raise ValueError('Incomplete field correspondence')
    if any(m['state'] not in ('SAME_FIELD_SHAPE','RENAMED_FIELD_SHAPE') for m in evidence['members']):raise ValueError('Unmapped historical field')
    clean=sanitized(text);definitions=definition_spans(text)
    structs=list(STRUCT.finditer(clean));decls=[s for s in structs if s[3]==alias];parents=[s for s in structs if s[3]==parent]
    if len(decls)!=1 or len(parents)!=1:raise ValueError('Unique source typedefs required')
    declaration=decls[0];parent_decl=parents[0];edits=[]
    if declaration[1] and re.search(r'\bstruct\s+'+re.escape(declaration[1])+r'\b',clean[:declaration.start()]+clean[declaration.end():]):raise ValueError('Tagged pointee used externally')
    for extra in evidence['unmatched_candidate_members']:
        original=next(m for m in one(alias)['members'] if m['name']==extra['member']);node=original['layout']
        if node['kind']!='array_type' or node['element'].get('size')!=1 or re.search(r'(?:->|\.)\s*'+re.escape(extra['member'])+r'\b',clean):raise ValueError('Unmatched field is not unused byte filler')
    def edit(start,end,after,reason):edits.append({'start':start,'end':end,'before':text[start:end],'after':after,'reason':reason})
    newline='\r\n' if '\r\n' in text else '\n'
    edit(declaration.start(),declaration.end(),'#include "recovered/'+canonical+'.h"'+newline+'typedef '+canonical+' '+alias+';','Canonical pointee with explicit legacy sizeof alias')
    pointer=list(re.finditer(r'\b'+re.escape(alias)+r'\s*\*\s*'+re.escape(member)+r'\s*;',parent_decl[0]))
    if len(pointer)!=1:raise ValueError('Unique parent pointer declaration required')
    start=parent_decl.start()+pointer[0].start();edit(start,start+len(alias),canonical,'Historical parent member pointee')
    for use in re.finditer(r'\b'+re.escape(alias)+r'\b',clean):
        if declaration.start()<=use.start()<declaration.end() or use.start()==start:continue
        if not re.search(r'\bsizeof\s*\(\s*$',clean[:use.start()]) or not re.match(r'\s*\)',clean[use.end():]):raise ValueError('Pointee used outside supported sizeof/member scope')
    for mapping in evidence['members']:
        old,new=mapping['candidate_member'],mapping['historical_member']
        if old==new:continue
        for access in re.finditer(r'(?:->|\.)\s*('+re.escape(old)+r')\b',clean):
            prefix=re.search(r'\b(\w+)\s*->\s*'+re.escape(member)+r'\s*\[\s*(?:\w+|[0-9]+)\s*\]\s*\.\s*$',clean[:access.start(1)])
            if not prefix:raise ValueError('Unsupported renamed member access')
            if re.search(r'(?:\.|->)\s*$',clean[:prefix.start()]):raise ValueError('Member-chain root is not the compiled local variable')
            owners=[f for f in definitions if f['body_start']<access.start()<f['end']]
            if len(owners)!=1:raise ValueError('Unique function owner required')
            variables=report['candidate_debug']['functions'].get(owners[0]['name'],{}).get('variables',[])
            roots=[v for v in variables if v['name']==prefix[1]]
            if len(roots)!=1 or not roots[0].get('function_scope') or roots[0]['type'].replace(' ','')!=parent+'*':raise ValueError('Unique compiled parent pointer variable required')
            edit(access.start(1),access.end(1),new,'Compiler-typed '+owners[0]['name']+':'+prefix[1]+'->'+member+' field correspondence')
    return patch_text(text,edits),{'parent':parent,'member':member,'pointee':evidence,'changes':edits,
        'scope':'Scratch experiment only. This recipe does not prove macro semantics, type identity, emission preservation or eligibility for promotion.'}
