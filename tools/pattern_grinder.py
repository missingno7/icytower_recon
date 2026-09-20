"""Run only existing CHEAP, single-pattern body tasks through the guarded pipeline."""
import argparse
import re
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path
from common import ROOT,read_json,write_json
from build import TARGETS
from grinder_task import SESSION
from mechanical_grinder import execute_task,busy


def select_task(tasks,load,attempted=()):
    for task in tasks:
        source=task.get('source'); name=task['function']
        if task.get('task_kind')!='FUNCTION_BODY' or task.get('difficulty')!='CHEAP' or (source,name) in attempted: continue
        if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',name): raise ValueError('Invalid function identifier')
        targets=[t for t,c in TARGETS.items() if c['source']==source]
        if len(targets)!=1: raise ValueError('No unique maintained target')
        card=load('docs/current/functions/'+Path(source).stem+'/'+name+'.json')
        if (card['source'],card['function'],card['target'])!=(source,name,targets[0]): raise ValueError('Wrong candidate-card owner')
        patterns=card.get('source_patterns',[])
        if card['difficulty']!='CHEAP' or not card['body_edit_allowed'] or len(patterns)!=1: continue
        pattern=patterns[0]['id']
        if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9-]*',pattern): raise ValueError('Invalid pattern identifier')
        return {**task,'target':targets[0],'pattern':pattern}
    return None


def command(task,action,load,reason=None):
    target,name=task['target'],task['function']
    if action in ('begin','abort','block'):
        args=['tools/grinder_task.py',action,target,name]
    elif action=='apply': args=['tools/apply_pattern.py',target,name,task['pattern']]
    elif action=='check': args=['tools/check_function.py',target,name]
    elif action=='promote':
        card=load('build/fast/'+target+'/'+name+'.json')
        if (card['source'],card['function'],card['target'])!=(task['source'],name,target): raise ValueError('Wrong FAST result owner')
        claim=card['state']
        if claim not in ('FUNCTION_MATCH','BODY_MATCH_LAYOUT_BLOCKED'): raise ValueError('FAST did not prove a promotable state')
        args=['tools/promote_function.py',target,name,'--claim',claim]
    else: raise ValueError('Unknown stage')
    if reason is not None: args+=['--reason',reason]
    return [sys.executable,*args]


def run_batch(limit):
    if limit<1: raise ValueError('Task limit must be positive')
    if SESSION.exists() or busy(): raise ValueError('Finish or recover the active task first')
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder=ROOT/'build/pattern-runs'/run_id; folder.mkdir(parents=True)
    history=ROOT/'docs/attempts/pattern-runs'/(run_id+'.jsonl'); history.parent.mkdir(parents=True,exist_ok=True)
    load=lambda path:read_json(ROOT/path)
    attempted=set(); outcomes=[]; sequence=0
    def record(row):
        with history.open('a',encoding='utf8') as stream:
            import json
            stream.write(json.dumps(row,separators=(',',':'))+'\n')
    for _ in range(limit):
        task=select_task(load('docs/current/grinder-queue.json')['tasks'],load,attempted)
        if task is None: break
        if SESSION.exists() or busy(): raise ValueError('Another task or transaction appeared')
        attempted.add((task['source'],task['function'])); record({'event':'SELECTED','task':task})
        def invoke(action,name,reason=None):
            nonlocal sequence
            sequence+=1; print(action,task['target'],name,flush=True)
            try:
                args=command(task,action,load,reason)
                result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,errors='replace')
                output={'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
            except Exception as exc: output={'returncode':1,'stderr':str(exc)}
            log=folder/('%03d-%s-%s.json'%(sequence,name,action)); write_json(log,output)
            record({'event':'STAGE','task':name,'action':action,'returncode':output['returncode'],'log':log.relative_to(ROOT).as_posix()})
            return output
        outcome=execute_task(task,invoke,lambda:read_json(SESSION) if SESSION.exists() else None,busy)
        outcomes.append({'target':task['target'],'function':task['function'],**outcome}); record({'event':'OUTCOME',**outcomes[-1]})
        print(outcome['state'],task['function'],flush=True)
        if not outcome['continue']: break
        if any(t.get('source')==task['source'] and t['function']==task['function'] and t.get('task_kind')=='FUNCTION_BODY' and t.get('difficulty')=='CHEAP' for t in load('docs/current/grinder-queue.json')['tasks']):
            outcomes[-1]['continue']=False; record({'event':'STOPPED_FOR_REVIEW','reason':'Task remained CHEAP after completion or block'}); break
    write_json(folder/'summary.json',{'outcomes':outcomes,'scope':'Only one generated body pattern per task; no inferred commands, manual edits, automatic commits or proof bypass.'})
    print('Run evidence:',history.relative_to(ROOT).as_posix())
    return 1 if any(not o['continue'] for o in outcomes) else 0


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int,default=1)
    raise SystemExit(run_batch(ap.parse_args().limit))
