"""Conservative i386 DWARF location attribution. Diagnostic evidence, never match proof."""
import re
import struct
from types import SimpleNamespace
from common import ROOT,identity,run
from binary import Binary
from dwarf import parse,address_lists,file_tables,line_rows
from type_graph import TypeGraph,number
from dwarf_layout import layout

REGISTERS=('eax','ecx','edx','ebx','esp','ebp','esi','edi')
ALIASES={'al':'eax','ah':'eax','ax':'eax','cl':'ecx','ch':'ecx','cx':'ecx','dl':'edx','dh':'edx','dx':'edx','bl':'ebx','bh':'ebx','bx':'ebx','sp':'esp','bp':'ebp','si':'esi','di':'edi'}


def expression_at(location,lists,pc,base):
    if not location: return None
    if 'location list' in location:
        table=lists.get(number(location)); matches=[]
        for entry in table.get('entries',[]) if table else []:
            if entry['kind']=='base_address_selection': base=entry['end']; continue
            if base+entry['begin']<=pc<base+entry['end']: matches.append(entry['expression_hex'])
        return matches[0] if len(matches)==1 else None
    m=re.search(r'byte block:\s*((?:[0-9a-fA-F]{1,2}(?:\s+|$))+)',location)
    return ''.join('%02x'%int(t,16) for t in m[1].split()) if m else None


def signed_leb(code,start):
    value=0; shift=0; pos=start
    while pos<len(code) and shift<35:
        byte=code[pos]; pos+=1; value|=(byte&127)<<shift; shift+=7
        if not byte&128:
            if byte&64: value-=1<<shift
            return value,pos
    raise ValueError('Incomplete or oversized DWARF signed LEB')


def decode_location(expression,frame=None):
    if not expression: return None
    try:
        code=bytes.fromhex(expression); op=code[0]
        if len(code)==1 and 0x50<=op<=0x57: return {'kind':'register','register':REGISTERS[op-0x50]}
        if 0x70<=op<=0x77 or op==0x91:
            offset,end=signed_leb(code,1)
            if end!=len(code): return None
            if op==0x91:
                if not frame or frame['kind'] not in ('register','memory') or 'register' not in frame: return None
                return {'kind':'memory','register':frame['register'],'offset':frame.get('offset',0)+offset}
            return {'kind':'memory','register':REGISTERS[op-0x70],'offset':offset}
        if len(code)==5 and op==3: return {'kind':'memory','address':struct.unpack_from('<I',code,1)[0]}
    except (ValueError,IndexError): pass
    # Pieces, stack values, CFA-dependent and compound expressions are not guessed.
    return None


def scope_contains(scope,pc,base):
    if scope.get('low_pc') is not None and scope.get('high_pc') is not None:
        return scope['low_pc']<=pc<scope['high_pc']
    entries=scope.get('range_list',{}).get('entries',[]) if scope.get('range_list') else []
    if not entries: return False
    for entry in entries:
        if entry['kind']=='base_address_selection': base=entry['end']; continue
        if base+entry['begin']<=pc<base+entry['end']: return True
    return False


def annotate(rows,variables,frame_location,locations,base,scopes=None):
    scopes=scopes or {}; result=[]
    for row in rows:
        pc=row['address']; frame=decode_location(expression_at(frame_location,locations,pc,base))
        registers={ALIASES.get(r,r) for r in re.findall(r'%([a-z]+)',row['assembly'])}
        memories=[]
        for m in re.finditer(r'(?P<off>-?0x[0-9a-f]+|-?\d+)?\(%(?P<reg>e[a-z]{2})\)',row['assembly']):
            memories.append((m['reg'],int(m['off'],0) if m['off'] else 0))
        uses=[]
        for variable in variables:
            scope=scopes.get(variable.get('scope'))
            if scope is not None and not scope_contains(scope,pc,base): continue
            expression=expression_at(variable.get('location'),locations,pc,base)
            location=decode_location(expression,frame)
            if not location: continue
            relation=None
            if location['kind']=='register' and location['register'] in registers: relation='register is used'
            elif location['kind']=='memory' and (location.get('register'),location.get('offset')) in memories: relation='variable storage is addressed'
            elif location['kind']=='memory' and location.get('address') is not None and re.search(r'(?<![0-9a-f])0x%x(?![0-9a-f])'%location['address'],row['assembly']): relation='absolute variable storage is addressed'
            if relation:
                uses.append({k:variable.get(k) for k in ('die','name','type','base_type','base_encoding')} | {'location':location,'expression_hex':expression,'relation':relation})
        result.append({**row,'dwarf_variables':uses})
    return result


