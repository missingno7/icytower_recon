"""Queue links from complete scoped interface evidence; never an admission proof."""
from collections import defaultdict


def annotate(tasks, body_cards):
    by_card={t['candidate_card']:t for t in tasks}
    reverse=defaultdict(list)
    for task in tasks:
        if task['task_kind']!='FUNCTION_BODY': continue
        card=body_cards[task['candidate_card']]
        prerequisites={}
        if card.get('body_edit_allowed'):
            observations=[*card.get('interface_scope',[]),
                          *card.get('callee_interface_scope',{}).get('observations',[])]
            for observation in observations:
                if not observation.get('blocking') or observation.get('source')!=task['source']: continue
                path='docs/current/interfaces/'+observation['function']+'.json'
                repair=by_card.get(path)
                if not repair or repair['task_kind']!='INTERFACE': continue
                local_edit=task['source'] in (repair.get('sources') or [repair.get('source')])
                prerequisites[path]={'function':repair['function'],'candidate_card':path,
                    'difficulty':repair['difficulty'],'state':observation['state'],
                    'planned_in_caller_cu':local_edit,
                    'limit':'Must reverify the caller after repair; other blockers may remain.'}
        task['prerequisite_tasks']=sorted(prerequisites.values(),key=lambda x:x['candidate_card'])
        for path,link in prerequisites.items():
            reverse[path].append({'source':task['source'],'function':task['function'],
                'candidate_card':task['candidate_card'],'planned_in_caller_cu':link['planned_in_caller_cu']})
    for task in tasks:
        if task['task_kind']=='FUNCTION_BODY': continue
        dependents=sorted(reverse.get(task['candidate_card'],[]),key=lambda x:x['candidate_card'])
        # A remote-only plan receives no priority for a local blocker it cannot repair.
        local=sum(row['planned_in_caller_cu'] for row in dependents)
        bonus=min(20,local*4) if task['difficulty']=='CHEAP' else 0
        task['prerequisite_for_count']=len(dependents)
        task['prerequisite_for']=dependents[:8]
        task['omitted_dependents']=max(0,len(dependents)-8)
        task['dependency_priority_bonus']=bonus
        task['priority']+=bonus
    return {'scope':'Direct, caller-local interface prerequisites from complete function evidence. No inferred call targets, type identity, transitive unlock claims or admission changes.',
            'edges':[{'prerequisite':path,**row} for path,rows in sorted(reverse.items()) for row in sorted(rows,key=lambda x:x['candidate_card'])]}
