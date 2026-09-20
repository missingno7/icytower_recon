"""Isolated global-type experiment; never a ledger/promotion input."""
import sys,re,json
from pathlib import Path
sys.path.insert(0,'tools')
from common import ROOT,read_json,write_json,identity,run
from recovery_pipeline import fresh_verify,OBJDUMP
from build import TARGETS,COMPILERS
from experiment import compare
from storage_diagnostics import diagnose
from type_views import shape_key
from source_scope import sanitized
from source_order import definition_spans

target='game-main'; name='play_char'
out=ROOT/'build/global-type-probes'/target/name; out.mkdir(parents=True,exist_ok=True)
baseline=fresh_verify(target,dest=out/'baseline')
row=next(r for r in diagnose(baseline)['objects'] if r['original']['name']==name and r['original']['scope']==['GLOBAL'])
old,new=row['original'],row['candidate']; source=ROOT/baseline['build']['config']['source']; before=identity(source)
assert new and new['layout']['kind']=='base_type'
first=old['layout']['members'][0]
assert first['offset']==0 and shape_key(first['layout'])==shape_key(new['layout'])
header=ROOT/'include/recovered'/(old['type']+'.h'); assert header.exists()
text=source.read_bytes().decode('cp1252'); clean=sanitized(text)
line=new['declaration_line']; lines=text.splitlines(keepends=True); start=sum(map(len,lines[:line-1])); end=start+len(lines[line-1].rstrip('\r\n'))
assert re.fullmatch(r'\s*'+re.escape(new['type'])+r'\s+'+name+r'\s*;',clean[start:end])
changes=[{'start':start,'end':end,'before':text[start:end],'after':old['type']+' '+name+';','role':'declaration'}, {'start':0,'end':0,'before':'','after':'#include "recovered/'+old['type']+'.h"\n','role':'generated_header'}]
spans=definition_spans(text)
for m in re.finditer(r'\b'+name+r'\b',clean):
 if start<=m.start()<end: continue
 prefix=clean[:m.start()].rstrip()
 if prefix.endswith('&') and (not prefix[:-1].rstrip() or prefix[:-1].rstrip()[-1] in '=([{,:?'):
  continue
 owners=[s for s in spans if s['start']<m.start()<s['end']]; assert len(owners)==1
 function=owners[0]['name']
 assert not any(v['name']==name for v in baseline['candidate_debug']['functions'][function]['variables'])
 assert not prefix.endswith(('.',']')) and not re.search(r'\bsizeof\s*\(?\s*$',prefix)
 changes.append({'start':m.start(),'end':m.end(),'before':name,'after':name+'.'+first['name'],'role':'offset_zero_scalar_access','function':function})
from interface_tasks import patch_text
copy=out/'candidate.c'; copy.write_bytes(patch_text(text,changes).encode('cp1252'))
args=list(baseline['build']['command']); obj=out/'candidate.o'
for flag,value in [('-MF',out/'candidate.d'),('-aux-info',out/'interfaces.aux'),('-c',copy),('-o',obj)]: args[args.index(flag)+1]=str(value)
args.insert(1,'-I'+str(source.parent))
run(args,toolchain=COMPILERS['tdm-2'])
report=compare(obj,TARGETS[target]['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
write_json(out/'comparison.json',report)
old_sections={s['name']:s['sha256'] for s in baseline['object_sections']}; new_sections={s['name']:s['sha256'] for s in report['object_sections']}
old_fn={f['name']:f for f in baseline['functions']}
result={'scope':'ISOLATED_DIAGNOSTIC_ONLY; maintained source and ledger unchanged','target':target,'global':name,'original_type':old['type'],'original_size':old['size'],'candidate_size':new['size'],'changes':changes,'source_before':before,'probe_source':identity(copy),'command':args,'object':identity(obj),'section_equal':{s:old_sections.get(s)==new_sections.get(s) for s in ('.text','.data','.rdata')},'protected_bodies_edited':[c['function'] for c in changes if c.get('function') and old_fn[c['function']]['status']=='FUNCTION_MATCH'],'new_exact_regressions':[f['name'] for f in report['functions'] if old_fn[f['name']]['status']=='FUNCTION_MATCH' and f['status']!='FUNCTION_MATCH'],'first_differences':[{'name':f['name'],'first_difference':f.get('first_difference')} for f in report['functions'] if old_fn[f['name']]['status']=='FUNCTION_MATCH' and f['status']!='FUNCTION_MATCH']}
assert identity(source)==before
write_json(out/'reproduction-result.json',result)
print(json.dumps(result,indent=2))
