import json,struct,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools'))
from binary import Binary
from compiler_context import resolved_candidate
base_obj=ROOT/'build/tu-context/game-fld-adspot/fldads-threadmain-20260924-base-control/unit.o'
target_obj=ROOT/'build/tu-context/game-fld-adspot/fldads-threadmain-20260924-update-local-random-after-threadmain/unit.o'

def section_bytes(path,name):
 b=Path(path).read_bytes(); n=struct.unpack_from('<H',b,2)[0]; opt=struct.unpack_from('<H',b,16)[0]; p=20+opt
 for i in range(n):
  h=b[p+40*i:p+40*(i+1)]; nm=h[:8].split(b'\0')[0].decode()
  if nm==name:
   size,ptr=struct.unpack_from('<II',h,16); return b[ptr:ptr+size]
 raise KeyError(name)

def strings(b):
 out=[]; i=0
 while i<len(b):
  j=b.find(b'\0',i); j=len(b) if j<0 else j; x=b[i:j]
  if x and all(32<=c<127 or c in (9,10,13) for c in x): out.append({'offset':i,'text':x.decode('ascii','replace')})
  i=j+1
 return out
b0=section_bytes(base_obj,'.rdata'); b1=section_bytes(target_obj,'.rdata')
exe=Binary(ROOT/'assets/icytower15.exe'); sec=next(s for s in exe.sections if s['name']=='.rdata'); raw=exe.at_va(exe.image_base+sec['rva'],sec['raw_size'])
needle=bytes.fromhex('00feff46'); occ=[]; i=0
while True:
 i=raw.find(needle,i)
 if i<0: break
 occ.append({'rva':hex(sec['rva']+i),'va':hex(exe.image_base+sec['rva']+i),'offset':i}); i+=1
reports={}
for label,rel in [('baseline','docs/attempts/research-20260924-fldads-threadmain/base-control-comparison.json'),('target_correct','docs/attempts/research-20260924-fldads-threadmain/update-local-before-csv-random-after-threadmain-comparison.json')]:
 d=json.loads((ROOT/rel).read_text()); fs={f['name']:f for f in d['functions']}; reports[label]={}
 for name in ['fldads_threadmain','fldads_get_random_ad']:
  f=fs[name]; reports[label][name]={'status':f['status'],'size':f.get('candidate_size'),'rdata_relocations':[{'offset':r.get('function_offset'),'addend':r.get('addend'),'historical_operand':hex(r['original_value']) if isinstance(r.get('original_value'),int) else None,'resolution':r.get('resolution'),'equal':r.get('equal')} for r in f.get('relocations',[]) if r.get('symbol')=='.rdata' and r.get('type')==6]}
result={'provenance':'Fresh locked TDM-2 object overlays compared to the unchanged original PE; no original object/source is available.','objects':{'baseline':{'size':len(b0),'sha256':hashlib.sha256(b0).hexdigest(),'strings':strings(b0)},'historical-update-local-order-plus-random-after-target':{'size':len(b1),'sha256':hashlib.sha256(b1).hexdigest(),'strings':strings(b1)},'delta_bytes':len(b1)-len(b0)},'candidate_float_reference':{'bytes':needle.hex(),'baseline_section_offset':hex(b0.find(needle)),'target_correct_section_offset':hex(b1.find(needle)),'historical_direct_operand':hex(0x4d4490)},'original_pe_float_occurrences_in_rdata':occ,'original_pe_rdata':{'rva':hex(sec['rva']),'raw_size':sec['raw_size'],'virtual_size':sec['virtual_size']},'function_relocations':reports,'conclusion':'Historical source-line order proves fldads_update_local_adimg precedes fldads_load_cache_from_csv; moving the whole unchanged definition swaps read-only string emission: Local file/Downloading precede Warning, and the later target literals move by four bytes (rdata 0x1a4 to 0x1a0). No data/string content is added or removed; the changed extent reflects padding/ordering. In the target-correct object, the float constant moves from .rdata+0x1a0 to +0x19c. Its four bytes occur multiple times in original PE .rdata, and the PE has no symbol/relocation/DWARF owner for this anonymous constant pool entry, so these materials cannot independently assign the original +0x4d4490 owner or prove a safe compensation. Stop pending original object/owner evidence.'}
(ROOT/'docs/attempts/research-20260924-fldads-threadmain/rdata-owner-analysis.json').write_text(json.dumps(result,indent=2)); print(json.dumps({k:v for k,v in result.items() if k not in ('objects','function_relocations')},indent=2))

