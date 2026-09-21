"""Isolate canonical-type and assertion-declaration effects. Never promotion proof."""
import argparse,json
from common import ROOT,identity,read_json,write_json,run
from build import COMPILERS,verify_inputs
from recovery_pipeline import fresh_verify,OBJDUMP,verifier_identity
from type_tasks import plans as canonical_plans
from type_views import plans as view_plans
from interface_tasks import patch_text
from interface_type_probe import report_fingerprint
from contribution_diagnostics import compare as contribution_compare
from experiment import compare


VARIANTS=[('baseline',False,False),('baseline-without-assertions',False,True),
          ('canonical',True,False),('canonical-without-assertions',True,True)]


def probe(target,task):
    ledger=read_json(ROOT/'src/recovery.json')
    candidates=[p for p in canonical_plans(ledger)+view_plans(ledger) if p['function']==task]
    if len(candidates)!=1:raise ValueError('Unique current canonical/type-view recipe required')
    plan=candidates[0]
    if target not in plan['affected_targets']:raise ValueError('Target is outside this recipe')
    out=ROOT/'build/type-context-probes'/target/task
    reference=fresh_verify(target,dest=out/'reference');build=reference['build'];source=build['config']['source']
    inputs=dict(build['local_inputs'])
    for path in (ROOT/'include/recovered').glob('*.h'):inputs[path.relative_to(ROOT).as_posix()]=identity(path)
    texts={p:(ROOT/p).read_bytes().decode('cp1252') for p in inputs if p.startswith(('src/','include/'))}
    edits=[e for e in plan['changes'] if e['file'] in texts]
    if not edits:raise ValueError('Recipe has no compiled input edits in this target')
    tools={p:identity(ROOT/p) for p in ('tools/type_context_probe.py','tools/type_tasks.py','tools/type_views.py','tools/interface_tasks.py')}
    result={'scope':'Four isolated diagnostic variants. Disabling assertions here is not a production change or acceptance option.',
        'target':target,'task':task,'plan':plan,'source_inputs':inputs,'probe_tools':tools,'compiler':build,
        'fixture':reference['fixture'],'verifier':reference['verifier'],'baseline_sources':texts,'variants':[],'outcome':'COMPLETE'}
    reports={}
    for label,canonical,no_assertions in VARIANTS:
        folder=out/label;overlay=folder/'overlay';folder.mkdir(parents=True,exist_ok=True)
        for path,text in texts.items():
            if canonical:text=patch_text(text,[e for e in edits if e['file']==path])
            dest=overlay/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(text.encode('cp1252'))
        args=list(build['command'])
        for flag,value in [('-MF',folder/'unit.d'),('-aux-info',folder/'interfaces.aux'),('-c',overlay/source),('-o',folder/'unit.o')]:args[args.index(flag)+1]=str(value)
        args[1:1]=['-I'+str(overlay/'include'),'-I'+str((ROOT/source).parent)]
        if no_assertions:args.insert(1,'-DRECOVERED_STATIC_ASSERT(expr,name)=')
        try:run(args,toolchain=COMPILERS[build['compiler']])
        except RuntimeError as exc:
            result['outcome']='COMPILE_FAILED';result['variants'].append({'variant':label,'error':str(exc)});break
        report=compare(folder/'unit.o',reference['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP);reports[label]=report
        equal=report_fingerprint(report)==report_fingerprint(reference)
        if label=='baseline' and not equal:raise ValueError('Overlay baseline changes raw contributions')
        result['variants'].append({'variant':label,'assertions_enabled':not no_assertions,'canonical_recipe_applied':canonical,
            'command':[str(a) for a in args],'object':identity(folder/'unit.o'),'raw_baseline_equal':equal,
            'function_matches':report['function_matches'],'contribution_diagnostics':contribution_compare(reference,report)})
        print(label,'raw baseline equal:',equal,flush=True)
    if len(reports)==4:
        result['paired_effects']={
            'canonicalization_with_assertions':contribution_compare(reports['baseline'],reports['canonical']),
            'canonicalization_without_assertions':contribution_compare(reports['baseline-without-assertions'],reports['canonical-without-assertions']),
            'assertions_in_baseline':contribution_compare(reports['baseline'],reports['baseline-without-assertions']),
            'assertions_after_canonicalization':contribution_compare(reports['canonical'],reports['canonical-without-assertions'])}
    for path,expected in {**inputs,**tools}.items():
        if identity(ROOT/path)!=expected:raise ValueError('Probe input changed: '+path)
    verify_inputs(build['compiler'])
    if verifier_identity()!=result['verifier'] or identity(ROOT/'assets/icytower15.exe')!=result['fixture']:raise ValueError('Oracle identity changed')
    dest=ROOT/'docs/attempts/type-context-probes'/target/(task+'.json')
    if dest.exists():
        with dest.with_suffix('.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(read_json(dest),separators=(',',':'))+'\n')
    write_json(dest,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('target');p.add_argument('task');a=p.parse_args()
    raise SystemExit(0 if probe(a.target,a.task)['outcome']=='COMPLETE' else 1)
