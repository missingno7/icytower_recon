import struct,sys,json,hashlib
from pathlib import Path

def sections(p):
 b=Path(p).read_bytes(); n=struct.unpack_from('<H',b,2)[0]; opt=struct.unpack_from('<H',b,16)[0]; pos=20+opt; out={}
 for i in range(n):
  h=b[pos+i*40:pos+(i+1)*40]; name=h[:8].split(b'\0')[0].decode('ascii','replace'); size,ptr=struct.unpack_from('<II',h,16); out[name]=b[ptr:ptr+size] if size else b''
 return out
paths={
 'baseline':'build/tu-context/game-fld-adspot/fldads-threadmain-20260924-base-control/unit.o',
 'target_correct':'build/tu-context/game-fld-adspot/fldads-threadmain-20260924-update-local-random-after-threadmain/unit.o',
 'target_correct_prior':'build/tu-context/game-fld-adspot/fldads-threadmain-20260924-update-local-random-after-threadmain/unit.o'
}
for label,p in paths.items():
 d=sections(p)['.rdata']; print(label,'size',len(d),'sha',hashlib.sha256(d).hexdigest())
 i=0
 while i<len(d):
  j=d.find(b'\0',i); j=len(d) if j<0 else j
  chunk=d[i:j]
  if chunk and all(32<=x<127 or x in (9,10,13) for x in chunk): print(f'{i:04x}',repr(chunk.decode('ascii','replace')))
  i=j+1
 print('tail',d[-16:].hex())
