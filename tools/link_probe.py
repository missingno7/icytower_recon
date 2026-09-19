"""Link a real PE with historical startup/library extraction and inspect order.

No forced function placement, copied code, undefined-symbol suppression or
fallback dispatch. A synthetic main makes this an honest CRT link probe,
not a playable/reconstructed icytower15.exe.
"""
from common import ROOT, TC, identity, read_json, run, write_json
from binary import Binary
from build import verify_inputs, COMPILERS
import argparse

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiler',choices=list(COMPILERS),default='tdm-1')
    a=ap.parse_args()
    tc=COMPILERS[a.compiler]
    verify_inputs(a.compiler)
    out=ROOT/'build/link-probe'
    if a.compiler!='tdm-1': out=out/a.compiler
    out.mkdir(parents=True,exist_ok=True)
    exe=out/'crt-probe.exe'
    exe.unlink(missing_ok=True)
    (out/'report.json').unlink(missing_ok=True)
    command=[tc/'bin/gcc.exe','-O2','-g','-mfpmath=387','-mwindows','tools/link_probe.c',
             '-Wl,-Map,'+str(out/'link.map'),'-Wl,--cref','-o',exe]
    run(command,toolchain=tc)
    run([tc/'bin/objdump.exe','-x',exe],out/'pe.txt',toolchain=tc)
    generated=Binary(exe)
    original=Binary(ROOT/'assets/icytower15.exe')
    if identity(original.path)!=read_json(ROOT/'evidence/fixture-lock.json'): raise ValueError('Fixture differs')
    actual={s['name']:s['va'] for s in generated.symbols if s.get('va') and s['type']&0x20}
    linked_starts=sorted(set(actual.values()))
    functions=read_json(ROOT/'evidence/census/functions.json')
    rows=[]
    for f in functions:
        if f['va']>=0x401318: break  # Evidence boundary: first game CU, not a placement instruction.
        names=f['coff_symbols'] or [f['name']]
        candidates=[(n,actual[n]) for n in names if n in actual]
        va=candidates[0][1] if len(candidates)==1 else None
        next_start=next((x for x in linked_starts if va is not None and x>va),None)
        actual_span=next_start-va if next_start is not None else None
        rows.append({'name':f['name'],'original_va':f['va'],'size':f['size'],'linked_va':va,
                     'linked_symbol_span':actual_span,'address_equal':va==f['va'],'span_equal':actual_span==f['size']})
    prefix=0
    start=original.image_base+original.sections[0]['rva']
    end=start
    for r in rows:
        if not r['address_equal'] or not r['span_equal'] or r['original_va']!=end: break
        end+=r['size']
        prefix=end-start
    left=original.section_bytes(original.sections[0])
    right=generated.section_bytes(generated.sections[0])
    byte_prefix=next((i for i,(x,y) in enumerate(zip(left,right)) if x!=y),min(len(left),len(right)))
    report={'scope':'Synthetic-main CRT probe; not the reconstructed game','compiler':a.compiler,'command':[str(x) for x in command],
            'output':identity(exe),'fixture':identity(original.path),'source':identity(ROOT/'tools/link_probe.c'),
            'toolchain_lock':identity(ROOT/'toolchain/lock.json'),
            'startup_functions':rows,'natural_startup_address_prefix_bytes':prefix,
            'strict_text_byte_prefix':byte_prefix,'first_byte_difference':{'va':start+byte_prefix,'original':left[byte_prefix],'candidate':right[byte_prefix]},
            'sections':generated.sections,'imports':generated.imports(),
            'entry_rva':generated.optional['entry_rva'],
            'game_link_milestone':False,
            'limitations':['Synthetic main replaces the absent game solely for this probe.',
                           'No game reconstruction coverage is credited for startup addresses.',
                           'Imports and target addresses differ because most game/libraries are absent.']}
    if a.compiler!='tdm-1': report['candidate_toolchain_lock']=identity(ROOT/'toolchain'/f'{a.compiler}-lock.json')
    write_json(out/'report.json',report)
    print({k:report[k] for k in ['natural_startup_address_prefix_bytes','strict_text_byte_prefix','entry_rva','game_link_milestone']})

if __name__=='__main__': main()
