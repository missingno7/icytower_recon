import json,struct,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools'))
from binary import Binary
D=ROOT/'docs/attempts/research-20260924-fldads-threadmain'
p=D/'rdata-owner-analysis.json'; out=json.loads(p.read_text())
exe=Binary(ROOT/'assets/icytower15.exe'); section=next(s for s in exe.sections if s['name']=='.rdata')
base=0x4d42f0; w=exe.at_va(base,0x1a4)
needles=[b'ads.csv\0',b'Cached ads are up to date\0',b'Downloading ad listing\0',b'http://www.icytower.com/icytower_pc.csv\0',b'Could not fetch ad listing from http://www.icytower.com/icytower_pc.csv (%d), skipping ad update\0',b'There are %d available ad spots.\0',bytes.fromhex('00feff46')]
out['original_pe_window']={'start_va':hex(base),'length':len(w),'end_va':hex(base+len(w)),'sha256':hashlib.sha256(w).hexdigest(),'matches_baseline_object_bytes':False,'limit':'Direct byte-order observation only; does not prove the original fld_adspot.o .rdata contribution boundary.'}
out['original_pe_window']['content_offsets']=[{'content':n[:-1].decode('ascii','replace') if n.endswith(b'\0') else n.hex(),'relative_offset':hex(w.find(n)),'occurrence_count_in_window':w.count(n)} for n in needles]
out['historical_source_order_evidence']={'fldads_update_local_adimg':80,'fldads_load_cache_from_csv':114,'state':'Historical source order places update-local before CSV loader. The full definition move preserves both bodies.'}
out['attribution']={'reordered_literals':['Local file %s is newer (%d) than server (%d), using local','Downloading %s -> %s','Warning: local file missing for %s, ad will not be shown'],'baseline_offsets':{'warning':'0x18','local_file':'0x54','downloading_pair':'0x8e','target_download':'0xbf','cached':'0x185','float':'0x1a0'},'moved_offsets':{'local_file':'0x18','downloading_pair':'0x52','warning':'0x68','target_download':'0xbd','cached':'0x181','float':'0x19c'},'interpretation':'Swapping the two unchanged function definitions changes string first-emission order and padding/alignment in GCC .rdata; total section length falls by 4 bytes. The current output strings/content are all retained. This is not evidence for a missing four-byte variable or literal.'}
p.write_text(json.dumps(out,indent=2))
