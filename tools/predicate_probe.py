"""Test one scalar truth test against equality to one in a scratch CU."""
import argparse,json
from common import ROOT,identity,read_json,write_json,run
from build import COMPILERS,verify_inputs
from recovery_pipeline import fresh_verify,OBJDUMP,verifier_identity
from interface_type_probe import report_fingerprint
from experiment import compare
from contribution_diagnostics import compare as contribution_compare
import re
from source_scope import function_span,sanitized


def plan(text,function,expression):
    if not re.fullmatch(r"[A-Za-z_]\w*(?:\s*->\s*[A-Za-z_]\w*)?",expression):raise ValueError("Only a simple scalar or pointer member is supported")
    lo,hi=function_span(text,function);clean=sanitized(text)
    spelling=r"\s*".join(re.escape(t) for t in re.findall(r"->|\w+",expression))
    matches=list(re.finditer(r"\bif\s*\(\s*("+spelling+r")\s*\)",clean[lo:hi]))
    if len(matches)!=1:raise ValueError("Expected one unnegated truth-test condition")
    a,b=matches[0].span(1);a+=lo;b+=lo
    change={"start":a,"end":b,"before":text[a:b],"after":"("+text[a:b]+") == 1"}
    return text[:a]+change["after"]+text[b:],change


def probe(target,function,expression):
    out=ROOT/'build/predicate-probes'/target/function
    reference=fresh_verify(target,dest=out/'reference');build=reference['build']
    source=build['config']['source'];original=(ROOT/source).read_bytes().decode('cp1252')
    candidate,recipe=plan(original,function,expression)
    inputs=dict(build['local_inputs'])
    tools={p:identity(ROOT/p) for p in ['tools/predicate_probe.py','tools/source_scope.py']}
    result={'scope':'Scratch-only experiment; no production edits or promotion proof.','target':target,'function':function,'expression':expression,'recipe':recipe,
            'source_inputs':inputs,'probe_tools':tools,'compiler':build,'fixture':reference['fixture'],'verifier':reference['verifier'],
            'baseline_source':original,'outcome':'COMPLETE','variants':[]}
    for label,text in [('baseline',original),('equal-to-one',candidate)]:
        folder=out/label;folder.mkdir(parents=True,exist_ok=True);copy=folder/'probe.c';copy.write_bytes(text.encode('cp1252'))
        args=list(build['command'])
        for flag,value in [('-MF',folder/'unit.d'),('-aux-info',folder/'interfaces.aux'),('-c',copy),('-o',folder/'unit.o')]:args[args.index(flag)+1]=str(value)
        args[1:1]=['-I'+str((ROOT/source).parent)]
        try:run(args,toolchain=COMPILERS[build['compiler']])
        except RuntimeError as exc:
            result['outcome']='COMPILE_FAILED';result['variants'].append({'variant':label,'error':str(exc)});break
        report=compare(folder/'unit.o',reference['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
        before,after=report_fingerprint(reference),report_fingerprint(report)
        equal=after==before
        raw_delta={k:{'removed':[r for r in before[k] if r not in after[k]][:8],
                      'added':[r for r in after[k] if r not in before[k]][:8],
                      'before_count':len(before[k]),'after_count':len(after[k])}
                   for k in before if before[k]!=after[k]}
        if label=='baseline' and not equal:raise ValueError('Scratch baseline changes contributions')
        result['variants'].append({'variant':label,'object':identity(folder/'unit.o'),'source_identity':identity(copy),
            'raw_contributions_equal':equal,'raw_fingerprint_delta':raw_delta,'function_matches':report['function_matches'],'target_result':{k:next(r for r in report['functions'] if r['name']==function).get(k) for k in ('status','candidate_size','original_size','first_difference','body_shape_equal')},
            'contribution_diagnostics':contribution_compare(reference,report)})
        print(label,'raw contributions equal:',equal,flush=True)
    for path,expected in {**inputs,**tools}.items():
        if identity(ROOT/path)!=expected:raise ValueError('Probe input changed: '+path)
    verify_inputs(build['compiler'])
    if verifier_identity()!=result['verifier'] or identity(ROOT/'assets/icytower15.exe')!=result['fixture']:raise ValueError('Oracle input changed')
    dest=ROOT/'docs/attempts/predicate-probes'/target/(function+'.json')
    if dest.exists():
        with dest.with_suffix('.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(read_json(dest),separators=(',',':'))+'\n')
    write_json(dest,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('target');p.add_argument('function');p.add_argument('expression');a=p.parse_args()
    raise SystemExit(0 if probe(a.target,a.function,a.expression)['outcome']=='COMPLETE' else 1)
