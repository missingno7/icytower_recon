"""Compare entire compiled CUs, with function extents taken from DWARF.

Masked equality alone is CODEGEN_SIMILAR. FUNCTION_MATCH requires matching
length plus every byte after independently resolving each relocation symbol.
No original bytes are used by compilation, only by this verifier.
"""
import argparse
import json
import struct
from pathlib import Path
from common import ROOT, identity, read_json, run, write_json
from binary import Binary
from dwarf import parse
from build import TARGETS, COMPILERS, verify_inputs, compile_target
from instructions import decode, zero_clear_projection
from data_owners import independent_owners, resolve_owner
from control_transfers import resolve as resolve_transfers,tail_layout,complete_stream

def original_contributions(exe, cu_file, text_va):
    """Select one COFF FILE group by filename AND its text contribution VA."""
    groups=[]
    group=[]
    for symbol in exe.symbols:
        if symbol['storage_class']==103:
            if group: groups.append(group)
            group=[]
        group.append(symbol)
    if group: groups.append(group)
    matches=[g for g in groups if any(s['name']=='.text' and s.get('va')==text_va
             and s['file']==cu_file and s['storage_class']==3 and s['aux_count'] for s in g)]
    return matches[0] if len(matches)==1 else []

def compare(obj_path,cu_path,exe_path,analysis_objdump):
    obj,exe=Binary(obj_path),Binary(exe_path)
    original=[f for f in read_json(ROOT/'evidence/census/functions.json') if f['compile_unit']==cu_path]
    cu=next(c for c in read_json(ROOT/'evidence/census/compilation-units.json') if c['path']==cu_path)
    text=next(s for s in obj.sections if s['name']=='.text')
    raw=obj.section_bytes(text)
    decoded=decode(obj_path, analysis_objdump)
    boundaries={i['address']: i for i in decoded}
    dies,_=parse(run([analysis_objdump,'--dwarf=info',obj_path],obj_path.parent/'dwarf.txt'))
    candidates={d['name']:d for d in dies.values() if d['tag']=='DW_TAG_subprogram' and d['low_pc'] is not None and d['high_pc'] is not None}
    entry_targets={d['low_pc'] for d in candidates.values()}
    forbidden=[]
    for d in candidates.values():
        if any(d['low_pc']<=i['address']<d['high_pc'] and i['mnemonic'].startswith('j') and '*' in i['assembly'] for i in decoded):
            forbidden.append((d['low_pc'],d['high_pc']))
    for relocation in obj.relocations:
        symbol=obj.by_index[relocation['symbol_index']]
        if symbol['section']==text['index']:
            section=next(s for s in obj.sections if s['index']==relocation['section'])
            content=obj.section_bytes(section); off=relocation['offset']
            if off+4<=len(content):
                addend=struct.unpack_from('<I',content,off)[0]
                entry_targets.update((addend, symbol['value']+addend))
        if relocation['section']==text['index']:
            entry_targets.update(range(relocation['offset'],relocation['offset']+4))
    zero_projection=zero_clear_projection(raw,decoded,entry_targets,forbidden)
    original_by_name={f['name']:f for f in original}
    def masked_code_equal(d,f):
        """Compare code shape without consulting relocation operands."""
        code=bytearray(raw[d['low_pc']:d['high_pc']])
        reference=bytearray(exe.at_va(f['va'],f['size']))
        if len(code)!=len(reference): return False
        for r in obj.relocations:
            if r['section']!=text['index'] or not d['low_pc']<=r['offset']<d['high_pc']: continue
            p=r['offset']-d['low_pc']
            code[p:p+4]=b'\0'*4
            reference[p:p+4]=b'\0'*4
        return code==reference
    orig_symbols={}
    for s in exe.symbols:
        if s.get('va') is not None:
            orig_symbols.setdefault(s['name'],[]).append(s)
    cu_file=cu_path.replace('\\','/').split('/')[-1]
    section_bases={}
    contribution_evidence={}
    owned=original_contributions(exe,cu_file,cu['low_pc'])
    for section in obj.sections:
        if section['name'] not in ('.data','.rdata','.bss'): continue
        anchors=[s for s in owned if s['name']==section['name'] and s['storage_class']==3 and s['aux_count']]
        candidate=[s for s in obj.symbols if s['name']==section['name'] and s['aux_count'] and s['section']==section['index']]
        if len(anchors)==1 and len(candidate)==1:
            old_size=struct.unpack_from('<I',bytes.fromhex(anchors[0]['aux_hex']))[0]
            new_size=struct.unpack_from('<I',bytes.fromhex(candidate[0]['aux_hex']))[0]
            if old_size==new_size and new_size:
                section_bases.setdefault(section['index'],set()).add(anchors[0]['va'])
                contribution_evidence[section['index']]={'symbol_index':anchors[0]['index'],
                    'file':cu_file,'text_anchor_va':cu['low_pc'],'va':anchors[0]['va'],'logical_size':old_size}
    # Section bases can be inferred from independent named symbol positions,
    # but conflicting evidence is never silently resolved.
    for s in obj.symbols:
        if s['section']<=0 or s['name'].startswith('.'): continue
        matches=orig_symbols.get(s['name'],[])
        own=[x for x in matches if x['file']==cu_file]
        matches=own or matches
        if len({x['va'] for x in matches})==1:
            section_bases.setdefault(s['section'],set()).add(matches[0]['va']-s['value'])
    # A function-scoped static has no stable COFF name: TDM appends a serial
    # number.  Bind it by its DWARF source identity and independently matched
    # owning function, never by the relocation operand being checked.
    original_dies={}
    for line in (ROOT/'evidence/census/dwarf-dies.jsonl').read_text(encoding='utf-8').splitlines():
        d=json.loads(line)
        original_dies[d['offset']]=d
    object_owners=independent_owners(obj,exe,dies,original_dies,cu_path)
    static_evidence=[]
    for d in dies.values():
        if d['tag']!='DW_TAG_variable' or d['address'] is None: continue
        parent=dies.get(d['parent'])
        if parent is None or parent['tag']!='DW_TAG_subprogram': continue
        function=original_by_name.get(parent['name'])
        if function is None or not masked_code_equal(parent,function): continue
        targets=[]
        for old in original_dies.values():
            if old['tag']!='DW_TAG_variable' or old.get('address') is None or old.get('name')!=d['name']: continue
            old_parent=original_dies.get(old.get('parent'))
            if old_parent is None or old_parent.get('tag')!='DW_TAG_subprogram' or old_parent.get('name')!=parent['name']: continue
            if Path(old.get('decl_file_path','')).name==cu_file:
                targets.append(old)
        symbols=[s for s in obj.symbols if s['section']>0 and s['storage_class']==3
                 and s['value']==d['address'] and not s['name'].startswith('.')]
        addresses={old['address'] for old in targets}
        if len(addresses)==1 and len(symbols)==1:
            base=next(iter(addresses))-d['address']
            section_bases.setdefault(symbols[0]['section'],set()).add(base)
            static_evidence.append({'function':parent['name'],'name':d['name'],'candidate_offset':d['address'],
                                    'original_va':next(iter(addresses)),'section':symbols[0]['name'],
                                    'section_base':base})
    sections_by_index={s['index']:s for s in obj.sections}
    def unique_literal_target(sym,addend,instruction):
        """Resolve an anonymous read-only literal from independent data evidence.

        When the field itself occurs more than once, a unique preceding data
        neighbourhood may still establish the table base.  The target is then
        derived from that base plus the field's offset; the relocated operand
        remains unused as evidence.
        """
        sizes={b'\xdd\x05':8,b'\xdc\x0d':8,b'\xd9\x05':4,b'\xd8\x0d':4}
        if sym['name']!='.rdata' or sym['section']<=0:
            return None
        section=sections_by_index.get(sym['section'])
        if section is None: return None
        content=obj.section_bytes(section)
        if addend<0 or addend>=len(content): return None
        size=sizes.get(instruction)
        if size is not None:
            if addend+size>len(content): return None
            literal=content[addend:addend+size]
        else:
            end=content.find(b'\0',addend)
            if end<0 or end-addend>255: return None
            literal=content[addend:end+1]
            if not literal or any((c<32 and c not in (9,10,13)) or c>126 for c in literal[:-1]): return None
        locations=[]
        for original_section in exe.sections:
            if original_section['name']!='.rdata': continue
            haystack=exe.section_bytes(original_section)
            start=0
            while True:
                found=haystack.find(literal,start)
                if found<0: break
                locations.append(exe.image_base+original_section['rva']+found)
                start=found+1
        if len(locations)==1:
            return locations[0]
        # Float tables commonly repeat a scalar.  Require twelve preceding
        # bytes plus the field itself to be unique before deriving its address.
        # This cannot make an altered relocation pass: only candidate .rdata
        # content and the original read-only-data layout establish the target.
        preceding=12
        if addend<preceding:
            return None
        neighbourhood=content[addend-preceding:addend+len(literal)]
        locations=[]
        for original_section in exe.sections:
            if original_section['name']!='.rdata': continue
            haystack=exe.section_bytes(original_section)
            start=0
            while True:
                found=haystack.find(neighbourhood,start)
                if found<0: break
                locations.append(exe.image_base+original_section['rva']+found+preceding)
                start=found+1
        if len(locations)==1:
            return locations[0]
        # A repeated first field can instead be anchored by succeeding table
        # fields.  The candidate data establishes this complete sequence;
        # neither the relocated instruction operand nor comparison bytes do.
        following=4
        if addend+len(literal)+following>len(content):
            return None
        neighbourhood=content[addend:addend+len(literal)+following]
        locations=[]
        for original_section in exe.sections:
            if original_section['name']!='.rdata': continue
            haystack=exe.section_bytes(original_section)
            start=0
            while True:
                found=haystack.find(neighbourhood,start)
                if found<0: break
                locations.append(exe.image_base+original_section['rva']+found)
                start=found+1
        return locations[0] if len(locations)==1 else None
    def target_address(sym,addend):
        if sym['name']=='.text':
            # A section relocation can point into a function even when
            # preceding function sizes differ; preserve that semantic target.
            owners=[d for d in candidates.values() if d['low_pc']<=addend<d['high_pc']]
            if len(owners)==1 and owners[0]['name'] in original_by_name:
                d=owners[0]
                return original_by_name[d['name']]['va']+addend-d['low_pc'],'function-relative .text'
            return None,'unknown .text addend'
        if sym['name'].startswith('.') and sym['section']>0:
            owned=resolve_owner(object_owners,sym['section'],addend)
            if owned is not None: return owned,'independent DWARF/COFF object owner and complete initializer'
            bases=section_bases.get(sym['section'],set())
            if len(bases)==1: return next(iter(bases))+addend,'independent section base (COFF ownership, symbol, or unique content)'
            return None,'section base not independently established'
        matches=orig_symbols.get(sym['name'],[])
        own=[s for s in matches if s['file']==cu_file]
        matches=own or matches
        addresses={s['va'] for s in matches}
        if len(addresses)!=1: return None,'missing or ambiguous symbol'
        # COFF common-symbol value is allocation size, NOT an address/addend.
        adjustment=sym['value'] if sym['section']>0 else 0
        return next(iter(addresses))+addend-adjustment,'named symbol'
    def initializer_target(sym,addend):
        target,reason=target_address(sym,addend)
        if target is None:
            literal=unique_literal_target(sym,addend,b'')
            if literal is not None: return literal,'unique read-only initializer literal or table content'
        return target,reason
    # Start with fully proved leaf objects. Pointer-containing objects can then
    # become owners only after every initializer relocation resolves without
    # consulting the original pointer field or any tested instruction operand.
    for _ in range(len(dies)+1):
        updated=independent_owners(obj,exe,dies,original_dies,cu_path,initializer_target)
        key=lambda o:(tuple(o['scope']),o['name'],o['candidate_offset'],o['original_va'])
        before={key(o) for o in object_owners['accepted']}; after={key(o) for o in updated['accepted']}
        if before-after: raise ValueError('Conflicting independently resolved initializer ownership')
        object_owners=updated
        if after==before: break
    else: raise ValueError('Initializer ownership did not converge')
    data_evidence=[]
    # Anonymous constants/jump tables have no public symbols. Resolve their
    # own relocations first and locate the ENTIRE contribution by unique
    # content. We never derive a target from the field being tested.
    for section in obj.sections:
        if section['name'] not in ('.data','.rdata'): continue
        symbol=next((s for s in obj.symbols if s['name']==section['name'] and s['aux_count']),None)
        size=struct.unpack_from('<I',bytes.fromhex(symbol['aux_hex']))[0] if symbol else section['raw_size']
        if not size: continue
        content=bytearray(obj.section_bytes(section)[:size])
        pending=[]
        for r in obj.relocations:
            if r['section']!=section['index']: continue
            p=r['offset']
            target,reason=target_address(obj.by_index[r['symbol_index']],struct.unpack_from('<I',content,p)[0])
            if target is None or r['type']!=6:
                pending.append(r)
            else: struct.pack_into('<I',content,p,target&0xffffffff)
        locations=[]
        if not pending:
            for original_section in exe.sections:
                if original_section['name']!=section['name']: continue
                haystack=exe.section_bytes(original_section)
                start=0
                while True:
                    pos=haystack.find(content,start)
                    if pos<0: break
                    locations.append(exe.image_base+original_section['rva']+pos)
                    start=pos+1
        if len(locations)==1:
            bases=section_bases.setdefault(section['index'],set())
            # Named evidence and content evidence must agree.
            bases.add(locations[0])
        data_evidence.append({'section':section['name'],'logical_size':size,
                              'unique_content_va':locations[0] if len(locations)==1 else None,
                              'matching_location_count':len(locations),'unresolved_relocations':pending,
                              'section_bases':sorted(section_bases.get(section['index'],set())),
                              'coff_contribution':contribution_evidence.get(section['index']),
                              'content_equal':not pending and len(section_bases.get(section['index'],set()))==1
                                  and next(iter(section_bases[section['index']])) in locations})
    rows=[]
    candidate_by_start={d['low_pc']:d for d in candidates.values()}
    for f in original:
        d=candidates.get(f['name'])
        if d is None:
            rows.append({'name':f['name'],'va':f['va'],'original_size':f['size'],'status':'MISSING'})
            continue
        low,high=d['low_pc'],d['high_pc']
        code=bytearray(raw[low:high])
        reference=exe.at_va(f['va'],f['size'])
        masked,masked_ref=bytearray(code),bytearray(reference)
        relocs=[]
        relocation_offsets=set()
        for r in obj.relocations:
            if r['section']!=text['index'] or not low<=r['offset']<high: continue
            p=r['offset']-low
            relocation_offsets.add(p)
            sym=obj.by_index[r['symbol_index']]
            addend=struct.unpack_from('<I',code,p)[0]
            target,reason=target_address(sym,addend)
            literal=unique_literal_target(sym,addend,bytes(code[max(0,p-2):p]))
            if target is None and literal is not None:
                target,reason=literal,'unique read-only literal or table content'
            expected=None
            if r['type']==6 and target is not None: expected=target&0xffffffff
            elif r['type']==20 and target is not None: expected=(target-f['va']-p-4)&0xffffffff
            actual=struct.unpack_from('<I',reference,p)[0] if p+4<=len(reference) else None
            if expected is not None: struct.pack_into('<I',code,p,expected)
            masked[p:p+4]=b'\0'*4
            if p+4<=len(masked_ref): masked_ref[p:p+4]=b'\0'*4
            relocs.append({**r,'function_offset':p,'addend':addend,'target_va':target,'resolution':reason,
                           'resolved_value':expected,'original_value':actual,'equal':expected is not None and expected==actual})
        # Every decoded relative edge to a CU function entry is independently
        # resolved, including rel8 JMP/Jcc. Internal basic-block edges remain raw.
        direct_transfers=resolve_transfers(code,reference,low,high,f['va'],list(boundaries.values()),list(candidates.values()),original,relocs)
        body_masked=bytearray(code)
        body_reference=bytearray(reference)
        for r in relocs:
            p=r['function_offset']
            body_masked[p:p+4]=b'\0'*4
            if p+4<=len(body_reference): body_reference[p:p+4]=b'\0'*4
        body_shape_equal=body_masked==body_reference
        masked_equal=masked==masked_ref
        function_instructions=[i for i in decoded if low<=i['address']<high]
        boundaries_verified=complete_stream(function_instructions,low,high-low)==raw[low:high]
        exact=boundaries_verified and code==reference and all(r['equal'] for r in relocs) and all(t['equal'] for t in direct_transfers)
        differences=[i for i,(x,y) in enumerate(zip(code,reference)) if x!=y]
        first=differences[0] if differences else min(len(code),len(reference)) if len(code)!=len(reference) else None
        rows.append({'name':f['name'],'va':f['va'],'original_size':f['size'],'candidate_offset':low,'candidate_size':high-low,
                     'relative_layout_equal':low==f['va']-cu['low_pc'], 'masked_equal':masked_equal, 'body_shape_equal':body_shape_equal,
                     'relocation_resolved_equal':exact,'relocations':relocs,'direct_transfers':direct_transfers,
                     'difference_offsets':differences, 'instruction_boundaries_verified':boundaries_verified,
                     'instructions':function_instructions,
                     'first_difference':None if first is None else {'offset':first,'original_va':f['va']+first,
                         'candidate_byte':code[first] if first<len(code) else None,'original_byte':reference[first] if first<len(reference) else None},
                     'status':'FUNCTION_MATCH' if exact else 'CODEGEN_SIMILAR' if masked_equal else 'DIFFER'})
        rows[-1]['tail_jump_layout']=None
        if abs((high-low)-f['size'])==3:
            old_instructions=decode(exe_path,analysis_objdump,f['va'],f['va']+f['size'])
            rows[-1]['tail_jump_layout']=tail_layout(rows[-1],old_instructions,list(candidates.values()),original,reference=reference)
    extras=sorted(set(candidates)-set(original_by_name))
    layout=all(r.get('relative_layout_equal',False) for r in rows) and not extras
    resolved=bytearray(raw)
    unresolved=[]
    for r in obj.relocations:
        if r['section']!=text['index']: continue
        p=r['offset']
        sym=obj.by_index[r['symbol_index']]
        target,reason=target_address(sym,struct.unpack_from('<I',raw,p)[0])
        if target is None or r['type'] not in (6,20): unresolved.append({**r,'reason':reason}); continue
        value=target if r['type']==6 else target-cu['low_pc']-p-4
        struct.pack_into('<I',resolved,p,value&0xffffffff)
    span=cu['high_pc']-cu['low_pc']
    # Auxiliary section length excludes file-level COFF padding.
    sectionsym=next(s for s in obj.symbols if s['name']=='.text' and s['aux_count'])
    logical_size=struct.unpack_from('<I',bytes.fromhex(sectionsym['aux_hex']))[0]
    whole=layout and logical_size==span and not unresolved and resolved[:span]==exe.at_va(cu['low_pc'],span)
    return {'historical_cu':cu_path,'original_cu_span':span,'candidate_text_logical_size':logical_size,
            'candidate_text_raw_size':len(raw),'candidate_zero_clear_projection':zero_projection,'functions':rows,'extra_functions':extras,
            'functions_total':len(original),'function_matches':sum(r['status']=='FUNCTION_MATCH' for r in rows),
            'masked_matches':sum(r.get('masked_equal',False) for r in rows),
            'whole_text_contribution_equal':whole,'relative_layout_equal':layout,'unresolved_text_relocations':unresolved,
            'object_sections':obj.sections,'object_symbols':obj.symbols,'object_relocations':obj.relocations,
            'common_allocations':[s for s in obj.symbols if s['section']==0 and s['value']>0],
            'initialized_data_comparison':data_evidence,
            'static_data_evidence':static_evidence,'object_ownership':object_owners,
            'original_defined_globals':[g for g in read_json(ROOT/'evidence/census/globals.json') if g['cu']==cu_path and g['address'] is not None],
            'object_match':False,'cu_match':False,
            'limits':['Original .o files unavailable; original relocation records cannot be compared directly.',
                      'All code functions checked; data/BSS symbols and relocations inventoried, full data and DWARF equality not established.',
                      'Relocation resolution is verification at observed VAs, never input to normal compilation or structural link.']}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('targets',nargs='+',choices=list(TARGETS))
    ap.add_argument('--matrix',action='store_true')
    ap.add_argument('--compiler',choices=list(COMPILERS),default='tdm-1')
    ap.add_argument('--objdump',type=Path,default=Path('C:/msys64/mingw64/bin/objdump.exe'))
    a=ap.parse_args()
    verify_inputs(a.compiler)
    base=ROOT/'build/experiments'
    if a.compiler!='tdm-1': base=base/a.compiler
    exe=ROOT/'assets/icytower15.exe'
    if identity(exe)!=read_json(ROOT/'evidence/fixture-lock.json'): raise ValueError('Wrong verification fixture')
    summary=[]
    for target in a.targets:
        options=['-O0','-O1','-O2','-O3','-Os'] if a.matrix else [TARGETS[target]['default']]
        for opt in options:
            directory=base/target/opt[1:]
            directory.mkdir(parents=True,exist_ok=True)
            report_path=directory/'comparison.json'
            report_path.unlink(missing_ok=True)
            obj,build=compile_target(target,[opt],directory,compiler=a.compiler)
            result=compare(obj,TARGETS[target]['historical_cu'],exe,a.objdump)
            result.update(build=build,fixture=identity(exe),analysis_tool=identity(a.objdump))
            write_json(report_path,result)
            row={'target':target,'opt':opt,'total':result['functions_total'],'function_matches':result['function_matches'],
                 'masked_matches':result['masked_matches'],'whole_text_equal':result['whole_text_contribution_equal'],
                 'report':report_path.relative_to(ROOT).as_posix()}
            summary.append(row)
            print(row)
    write_json(base/'summary.json',summary)

if __name__=='__main__': main()