def candidate_debug(build,objdump):
    path=build['command'][-1]
    if identity(path)!=build['object']: raise ValueError('Candidate object changed; fresh-verify '+build['target'])
    obj=Binary(path); dies,_=parse(run([objdump,'--dwarf=info',path])); graph=TypeGraph(dies.values())
    tables={}
    for name in ('.debug_loc','.debug_ranges'):
        section=next((s for s in obj.sections if s['name']==name),None)
        if section is None: tables[name]=[]; continue
        symbol=next((s for s in obj.symbols if s['name']==name and s['aux_count']),None)
        size=struct.unpack_from('<I',bytes.fromhex(symbol['aux_hex']))[0] if symbol else section['raw_size']
        proxy=SimpleNamespace(sections=[dict(section,virtual_size=size)],section_bytes=obj.section_bytes)
        tables[name]=address_lists(proxy,name)
    ranges={r['offset']:r for r in tables['.debug_ranges']}; functions={}
    source_tables={t['offset']:t for t in file_tables(run([objdump,'--dwarf=rawline',path]))}
    for d in dies.values():
        if d['tag']!='DW_TAG_subprogram' or d.get('low_pc') is None: continue
        variables=[]; scopes={}
        for node in graph.descendants(d['offset']):
            if node['tag'] in ('DW_TAG_variable','DW_TAG_formal_parameter'):
                try:
                    variable=graph.variable(node)
                    table=source_tables.get(number(dies[node['cu']]['resolved'].get('DW_AT_stmt_list')),{})
                    entry=table.get('files',{}).get(number(node['resolved'].get('DW_AT_decl_file')),{})
                    variable.update(role=node['tag'],declaration_line=number(node['resolved'].get('DW_AT_decl_line')),
                                    declaration_file=entry.get('path'),byte_size=graph.size(node.get('type_ref')),
                                    constant_value=node['resolved'].get('DW_AT_const_value'),
                                    function_scope=node.get('parent')==d['offset'])
                    variables.append(variable)
                except ValueError: continue
            if node['tag'] in ('DW_TAG_lexical_block','DW_TAG_inlined_subroutine'):
                scopes[str(node['offset'])]={'low_pc':node.get('low_pc'),'high_pc':node.get('high_pc'),'range_list':ranges.get(number(node['resolved'].get('DW_AT_ranges')))}
        functions[d['name']]={'base':dies[d['cu']].get('low_pc') or 0,'frame_location':d['resolved'].get('DW_AT_frame_base'),'variables':variables,'scopes':scopes}
    if identity(path)!=build['object']: raise ValueError('Candidate object changed during diagnostic extraction')
    globals_=[{'name':d['name'],'die':d['offset'],'layout':layout(graph,d.get('type_ref'))}
              for d in dies.values() if d['tag']=='DW_TAG_variable' and d.get('name') and dies.get(d.get('parent'),{}).get('tag')=='DW_TAG_compile_unit']
    maintained_names=set()
    for source in build['local_inputs']:
        if source.startswith(('src/','include/')):
            maintained_names.update(re.findall(r'\b[A-Za-z_]\w*\b',(ROOT/source).read_bytes().decode('cp1252')))
    typedefs=[{'name':d['name'],'die':d['offset'],'layout':layout(graph,d.get('type_ref')),
               'alias_of':dies[d['type_ref']]['name'] if d.get('type_ref') and dies[d['type_ref']]['tag']=='DW_TAG_typedef' else None}
              for d in dies.values() if d['tag']=='DW_TAG_typedef' and d.get('name') in maintained_names]
    from storage_diagnostics import storage_rows
    storage=storage_rows(graph,obj,source_tables)
    return {'schema':7,'line_mappings':line_rows(run([objdump,'--dwarf=decodedline',path])),'storage':storage,'typedefs':typedefs,'object':build['object'],'location_lists':tables['.debug_loc'],'functions':functions,'globals':globals_,
            'limit':'Decoded live locations are diagnostic associations, not proof of value equivalence.'}
