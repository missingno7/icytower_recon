"""Compare entire compiled CUs, with function extents taken from DWARF.

Masked equality alone is CODEGEN_SIMILAR. FUNCTION_MATCH requires matching
length plus every byte after independently resolving each relocation symbol.
No original bytes are used by compilation, only by this verifier.
"""
import argparse
import struct
from pathlib import Path
from common import ROOT, identity, read_json, run, write_json
from binary import Binary
from dwarf import parse
from build import TARGETS, COMPILERS, verify_inputs, compile_target

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
    dies,_=parse(run([analysis_objdump,'--dwarf=info',obj_path],obj_path.parent/'dwarf.txt'))
    candidates={d['name']:d for d in dies.values() if d['tag']=='DW_TAG_subprogram' and d['low_pc'] is not None and d['high_pc'] is not None}
    original_by_name={f['name']:f for f in original}
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
    sections_by_index={s['index']:s for s in obj.sections}
    def unique_literal_target(sym,addend,instruction):
        """Resolve an anonymous read-only literal by unique content, not its field."""
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
        for r in obj.relocations:
            if r['section']!=text['index'] or not low<=r['offset']<high: continue
            p=r['offset']-low
            sym=obj.by_index[r['symbol_index']]
            addend=struct.unpack_from('<I',code,p)[0]
            target,reason=target_address(sym,addend)
            literal=unique_literal_target(sym,addend,bytes(code[max(0,p-2):p]))
            if target is None and literal is not None:
                target,reason=literal,'unique read-only literal content'
            expected=None
            if r['type']==6 and target is not None: expected=target&0xffffffff
            elif r['type']==20 and target is not None: expected=(target-f['va']-p-4)&0xffffffff
            actual=struct.unpack_from('<I',reference,p)[0] if p+4<=len(reference) else None
            if expected is not None: struct.pack_into('<I',code,p,expected)
            masked[p:p+4]=b'\0'*4
            if p+4<=len(masked_ref): masked_ref[p:p+4]=b'\0'*4
            relocs.append({**r,'function_offset':p,'addend':addend,'target_va':target,'resolution':reason,
                           'resolved_value':expected,'original_value':actual,'equal':expected is not None and expected==actual})
        masked_equal=masked==masked_ref
        exact=code==reference and all(r['equal'] for r in relocs)
        differences=[i for i,(x,y) in enumerate(zip(code,reference)) if x!=y]
        first=differences[0] if differences else min(len(code),len(reference)) if len(code)!=len(reference) else None
        rows.append({'name':f['name'],'va':f['va'],'original_size':f['size'],'candidate_offset':low,'candidate_size':high-low,
                     'relative_layout_equal':low==f['va']-cu['low_pc'], 'masked_equal':masked_equal,
                     'relocation_resolved_equal':exact,'relocations':relocs,
                     'first_difference':None if first is None else {'offset':first,'original_va':f['va']+first,
                         'candidate_byte':code[first] if first<len(code) else None,'original_byte':reference[first] if first<len(reference) else None},
                     'status':'FUNCTION_MATCH' if exact else 'CODEGEN_SIMILAR' if masked_equal else 'DIFFER'})
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
            'candidate_text_raw_size':len(raw),'functions':rows,'extra_functions':extras,
            'functions_total':len(original),'function_matches':sum(r['status']=='FUNCTION_MATCH' for r in rows),
            'masked_matches':sum(r.get('masked_equal',False) for r in rows),
            'whole_text_contribution_equal':whole,'relative_layout_equal':layout,'unresolved_text_relocations':unresolved,
            'object_sections':obj.sections,'object_symbols':obj.symbols,'object_relocations':obj.relocations,
            'common_allocations':[s for s in obj.symbols if s['section']==0 and s['value']>0],
            'initialized_data_comparison':data_evidence,
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
