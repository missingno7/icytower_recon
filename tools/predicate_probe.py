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


def invert_return_guard(text,function,condition):
    scalar=r'[A-Za-z_]\w*(?:\s*->\s*[A-Za-z_]\w*)?'
    if not re.fullmatch(scalar+r'\s*(?:==|!=)\s*'+scalar,condition):raise ValueError('Only a scalar equality guard is supported')
    lo,hi=function_span(text,function);clean=sanitized(text)
    spelling=r'\s*'.join(re.escape(t) for t in re.findall(r'->|==|!=|\w+',condition))
    matches=list(re.finditer(r'\bif\s*\(\s*('+spelling+r')\s*\)\s*\{',clean[lo:hi]))
    if len(matches)!=1:raise ValueError('Expected one braced equality guard')
    match=matches[0];start=lo+match.start();opening=lo+match.end()-1
    if clean[lo:start].count('{')-clean[lo:start].count('}')!=1:raise ValueError('Guard must be at function scope')
    depth=1;end=opening+1
    while end<hi and depth:
        depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
    body=clean[opening+1:end-1]
    terminal=re.search(r'\breturn\b[^;{}]*;\s*$',body)
    if not terminal or body[:terminal.start()].count('{')!=body[:terminal.start()].count('}'):raise ValueError('Guard needs an unconditional terminal return')
    prefix=body[:terminal.start()].rstrip()
    if prefix and prefix[-1] not in ';}':raise ValueError('Terminal return may still be controlled by an unbraced statement')
    tail=clean[end:hi-1]
    if not tail.strip() or re.match(r'\s*else\b',tail):raise ValueError('Expected a following function tail without else')
    if re.search(r'(?m)^\s*#|\b(?:goto|case|default)\b|(?:^|[;{}])\s*\w+\s*:',clean[start:hi-1]):raise ValueError('Labels or preprocessing require review')
    after='if (!('+text[lo+match.start(1):lo+match.end(1)]+')) {'+text[end:hi-1]+'} else '+text[opening:end]
    change={'start':start,'end':hi-1,'before':text[start:hi-1],'after':after}
    return text[:start]+after+text[hi-1:],change


def interval_switch(text,function,variable):
    if not re.fullmatch(r'[A-Za-z_]\w*',variable):raise ValueError('One interval variable required')
    lo,hi=function_span(text,function);clean=sanitized(text)
    scalar=r'[A-Za-z_]\w*(?:\s*->\s*[A-Za-z_]\w*)?'
    pattern=r'\bif\s*\(\s*(!\s*'+scalar+r')\s*&&\s*\(unsigned\s+int\)\s*\(\s*'+re.escape(variable)+r'\s*-\s*(\d+)\s*\)\s*<=\s*(\d+)U\s*\)\s*\{'
    matches=list(re.finditer(pattern,clean[lo:hi]))
    if len(matches)!=1:raise ValueError('One guarded unsigned interval required')
    m=matches[0];lower=int(m[2]);count=int(m[3])+1
    if not 1<=count<=8 or lower+count>2147483647:raise ValueError('Interval exceeds bounded switch scope')
    start=lo+m.start();opening=lo+m.end()-1;end=opening+1;depth=1
    while end<hi and depth:
        depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
    body=clean[opening+1:end-1]
    terminal=re.search(r'\breturn\b[^;{}]*;\s*$',body)
    if not terminal or body[:terminal.start()].count('{')!=body[:terminal.start()].count('}') or (body[:terminal.start()].rstrip() and body[:terminal.start()].rstrip()[-1] not in ';}'):raise ValueError('Interval arm must end in unconditional return')
    if re.match(r'\s*else\b',clean[end:hi]):raise ValueError('Existing else unsupported')
    if re.search(r'\b(?:break|continue|goto|case|default)\b|(?m:^\s*#)|(?:^|[;{}])\s*\w+\s*:',body):raise ValueError('Control transfer or label in interval arm')
    after='if ('+text[lo+m.start(1):lo+m.end(1)]+') { switch ('+variable+') { '+''.join('case '+str(v)+': ' for v in range(lower,lower+count))+text[opening:end]+' default: break; } }'
    change={'start':start,'end':end,'before':text[start:end],'after':after}
    return text[:start]+after+text[end:],change


def probe(target,function,expression,invert_guard=None,switch_interval=None):
    if invert_guard and switch_interval:raise ValueError("Choose one structural trial per run")
    out=ROOT/'build/predicate-probes'/target/function
    reference=fresh_verify(target,dest=out/'reference');build=reference['build']
    source=build['config']['source'];original=(ROOT/source).read_bytes().decode('cp1252')
    candidate,recipe=plan(original,function,expression)
    variants=[('baseline',original),('equal-to-one',candidate)]
    guard_changes=[]
    if invert_guard:
        for label,text in [('inverted-guard',original),('equal-one-and-inverted-guard',candidate)]:
            changed,edit=invert_return_guard(text,function,invert_guard);variants.append((label,changed));guard_changes.append({'variant':label,'change':edit})
    if switch_interval:
        for label,text in [('interval-switch',original),('equal-one-and-interval-switch',candidate)]:
            changed,edit=interval_switch(text,function,switch_interval);variants.append((label,changed));guard_changes.append({'variant':label,'change':edit})
    inputs=dict(build['local_inputs'])
    tools={p:identity(ROOT/p) for p in ['tools/predicate_probe.py','tools/source_scope.py']}
    result={'scope':'Scratch-only experiment; no production edits or promotion proof.','target':target,'function':function,'expression':expression,'recipe':recipe,'guard_changes':guard_changes,'invert_guard':invert_guard,'switch_interval':switch_interval,
            'source_inputs':inputs,'probe_tools':tools,'compiler':build,'fixture':reference['fixture'],'verifier':reference['verifier'],
            'baseline_source':original,'outcome':'COMPLETE','variants':[]}
    for label,text in variants:
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('target');p.add_argument('function');p.add_argument('expression');p.add_argument('--invert-guard');p.add_argument('--switch-interval');a=p.parse_args()
    raise SystemExit(0 if probe(a.target,a.function,a.expression,a.invert_guard,a.switch_interval)['outcome']=='COMPLETE' else 1)
