"""Verify archived COFF startup contributions; no executable bytes generated."""
import struct
from common import ROOT, identity, read_json, write_json
from binary import Binary
from build import COMPILERS, verify_inputs

def compare_object(path,original):
    obj=Binary(path)
    names={}
    for symbol in original.symbols:
        if symbol.get('va') is not None or symbol['section']==-1:
            names.setdefault(symbol['name'],set()).add(symbol.get('va',symbol['value']))
    bases={}
    evidence=[]
    for symbol in obj.symbols:
        hits=names.get(symbol['name'],set())
        if symbol['section']>0 and not symbol['name'].startswith('.') and len(hits)==1:
            bases.setdefault(symbol['section'],set()).add(next(iter(hits))-symbol['value'])
    for section in obj.sections:
        if section['name']!='.rdata' or section['relocation_count']: continue
        symbol=next((s for s in obj.symbols if s['name']=='.rdata' and s['aux_count']),None)
        length=struct.unpack_from('<I',bytes.fromhex(symbol['aux_hex']))[0] if symbol else section['raw_size']
        if not length: continue
        content=obj.section_bytes(section)[:length]
        hits=[]
        for target in original.sections:
            if target['name']!='.rdata': continue
            data=original.section_bytes(target)
            offset=data.find(content)
            while offset>=0:
                hits.append(original.image_base+target['rva']+offset)
                offset=data.find(content,offset+1)
        if len(hits)==1:
            bases.setdefault(section['index'],set()).add(hits[0])
        evidence.append({'section':section['name'],'length':length,'content_match_locations':hits})
    def resolve(sym):
        if sym['storage_class']==105:
            # COFF weak extern: auxiliary tag index points to the fallback.
            fallback=struct.unpack_from('<I',bytes.fromhex(sym['aux_hex']))[0]
            return resolve(obj.by_index[fallback])
        if sym['section']==-1:
            hits=names.get(sym['name'],set())
            return sym['value'] if hits=={sym['value']} else None
        if sym['name'].startswith('.') and sym['section']>0:
            hits=bases.get(sym['section'],set())
            return next(iter(hits)) if len(hits)==1 else None
        hits=names.get(sym['name'],set())
        return next(iter(hits))-(sym['value'] if sym['section']>0 else 0) if len(hits)==1 else None
    section=next(s for s in obj.sections if s['name']=='.text')
    hits=bases.get(section['index'],set())
    if len(hits)!=1: raise ValueError('Text placement not established by all named symbols')
    base=next(iter(hits))
    code=bytearray(obj.section_bytes(section))
    reference=original.at_va(base,len(code))
    relocations=[]
    for r in obj.relocations:
        if r['section']!=section['index']: continue
        p=r['offset']
        sym=obj.by_index[r['symbol_index']]
        target=resolve(sym)
        value=None
        if target is not None and r['type'] in (6,20):
            value=(target+struct.unpack_from('<I',code,p)[0]-(base+p+4 if r['type']==20 else 0))&0xffffffff
            struct.pack_into('<I',code,p,value)
        expected=struct.unpack_from('<I',reference,p)[0]
        relocations.append({**r,'resolved_value':value,'original_value':expected,'equal':value is not None and value==expected})
    mismatch=next((i for i,(x,y) in enumerate(zip(code,reference)) if x!=y),None)
    return {'object':str(path.relative_to(ROOT)), 'identity':identity(path),'text_base_inferred_from_symbols':base,
            'text_size_including_object_padding':len(code),'relocations':relocations,'data_evidence':evidence,
            'whole_text_equal':code==reference and all(r['equal'] for r in relocations),
            'first_mismatch':None if mismatch is None else {'offset':mismatch,'va':base+mismatch,'candidate':code[mismatch],'original':reference[mismatch]},
            'object_match':False,'limits':'Text contribution including padding compared; full debug/data/symbol-record equality not asserted.'}

def main():
    if identity(ROOT/'assets/icytower15.exe')!=read_json(ROOT/'evidence/fixture-lock.json'):
        raise ValueError('Wrong verification fixture')
    original=Binary(ROOT/'assets/icytower15.exe')
    reports=[]
    for compiler,tc in COMPILERS.items():
        verify_inputs(compiler)
        for relative in ['lib/crt2.o','lib/gcc/mingw32/4.4.1/crtbegin.o']:
            try:
                report=compare_object(tc/relative,original)
            except ValueError as error:
                report={'object':str((tc/relative).relative_to(ROOT)),'whole_text_equal':False,'placement_conflict':str(error),'identity':identity(tc/relative)}
            report['compiler']=compiler
            reports.append(report)
            print(compiler,relative,report['whole_text_equal'],report.get('first_mismatch',report.get('placement_conflict')))
    write_json(ROOT/'docs/experiments/runtime-objects.json',{'fixture':identity(original.path),'objects':reports})

if __name__=='__main__': main()
