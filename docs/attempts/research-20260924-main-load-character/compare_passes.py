import difflib, pathlib, re
base=pathlib.Path('build/tu-context/game-main/research-20260924-main-load-character-accepted-context-pass-baseline')
cand=pathlib.Path('build/tu-context/game-main/research-20260924-main-load-character-init-snapshot-pass')
def section(path,name):
 t=path.read_text(errors='replace'); starts=[m.start() for m in re.finditer(r'^;; Function ([^\n]+)$',t,re.M)]
 for i,s in enumerate(starts):
  if name in t[s:t.find('\n',s)]: return t[s:starts[i+1] if i+1<len(starts) else len(t)]
def norm(s):
 s=re.sub(r'D:\\Prog\\icytower_recon\\build\\tu-context\\game-main\\research-20260924-main-load-character-[^\\]+\\overlay','OVERLAY',s)
 s=re.sub(r'0x[0-9a-fA-F]{7,16}','0xPTR',s); s=re.sub(r'temp\.\d+','temp.N',s)
 return s
for dump in ['main.c.181r.csa','main.c.182r.peephole2']:
 print(dump)
 for name in ['load_character']:
  aa=norm(section(base/dump,name)).splitlines(); bb=norm(section(cand/dump,name)).splitlines(); sm=difflib.SequenceMatcher(a=aa,b=bb,autojunk=False)
  changes=[(aa[i],bb[j]) for tag,i,k,j,l in sm.get_opcodes() if tag!='equal' for i,j in zip(range(i,k),range(j,l))][:5]
  print(name,'normalized_equal',aa==bb,'lines',len(aa),len(bb),'matching',round(sm.ratio(),4),'residuals',changes)
