"""Isolated interface-plus-branch experiment. Never a promotion input."""
import argparse
import json
from pathlib import Path
from common import ROOT,read_json,write_json,identity,run
from build import COMPILERS,verify_inputs
from recovery_pipeline import fresh_verify,OBJDUMP,verifier_identity
from experiment import compare
from interface_tasks import patch_text,plan_interface
from interface_type_probe import report_fingerprint
from interfaces import collect_interfaces
from source_scope import sanitized,function_span,body_hash
import re


def invert_if(text,function,variable):
    if not re.fullmatch(r'[A-Za-z_]\w*',variable): raise ValueError('Condition must be one scalar identifier')
    start,end=function_span(text,function);clean=sanitized(text)
    matches=list(re.finditer(r'\bif\s*\(\s*'+re.escape(variable)+r'\s*\)\s*\{',clean[start:end]))
    if len(matches)!=1: raise ValueError('Expected one explicit braced if for this condition')
    match=matches[0];a=start+match.start();first=start+match.end()-1
    def close(opening):
        depth=1;at=opening+1
        while at<end and depth:
            depth+=(clean[at]=='{')-(clean[at]=='}');at+=1
        if depth: raise ValueError('Unclosed branch')
        return at
    first_end=close(first)
    other=re.match(r'\s*else\s*\{',clean[first_end:end])
    if not other: raise ValueError('An explicit braced else is required')
    second=first_end+other.end()-1;b=close(second)
    if re.search(r'(?m)^\s*#|\b(?:case|goto)\b|(?:^|[;{}])\s*[A-Za-z_]\w*\s*:',clean[a:b]):
        raise ValueError('Preprocessor directives or labels require supervisor review')
    replacement='if (!('+variable+')) '+text[second:b]+' else '+text[first:first_end]
    return text[:a]+replacement+text[b:],{'start':a,'end':b,'before':text[a:b],'after':replacement}


def probe(target,function,interface,condition):
    from refresh_recovery import validate_ledger
    ledger=read_json(ROOT/'src/recovery.json');validate_ledger(ledger)
    _,conflicts=collect_interfaces(ledger)
    rows=[r for r in conflicts if r['function']==interface]
    if len(rows)!=1: raise ValueError('Expected one known interface conflict')
    plan=plan_interface(rows[0],ledger)
    if plan['task_kind']!='INTERFACE' or not plan.get('changes'): raise ValueError('No bounded interface recipe')
    out=ROOT/'build/compound-probes'/target/function
    reference=fresh_verify(target,dest=out/'reference')
    build=reference['build'];source=build['config']['source'];original=(ROOT/source).read_bytes().decode('cp1252')
    edits=[e for e in plan['changes'] if e['file']==source]
    if not edits: raise ValueError('Interface recipe does not edit this CU source')
    declared=patch_text(original,edits)
    if body_hash(original,function)!=body_hash(declared,function): raise ValueError('Interface recipe changes target body')
    combined,branch=invert_if(declared,function,condition)
    variants=[('baseline',original),('interface-only',declared),('interface-and-inverted-if',combined)]
    result={'scope':'Diagnostic only; no maintained source edits, no ledger promotion, no bypass of interface/body admission.',
        'target':target,'function':function,'interface':interface,'condition':condition,
        'source_inputs':build['local_inputs'],'toolchain_lock':build['candidate_toolchain_lock'],
        'compiler':build['compiler'],'compiler_config':build['config'],'compiler_flags':build['flags'],
        'fixture':reference['fixture'],'verifier':reference['verifier'],'baseline_source':original,'outcome':'COMPLETE',
        'probe_tool':identity(ROOT/'tools/compound_probe.py'),'interface_changes':edits,'branch_change':branch,'variants':[]}
    for label,text in variants:
        folder=out/label;folder.mkdir(parents=True,exist_ok=True);copy=folder/'probe.c';copy.write_bytes(text.encode('cp1252'))
        args=list(build['command'])
        for flag,value in [('-MF',folder/'unit.d'),('-aux-info',folder/'interfaces.aux'),('-c',copy),('-o',folder/'unit.o')]:args[args.index(flag)+1]=str(value)
        args[1:1]=['-I'+str((ROOT/source).parent)]
        try: run(args,toolchain=COMPILERS['tdm-2'])
        except RuntimeError as exc:
            result['outcome']='COMPILE_FAILED'
            result['variants'].append({'variant':label,'source_identity':identity(copy),'compile_error':str(exc)})
            break
        report=compare(folder/'unit.o',reference['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
        if label=='baseline' and report_fingerprint(report)!=report_fingerprint(reference):
            raise ValueError('Scratch baseline changes emission')
        row=next(r for r in report['functions'] if r['name']==function)
        result['variants'].append({'variant':label,'source':copy.relative_to(ROOT).as_posix(),'source_identity':identity(copy),
            'target_body_sha256':body_hash(text,function),'object_identity':identity(folder/'unit.o'),
            'status':row['status'],'candidate_size':row.get('candidate_size'),'original_size':row['original_size'],
            'body_shape_equal':row.get('body_shape_equal'),'first_difference':row.get('first_difference'),
            'difference_offsets':row.get('difference_offsets',[]),'function_matches':report['function_matches'],
            'relocations':[r for r in row.get('relocations',[]) if not r['equal']],
            'direct_transfers':[r for r in row.get('direct_transfers',[]) if not r['equal']]})
        print(label,row['status'],row.get('candidate_size'),'/',row['original_size'],flush=True)
    for path,expected in build['local_inputs'].items():
        if identity(ROOT/path)!=expected: raise ValueError('Maintained source changed during probe')
    if identity(ROOT/'tools/compound_probe.py')!=result['probe_tool']: raise ValueError('Probe tool changed during execution')
    verify_inputs('tdm-2')
    if verifier_identity()!=result['verifier'] or identity(ROOT/'assets/icytower15.exe')!=result['fixture']:
        raise ValueError('Verifier or historical fixture changed during execution')
    dest=ROOT/'docs/attempts/compound-probes'/target/(function+'.json')
    if dest.exists():
        with dest.with_suffix('.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(read_json(dest),separators=(',',':'))+'\n')
    write_json(dest,result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('target');parser.add_argument('function')
    parser.add_argument('--interface',required=True);parser.add_argument('--invert-if',required=True)
    args=parser.parse_args();result=probe(args.target,args.function,args.interface,args.invert_if)
    raise SystemExit(0 if result['outcome']=='COMPLETE' else 1)
