"""Measure natural game layout in an independently linked synthetic PE."""
from common import ROOT, identity, read_json, write_json
from binary import Binary

def main():
    directory=ROOT/'build/integration/tdm-2'
    build=read_json(directory/'build.json')
    candidate=Binary(directory/'integration-probe.exe')
    if identity(candidate.path)!=build['executable']: raise ValueError('Stale integration PE')
    fixture=identity(ROOT/'assets/icytower15.exe')
    if fixture!=read_json(ROOT/'evidence/fixture-lock.json'): raise ValueError('Wrong fixture')
    actual={s['name']:s['va'] for s in candidate.symbols if s.get('va') and s['type']&0x20}
    rows=[]
    ownership={u['historical_path']:u['classification'] for u in read_json(ROOT/'src/units.json')}
    for obj in build['game_objects']:
        report=read_json(ROOT/'build/experiments/tdm-2'/obj['target']/'O2/comparison.json')
        if obj['object']!=report['build']['object']:
            # Debug filenames may depend on the output path. Check text extents
            # against the actual linked object's DWARF through the same verifier.
            from experiment import compare
            from pathlib import Path
            report=compare(directory/obj['target']/'unit.o',obj['historical_cu'],
                           ROOT/'assets/icytower15.exe',Path('C:/msys64/mingw64/bin/objdump.exe'))
        for f in report['functions']:
            linked=actual.get('_'+f['name'])
            rows.append({'name':f['name'],'original_va':f['va'],'linked_va':linked,
                         'classification':ownership[obj['historical_cu']],
                         'original_body_size':f['original_size'],'candidate_body_size':f.get('candidate_size'),
                         'address_equal':linked==f['va'],
                         'body_size_equal':f.get('candidate_size')==f['original_size'],
                         'object_function_status':f['status']})
    rows.sort(key=lambda x:x['original_va'])
    start=rows[0]['original_va']
    end=start
    for row in rows:
        if not row['address_equal'] or not row['body_size_equal']: break
        end=row['original_va']+row['original_body_size']
    result={'scope':'Synthetic integration PE; address/extent equality is not linked byte equality',
            'fixture':fixture,'build_report':identity(directory/'build.json'),
            'functions':rows,'natural_game_address_extent_prefix_bytes':end-start,
            'first_layout_mismatch':next((r for r in rows if not r['address_equal'] or not r['body_size_equal']),None)}
    write_json(ROOT/'docs/experiments/integration-layout.json',result)
    print(result['first_layout_mismatch'])

if __name__=='__main__': main()
