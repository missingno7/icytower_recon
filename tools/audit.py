"""Check saved provenance and inventory consistency without re-running experiments."""
from collections import Counter
from common import ROOT, identity, read_json
from build import verify_inputs

def main():
    verify_inputs()
    verify_inputs('tdm-2')
    lock=read_json(ROOT/'evidence/census-lock.json')
    assert identity(ROOT/'assets/icytower15.exe')==lock['fixture']
    for name,expected in lock['outputs'].items():
        assert identity(ROOT/'evidence/census'/name)==expected, name
    for row in read_json(ROOT/'evidence/research-lock.json')['files']:
        assert identity(ROOT/row['snapshot'])=={k:row[k] for k in ['size','sha256']},row['snapshot']
    units=read_json(ROOT/'src/units.json')
    assert len(units)==25
    assert Counter(u['classification'] for u in units)=={'GAME':18,'VENDORED_UPSTREAM':5,'AMBIGUOUS':2}
    assert sorted(p.name for p in (ROOT/'src').glob('*.c'))==sorted(u['source'].split('/')[-1] for u in units)
    for name in ['loadpng.c','savepng.c','regpng.c']:
        assert identity(ROOT/'src'/name)==identity(ROOT/'third_party/allegro-4.4.1/addons/loadpng'/name)
    pe=read_json(ROOT/'evidence/census/pe.json')
    assert len(pe['sections'])==15
    assert pe['optional_header']['image_base']==0x400000
    assert not any(d['present'] for d in pe['directories'] if d['name'] in ['base_relocation','tls','export','load_config','debug'])
    fresh={(d['dll'].lower(),e['name'],e['iat_va']) for d in pe['imports'] for e in d['entries']}
    inherited={(dll.lower(),name,int(va,16)) for dll,name,va in read_json(ROOT/'evidence/research/imports.json')}
    assert fresh==inherited
    assert sum(len(d['entries']) for d in pe['imports'])==320
    assert len(pe['resources']['leaves'])==2
    assert len(read_json(ROOT/'evidence/census/compilation-units.json'))==148
    print('PASS: fixture, census, research snapshots, build-input locks, 25-CU ownership, upstream copies, PE invariants.')

if __name__=='__main__': main()
