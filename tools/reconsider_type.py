"""Reopen a blocked type experiment only after fresh raw-preserving CU probes."""
import argparse
from common import ROOT,read_json,write_json,identity
from type_context_probe import probe
from type_tasks import plans as canonical_plans
from type_views import plans as view_plans
from grinder_task import SESSION,snapshot_files
from promote_function import promotion_lock,JOURNAL
from publication import publication
from refresh_recovery import validate_ledger,publish_status
from recovery_pipeline import CURRENT


def require_preservation(result,target,task):
    if result.get('target')!=target or result.get('task')!=task or result.get('outcome')!='COMPLETE':raise ValueError('Incomplete/wrong type reconsideration probe')
    variants=result.get('variants',[])
    for label in ('baseline','canonical'):
        rows=[v for v in variants if v.get('variant')==label]
        if len(rows)!=1 or rows[0].get('raw_baseline_equal') is not True:raise ValueError('Raw contribution preservation unproven: '+target+':'+label)


def reconsider(name):
    with promotion_lock():
        if SESSION.exists():raise ValueError('Finish the active task before reconsideration')
        ledger=read_json(ROOT/'src/recovery.json');validate_ledger(ledger)
        blocks_path=CURRENT/'interface-blocks.json';blocks=read_json(blocks_path)
        if name not in blocks:raise ValueError('No recorded type block')
        candidates=[p for p in canonical_plans(ledger)+view_plans(ledger) if p['function']==name]
        if len(candidates)!=1 or not candidates[0]['affected_targets']:raise ValueError('No unique bounded current type recipe')
        plan=candidates[0];before=snapshot_files();ledger_id=identity(ROOT/'src/recovery.json');blocks_id=identity(blocks_path)
        probes=[]
        for target in plan['affected_targets']:
            result=probe(target,name);require_preservation(result,target,name)
            probes.append('docs/attempts/type-context-probes/'+target+'/'+name+'.json')
        if snapshot_files()!=before or identity(ROOT/'src/recovery.json')!=ledger_id or identity(blocks_path)!=blocks_id:raise ValueError('Reconsideration inputs changed')
        path=ROOT/'docs/attempts/type-reconsideration'/(name+'.json')
        protected=[ROOT/'src/recovery.json',ROOT/'docs/progress.json',ROOT/'docs/blocker-summary.json',path,*CURRENT.rglob('*')]
        with publication(protected,CURRENT,JOURNAL,ROOT):
            previous=blocks.pop(name);write_json(blocks_path,blocks);publish_status(ledger)
            rows=[t for t in read_json(CURRENT/'grinder-queue.json')['tasks'] if t['function']==name and t['task_kind']==plan['task_kind']]
            if len(rows)!=1 or rows[0]['difficulty']!='CHEAP':raise ValueError('Another prerequisite still prevents bounded type admission')
            write_json(path,{'task':name,'prior_block':previous,'probes':[{'path':p,'identity':identity(ROOT/p)} for p in probes],
                'state':'REOPENED_FOR_VERIFIED_EXPERIMENT','source_inputs':plan['source_identities'],
                'limit':'Only the historical block is retired. No source or proof status changed; ordinary FAST and atomic promotion remain mandatory.'})
        print('Reopened bounded task:',name)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('task');a=p.parse_args();reconsider(a.task)
