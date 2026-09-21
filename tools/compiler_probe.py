"""Isolated compiler-context diagnostics. Probe objects are never promotion inputs."""
import argparse
import json
import re
from pathlib import Path
from common import ROOT,identity,read_json,write_json,run
from build import COMPILERS,TARGETS
from experiment import compare
from recovery_pipeline import fresh_verify,OBJDUMP
from source_scope import function_span,body_hash
from type_graph import graph
from compiler_context import resolved_candidate,variant_difference
from rtl_evidence import pass_identity,compare_passes


def scoped_dump(text,name):
    matches=list(re.finditer(r'^;; Function (\w+).*$',text,re.M))
    for index,match in enumerate(matches):
        if match[1]==name: return text[match.start():matches[index+1].start() if index+1<len(matches) else len(text)]
    return None


def omit_peer(text,target,peer):
    if peer==target: raise ValueError('Cannot omit the target function')
    before=body_hash(text,target)
    a,b=function_span(text,peer)
    variant=text[:a]+';'+'\n'*text[a:b].count('\n')+text[b:]
    if body_hash(variant,target)!=before: raise ValueError('Peer omission changed target body')
    return variant


def probe(target,name,omit,local_types=(),extra_flags=()):
    reference=fresh_verify(target,dest=ROOT/'build/compiler-evidence'/target/name/'reference')
    build=reference['build']; source=ROOT/build['config']['source']; before=identity(source)
    text=source.read_bytes().decode('cp1252'); start,_=function_span(text,name)
    variants=[('baseline',text)]
    for peer in omit:
        variants.append(('omit-'+peer,omit_peer(text,name,peer)))
    g=graph()
    original_unit=next(u for u in read_json(ROOT/'src/units.json') if u['source']==build['config']['source'])
    original_function=next(f for f in original_unit['functions'] if f['name']==name)
    for variable in local_types:
        old=[d for d in g.descendants(original_function['die']) if d['tag']=='DW_TAG_variable' and d['name']==variable]
        new=[d for d in reference['candidate_debug']['functions'][name]['variables'] if d['name']==variable]
        if len(old)!=1 or len(new)!=1: raise ValueError('Ambiguous local identity')
        desired=g.declaration(old[0]['type_ref']); actual=new[0]['type']
        if desired==actual: raise ValueError('Local type already agrees')
        if any(re.search(r'[^a-zA-Z_ *]',t) for t in (desired,actual)): raise ValueError('Complex declarator needs supervisor review')
        spelling=r'\s*'.join(re.escape(t) for t in re.findall(r'\w+|\*',actual))+r'\s*'+re.escape(variable)+r'\b'
        a,b=function_span(text,name); body=text[a:b]
        matches=list(re.finditer(r'(?m)^([ \t]*(?:register\s+)?)'+spelling,body))
        if len(matches)!=1: raise ValueError('Cannot isolate local declaration')
        match=matches[0]; replacement=match[1]+g.declaration(old[0]['type_ref'],variable)
        variant=text[:a]+body[:match.start()]+replacement+body[match.end():]+text[b:]
        variants.append(('dwarf-type-'+variable,variant))
    allowed={'-fno-unit-at-a-time','-fno-toplevel-reorder','-fno-schedule-insns2','-fno-peephole2'}
    if set(extra_flags)-allowed: raise ValueError('Flag is outside the bounded compiler-context diagnostic set')
    variants.extend(('flag-'+flag.lstrip('-'),text) for flag in extra_flags)
    result={'schema':1,'target':target,'function':name,'source':build['config']['source'],
            'source_inputs':build['local_inputs'],'toolchain_lock':build['candidate_toolchain_lock'],
            'probe_tool':identity(ROOT/'tools/compiler_probe.py'),'target_body_sha256':body_hash(text,name),'variants':[],
            'acceptance':'DIAGNOSTIC_ONLY: no ledger updates, no production source edits, no body or layout match claims.'}
    for label,variant in variants:
        if not label.startswith('dwarf-type-') and body_hash(variant,name)!=result['target_body_sha256']: raise ValueError('Target body changed in probe')
        out=ROOT/'build/compiler-evidence'/target/name/label; out.mkdir(parents=True,exist_ok=True)
        copy=out/'probe.c'; copy.write_bytes(variant.encode('cp1252')); obj=out/'unit.o'; obj.unlink(missing_ok=True)
        args=list(build['command'])
        for flag,value in [('-MF',out/'unit.d'),('-aux-info',out/'interfaces.aux'),('-c',copy),('-o',obj)]: args[args.index(flag)+1]=str(value)
        if label.startswith('flag-'): args.insert(args.index('-c'),'-'+label.removeprefix('flag-'))
        args[1:1]=['-fdump-rtl-all','-I'+str(source.parent)]
        args=[('-I'+str(ROOT/a[2:])) if a.startswith('-I') and not Path(a[2:]).is_absolute() else a for a in args]
        for stale in out.glob('*r.*'):
            if stale.is_file(): stale.unlink()
        run(args,cwd=out,toolchain=COMPILERS['tdm-2'])
        report=compare(obj,TARGETS[target]['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
        function=next(r for r in report['functions'] if r['name']==name)
        if label=='baseline':
            if next(s['sha256'] for s in report['object_sections'] if s['name']=='.text')!=next(s['sha256'] for s in reference['object_sections'] if s['name']=='.text'):
                raise ValueError('Diagnostic source copy changed baseline text; context experiment refused')
        dumps={}; passes=[]
        for dump in sorted(out.glob('*r.*'),key=pass_identity):
            scoped=scoped_dump(dump.read_text(errors='replace'),name)
            if scoped:
                dest=out/'focus'/dump.name; dest.parent.mkdir(exist_ok=True); dest.write_text(scoped,encoding='utf-8')
                number,phase=pass_identity(dump)
                dumps[str(number)+':'+phase]=dest.relative_to(ROOT).as_posix()
                passes.append({'number':number,'phase':phase,'path':dest.relative_to(ROOT).as_posix(),'identity':identity(dest)})
        result['variants'].append({'variant':label,'source':copy.relative_to(ROOT).as_posix(),'source_identity':identity(copy),'target_body_sha256':body_hash(variant,name),
            'command':args,'object':identity(obj),'candidate_size':function.get('candidate_size'),
            'comparison_verdict':function['status'],'all_function_matches':report['function_matches'],'whole_text_contribution_equal':report['whole_text_contribution_equal'],'difference_offsets':function.get('difference_offsets',[]),
            'instructions':function.get('instructions',[]),'candidate_offset':function.get('candidate_offset'),'resolved_code':resolved_candidate(function),
            'focused_rtl_dumps':dumps,'focused_rtl_passes':passes})
    for path,expected in build['local_inputs'].items():
        if identity(ROOT/path)!=expected: raise ValueError('Maintained source changed during compiler probe')
    if identity(source)!=before: raise ValueError('Probe modified maintained source')
    baseline=result['variants'][0]
    for variant in result['variants']:
        difference=variant_difference(baseline,variant)
        variant['context_difference']=difference
        variant['context_changed_offsets']=difference['first_changed_offsets']
        variant['rtl_comparison']=compare_passes(baseline,variant,ROOT)
    path=ROOT/'docs/attempts/compiler-context'/target/(name+'.json')
    if path.exists():
        archive=path.with_suffix('.jsonl')
        with archive.open('a',encoding='utf-8') as stream: stream.write(json.dumps(read_json(path),separators=(',',':'))+'\n')
    trace=path.with_name(name+'-rtl.json')
    result['rtl_tool']=identity(ROOT/'tools/rtl_evidence.py')
    result['rtl_evidence']=trace.relative_to(ROOT).as_posix()
    write_json(trace,{'target':target,'function':name,'probe_tool':result['probe_tool'],'rtl_tool':result['rtl_tool'],
                      'variants':[{'variant':v['variant'],**v['rtl_comparison']} for v in result['variants'] if v['variant']!='baseline']})
    result['source_snapshot']=text
    write_json(path,result)
    for variant in result['variants']:
        difference=variant['context_difference']
        print(variant['variant'],'size',variant['candidate_size'],'original mismatch bytes',len(variant['difference_offsets']),'first offsets',variant['difference_offsets'][:8],
              'context size delta',difference['size_delta'],'changed resolved bytes',difference['changed_byte_count'])
    print('Diagnostic context evidence:',path.relative_to(ROOT).as_posix())
    return result


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('target'); ap.add_argument('function'); ap.add_argument('--omit-peer','--omit-earlier',dest='omit_peer',action='append',default=[],help='Omit one other same-CU definition in a scratch copy; source order is unrestricted.'); ap.add_argument('--dwarf-local-type',action='append',default=[]); ap.add_argument('--extra-flags',action='append',default=[])
    a=ap.parse_args()
    if len(a.omit_peer)+len(a.dwarf_local_type)+len(a.extra_flags)>3: raise ValueError('At most three bounded context probes')
    probe(a.target,a.function,a.omit_peer,a.dwarf_local_type,a.extra_flags)


if __name__=='__main__': main()
