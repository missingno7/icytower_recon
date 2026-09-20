"""Print the next bounded CHEAP task; the complete queue is an explicit request."""
import argparse
import json
from common import ROOT, read_json, write_json


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output'); ap.add_argument('--all',action='store_true')
    ap.add_argument('--limit',type=int,help='Maximum tasks to print (default: one CHEAP task, or every task with --all).')
    a=ap.parse_args()
    if a.limit is not None and a.limit<1: raise ValueError('Limit must be positive')
    if (ROOT/'build/grinder/promotion.lock').exists(): raise ValueError('Promotion in progress; retry')
    from refresh_recovery import validate_ledger
    validate_ledger(read_json(ROOT/'src/recovery.json'))
    queue=read_json(ROOT/'docs/current/grinder-queue.json')
    if not a.all: queue['tasks']=[r for r in queue['tasks'] if r['difficulty']=='CHEAP']
    queue['eligible_task_count']=len(queue['tasks'])
    limit=a.limit if a.limit is not None else None if a.all else 1
    if limit is not None: queue['tasks']=queue['tasks'][:limit]
    queue['next_action']='Open candidate_card and use its listed commands.' if queue['tasks'] else 'No CHEAP task remains; hand the supervisor queue back for one recurring blocker intervention.'
    if a.output: write_json(a.output,queue)
    else: print(json.dumps(queue,indent=2))


if __name__=='__main__': main()
