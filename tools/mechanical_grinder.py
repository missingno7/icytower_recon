"""Run bounded, generated mechanical tasks through the existing proof gates."""
import argparse,json,re,subprocess,sys
from datetime import datetime,timezone
from common import ROOT,read_json,write_json
from grinder_task import SESSION
from task_outcomes import CANDIDATE_REJECTED_EXIT

KINDS={'INTERFACE','CANONICAL_TYPE','TYPE_VIEW','SOURCE_ORDER','ARRAY_EXTENT','DATA_POINTER','LOCAL_DECLARATION','STATIC_SCOPE','GLOBAL_TYPE'}


def select_task(tasks,attempted=()):
    for task in tasks:
        key=(task.get('task_kind'),task['function'])
        if task.get('difficulty')=='CHEAP' and task.get('task_kind') in KINDS and key not in attempted:
            if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',task['function']): raise ValueError('Invalid mechanical task identifier')
            return task
    return None


def execute_task(task,invoke,session_state,recovery_required):
    name=task['function']
    def owned():
        current=session_state()
        if task.get('task_kind')=='FUNCTION_BODY':
            return current is not None and current.get('kind')!='INTERFACE' and current.get('function')==name and current.get('target')==task['target']
        return current is not None and current.get('kind')=='INTERFACE' and current.get('function')==name
    for stage in ('begin','apply','check','promote'):
        if stage!='begin' and not owned(): return {'state':'RECOVERY_REQUIRED','stage':stage,'reason':'Expected task session is absent or belongs to another task','continue':False}
        result=invoke(stage,name)
        if result['returncode']:
            reason=(result.get('stderr') or result.get('stdout') or 'No diagnostic output').strip()[-1800:]
            if recovery_required(): return {'state':'RECOVERY_REQUIRED','stage':stage,'reason':reason,'continue':False}
            # Only the explicit completed-FAST rejection contract can blame a candidate.
            # Compiler, I/O, apply, admission and acceptance failures stop for review.
            cleanup='block' if stage=='check' and result['returncode']==CANDIDATE_REJECTED_EXIT else 'abort'
            if owned():
                restored=invoke(cleanup,name,stage+' failed: '+reason)
                if restored['returncode'] or session_state() is not None:
                    return {'state':'RECOVERY_REQUIRED','stage':stage,'reason':reason,'continue':False}
            elif session_state() is not None:
                return {'state':'RECOVERY_REQUIRED','stage':stage,'reason':'Foreign task session appeared','continue':False}
            return {'state':'BLOCKED_SUPERVISOR' if cleanup=='block' else 'STOPPED_FOR_REVIEW','stage':stage,'reason':reason,'continue':cleanup=='block'}
    if session_state() is not None: return {'state':'RECOVERY_REQUIRED','stage':'promote','reason':'Successful acceptance left an open task session','continue':False}
    return {'state':'PROMOTED','continue':True}


def busy():
    return any((ROOT/'build/grinder'/name).exists() for name in ('promotion.lock','recovery.lock','publication.zip'))


def run_batch(limit):
    if limit<1: raise ValueError('Task limit must be positive')
    if SESSION.exists() or busy(): raise ValueError('Finish or recover the existing task/transaction first')
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'); folder=ROOT/'docs/attempts/mechanical-runs'/run_id; folder.mkdir(parents=True)
    history=ROOT/'docs/attempts/mechanical-runs'/(run_id+'.jsonl'); history.parent.mkdir(parents=True,exist_ok=True)
    sequence=0; outcomes=[]; attempted=set()
    def record(row):
        with history.open('a',encoding='utf-8') as stream: stream.write(json.dumps(row,separators=(',',':'))+'\n')
    def invoke(action,name,reason=None):
        nonlocal sequence
        sequence+=1; args=[sys.executable,'tools/interface_task.py',action,name]
        if reason is not None: args+=['--reason',reason]
        print(action,name,flush=True)
        try:
            completed=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,errors='replace')
            result={'returncode':completed.returncode,'stdout':completed.stdout,'stderr':completed.stderr}
        except OSError as exc:
            result={'returncode':1,'stdout':'','stderr':type(exc).__name__+': '+str(exc)}
        log=folder/('%03d-%s-%s.json'%(sequence,name,action))
        write_json(log,result)
        record({'event':'STAGE','task':name,'action':action,'returncode':result['returncode'],'log':log.relative_to(ROOT).as_posix()})
        return result
    state=lambda:read_json(SESSION) if SESSION.exists() else None
    for _ in range(limit):
        tasks=read_json(ROOT/'docs/current/grinder-queue.json')['tasks']; task=select_task(tasks,attempted)
        if task is None: break
        if SESSION.exists() or busy(): raise ValueError('Another task or transaction became active')
        attempted.add((task['task_kind'],task['function']))
        record({'event':'SELECTED','task':task,'scope':'Generated mechanical edits only; existing FAST/ACCEPTANCE gates perform all proof and publication.'})
        outcome=execute_task(task,invoke,state,busy); outcomes.append({'function':task['function'],'kind':task['task_kind'],**outcome}); record({'event':'OUTCOME',**outcomes[-1]})
        print(outcome['state'],task['function'],flush=True)
        if not outcome['continue']: break
        remaining=read_json(ROOT/'docs/current/grinder-queue.json')['tasks']
        if any(t['function']==task['function'] and t.get('task_kind')==task['task_kind'] and t.get('difficulty')=='CHEAP' for t in remaining):
            record({'event':'STOPPED_FOR_REVIEW','reason':'Task remained eligible after completion/block; planner progress invariant failed'})
            outcomes[-1]['continue']=False; break
    summary={'run':run_id,'limit':limit,'outcomes':outcomes,'history':history.relative_to(ROOT).as_posix(),
             'scope':'No body tasks, no automatic commits, no proof bypass. Stop on acceptance/infrastructure failures or incomplete cleanup.'}
    write_json(folder/'summary.json',summary); print('Run evidence:',summary['history'])
    return 1 if any(not r['continue'] for r in outcomes) else 0


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int,default=1); a=ap.parse_args()
    return run_batch(a.limit)


if __name__=='__main__': raise SystemExit(main())
