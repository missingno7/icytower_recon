import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from tu_context_probe import compile_overlay
from experiment import compare
from recovery_pipeline import OBJDUMP
src='src/fld_adspot.c'; target='game-fld-adspot'; outdir=ROOT/'docs/attempts/research-20260924-fldads-threadmain'
base=(ROOT/src).read_text(encoding='cp1252')
correct=base.replace('#include "recovered/FLDAdSpot.h"','#include "recovered/FLDAdSpot.h"\n#include "recovered/HTTPHeader.h"')
correct=correct.replace('    int iNumHeaders;\n    void *pHeaders;','    unsigned int iNumHeaders;\n    HTTPHeader *pHeaders;').replace('    int iPayloadSize;','    unsigned int iPayloadSize;')
size_t=correct.replace('void fldads_update_cache(unsigned char *pData, int iDataSize)','void fldads_update_cache(unsigned char *pData, size_t iDataSize)')
variants={'base-control':base,'httpresponse-dwarf-types':correct,'update-cache-size_t':size_t}
results={}
for label,s in variants.items():
    p=outdir/(label+'.c'); p.write_text(s,encoding='cp1252')
    out,ref,build,r=compile_overlay(target,src,s,'fldads-threadmain-20260924-'+label,dumps=False)
    if r.returncode:
        results[label]={'compile_failed':True,'stderr':r.stderr,'candidate_source_sha256':hashlib.sha256(s.encode('cp1252')).hexdigest()}; continue
    report=compare(out/'unit.o',ref['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
    (outdir/(label+'-comparison.json')).write_text(json.dumps(report,indent=2))
    fs={f['name']:f for f in report['functions']}
    results[label]={'candidate_source_sha256':hashlib.sha256(s.encode('cp1252')).hexdigest(),'object_sha256':hashlib.sha256((out/'unit.o').read_bytes()).hexdigest(),'function_matches':report.get('function_matches'),'whole_text_contribution_equal':report.get('whole_text_contribution_equal'),'object_match':report.get('object_match'),'cu_match':report.get('cu_match'),'target':{k:fs['fldads_threadmain'].get(k) for k in ['status','candidate_size','original_size','first_difference','mismatch_count']},'statuses':{n:f['status'] for n,f in fs.items()},'build_output':str(out.relative_to(ROOT))}
(outdir/'typed-interface-batch-summary.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
