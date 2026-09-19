"""Regenerate immutable binary facts and the historical CU skeleton.

Source bodies are never overwritten. Exported research is labeled inherited;
fresh PE/COFF/DWARF facts name their input hash and analyzing tool.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from common import ROOT, identity, read_json, run, write_json
from binary import Binary
from dwarf import parse, line_rows, file_tables, address_lists, integer

GAME_ROOT = 'F:\\projects\\icytower\\trunk\\source\\'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--exe',type=Path,default=ROOT/'assets/icytower15.exe')
    ap.add_argument('--objdump',type=Path,default=Path('C:/msys64/mingw64/bin/objdump.exe'))
    ap.add_argument('--reuse-dumps',action='store_true',help='Reparse previously hash-verified dumps of this exact fixture with this exact analysis tool')
    a=ap.parse_args()
    out=ROOT/'evidence/census'
    out.mkdir(parents=True,exist_ok=True)
    fixture=identity(a.exe)
    lock_path=ROOT/'evidence/fixture-lock.json'
    if lock_path.exists() and read_json(lock_path)!=fixture:
        raise ValueError('Original EXE identity changed; census refused')
    write_json(lock_path,fixture)
    binary=Binary(a.exe)
    pe=binary.census()
    write_json(out/'pe.json',pe)
    write_json(out/'imports.json',pe['imports'])
    write_json(out/'resources.json',pe['resources'])
    write_json(out/'coff-files.json',pe['coff_files'])
    raw=ROOT/'build/census'
    raw.mkdir(parents=True,exist_ok=True)
    if a.reuse_dumps:
        previous=read_json(out/'provenance.json')
        assert previous['fixture']==fixture
        assert previous['analysis_tool']['sha256']==identity(a.objdump)['sha256']
        for filename,expected in previous['raw_dumps'].items():
            if identity(raw/filename)!=expected: raise ValueError('Raw dump hash changed: '+filename)
    def dump(option,filename):
        path=raw/filename
        if a.reuse_dumps: return path.read_text(encoding='utf-8')
        return run([a.objdump,'--dwarf='+option,a.exe],path)
    text=dump('info','dwarf-info.txt')
    dies,summary=parse(text)
    lines=dump('decodedline','dwarf-lines.txt')
    rawline=dump('rawline','dwarf-rawline.txt')
    dump('loc','dwarf-locations.txt')
    dump('Ranges','dwarf-ranges.txt')
    tables=file_tables(rawline)
    table_index={t['offset']:t for t in tables}
    for d in dies.values():
        stmt=integer(dies[d['cu']]['attrs'].get('DW_AT_stmt_list'))
        fileno=integer(d['resolved'].get('DW_AT_decl_file'))
        d['decl_file_path']=table_index.get(stmt,{}).get('files',{}).get(fileno,{}).get('path')
    write_json(out/'source-files.json',tables)
    write_json(out/'location-lists.json',address_lists(binary,'.debug_loc'))
    write_json(out/'range-lists.json',address_lists(binary,'.debug_ranges'))
    # Compact JSONL keeps the entire typed graph independently accessible.
    with (out/'dwarf-dies.jsonl').open('w',encoding='utf-8',newline='\n') as f:
        for d in dies.values(): f.write(json.dumps(d,separators=(',',':'))+'\n')
    write_json(out/'line-mappings.json',line_rows(lines))
    cus=[]
    for d in dies.values():
        if d['tag']=='DW_TAG_compile_unit':
            cus.append({'die':d['offset'],'path':d['name'],'producer':d['resolved'].get('DW_AT_producer'),
                        'low_pc':d['low_pc'],'high_pc':d['high_pc'],'attrs':d['attrs']})
    write_json(out/'compilation-units.json',cus)
    summary['producers']=dict(Counter(c['producer'] for c in cus))
    summary['cu_count']=len(cus)
    summary['line_rows']=len(line_rows(lines))
    write_json(out/'dwarf-summary.json',summary)
    inherited=read_json(ROOT/'evidence/research/artifacts/functions.json')
    by_va={d['low_pc']:d for d in dies.values() if d['tag']=='DW_TAG_subprogram' and d['low_pc'] is not None}
    functions=[]
    for old in inherited:
        f=dict(old)
        f['va']=int(f['va'],16)
        f['extent_evidence']='inherited research: COFF next-symbol span (may include padding)' if f['source']=='coff' else 'DWARF high_pc-low_pc'
        if f['va'] in by_va:
            d=by_va[f['va']]
            f.update(name=d['name'],die=d['offset'],type_ref=d['type_ref'],decl_file_path=d['decl_file_path'],parameters=[x for x in d['children'] if dies[x]['tag']=='DW_TAG_formal_parameter'])
            if d['high_pc'] is not None:
                f['size']=d['high_pc']-d['low_pc']
            f['compile_unit']=dies[d['cu']]['name']
        f['coff_symbols']=[s['name'] for s in binary.symbols if s.get('va')==f['va'] and s['type']&0x20]
        f['sha256']=__import__('hashlib').sha256(binary.at_va(f['va'],f['size'])).hexdigest()
        functions.append(f)
    write_json(out/'functions.json',functions)
    globals_=[{'die':d['offset'],'name':d['name'],'type_ref':d['type_ref'],'cu':dies[d['cu']]['name'],
               'address':d['address'],'scope':d['parent'],'decl_file_path':d['decl_file_path'],'attrs':d['resolved']}
              for d in dies.values() if d['tag']=='DW_TAG_variable' and d['depth']==1]
    write_json(out/'globals.json',globals_)
    types=[{'die':d['offset'],'kind':d['tag'],'name':d['name'],'cu':d['cu'],'type_ref':d['type_ref'],
            'children':d['children'],'decl_file_path':d['decl_file_path'],'attrs':d['resolved']} for d in dies.values()
           if d['tag'].endswith('_type') or d['tag']=='DW_TAG_typedef']
    write_json(out/'types.json',types)
    boundary=read_json(ROOT/'evidence/research/artifacts/lib_boundary.json')
    write_json(out/'ownership.json',{'status':'INHERITED_RESEARCH', 'source':'evidence/research/artifacts/lib_boundary.json',
        'denominator':'sum of attributed function spans, NOT PE .text virtual size',
        'families':boundary['ownership'],
        'corrections':['csv.c/httpget.c remain recovery-owned pending provenance', 'logg.c has a local extension; upstream body is not the full historical CU',
                       'strptime.c/timecompat.c family identified, exact source revision unresolved'],
        'modified_vendor_cus':[{'path':'C:\\Lib\\allegro4\\addons\\logg\\logg.c','classification':'VENDORED_MODIFIED','missing':'memory-reader extension (7 functions, inherited estimate 667 bytes)'}]})
    units=[]
    for cu in cus:
        if not cu['path'].startswith(GAME_ROOT): continue
        basename=cu['path'].split('\\')[-1]
        upstream=basename in ['loadpng.c','savepng.c','regpng.c']
        compat=basename in ['strptime.c','timecompat.c']
        ambiguous=basename in ['csv.c','httpget.c']
        classification='VENDORED_UPSTREAM' if upstream or compat else 'AMBIGUOUS' if ambiguous else 'GAME'
        fns=[dict(f,state='KNOWN_UPSTREAM' if upstream else 'UNKNOWN') for f in functions if f['compile_unit']==cu['path']]
        unit={'source':'src/'+basename,'historical_path':cu['path'],'classification':classification,
              'provenance_status':'exact upstream release available' if upstream else 'upstream family only; exact revision unresolved' if compat else 'DWARF topology',
              'cu_die':cu['die'],'low_pc':cu['low_pc'],'high_pc':cu['high_pc'],'functions':fns,
              'globals':[g for g in globals_ if g['cu']==cu['path']]}
        units.append(unit)
        source=ROOT/'src'/basename
        if not source.exists():
            listing='\n'.join(f' * UNKNOWN: {f["name"]} @ 0x{f["va"]:08x}, {f["size"]} bytes' for f in fns)
            source.write_text(f'/* Historical CU: {cu["path"]}\n * Ownership: {classification}\n * Source recovery pending. This file intentionally defines no fallback code.\n{listing}\n */\n',encoding='utf-8')
    assert len(units)==25, f'Expected 25 historical game-tree CUs, saw {len(units)}'
    write_json(ROOT/'src/units.json',units)
    write_json(out/'provenance.json',{'fixture':fixture,'analysis_tool':{'path':str(a.objdump),**identity(a.objdump),
               'version':run([a.objdump,'--version']).splitlines()[0]},
               'raw_dumps':{p.name:identity(p) for p in sorted(raw.glob('*.txt'))},
               'generator_sources':{str(p.relative_to(ROOT)).replace('\\','/'):identity(p) for p in [ROOT/'tools/census.py',ROOT/'tools/binary.py',ROOT/'tools/dwarf.py',ROOT/'tools/common.py']},
               'fresh':['PE headers','sections','imports','resources','COFF symbols/files','DWARF DIE graph','line mappings'],
               'inherited':['COFF-only function extents','library ownership and compatibility','compiler flag hypotheses'],
               'raw_attributes':'Every DIE, child, type reference, origin/specification, location expression and range reference is retained in dwarf-dies.jsonl. Location/range list bodies and source file tables are separate canonical JSON documents; original DWARF remains in the fixture.'})
    write_json(ROOT/'evidence/census-lock.json',{'fixture':fixture,'outputs':{p.name:identity(p) for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps({'cu_count':len(cus),'game_tree_cus':len(units),'functions':len(functions),**summary},indent=2))

if __name__=='__main__': main()
