"""Rank repeated prerequisite investigations; never change grinder admission."""
from collections import Counter,defaultdict


def build(tasks,dependencies):
    by_card={t['candidate_card']:t for t in tasks}
    groups=[];covered=set()
    reverse=defaultdict(dict)
    for edge in dependencies['edges']:
        task=by_card.get(edge['candidate_card']);repair=by_card.get(edge['prerequisite'])
        if not task or not repair or task['task_kind']!='FUNCTION_BODY':continue
        if not task.get('body_edit_allowed') or task['state']=='BODY_MATCH_LAYOUT_BLOCKED':continue
        reverse[edge['prerequisite']][edge['candidate_card']]=edge
    for path,edges in sorted(reverse.items()):
        repair=by_card[path]
        # Already executable repairs belong to the cheap queue, not supervisor work.
        if repair['difficulty']=='CHEAP':continue
        rows=sorted(edges.values(),key=lambda e:e['candidate_card'])
        covered.update(e['candidate_card'] for e in rows)
        groups.append({'kind':'SHARED_INTERFACE_PREREQUISITE','key':path,
            'affected_function_count':len(rows),'planned_in_caller_count':sum(bool(e['planned_in_caller_cu']) for e in rows),
            'repair_card':path,'repair_state':repair['state'],
            'examples':rows[:5],'omitted_examples':max(0,len(rows)-5),
            'next_action':'Read the repair card and retained failure evidence; solve its declaration/compiler blocker once, then regenerate and reverify dependent callers.'})
    symptoms=defaultdict(list);protected=[]
    for task in tasks:
        if task['task_kind']!='FUNCTION_BODY':continue
        if task['state']=='BODY_MATCH_LAYOUT_BLOCKED':protected.append(task);continue
        if task['difficulty']=='CHEAP' or task['candidate_card'] in covered:continue
        # Same CU/compiler context and observed class, not an inferred shared cause.
        symptoms[(task['target'],task['difference_class'])].append(task)
    for (target,classification),rows in sorted(symptoms.items()):
        rows=sorted(rows,key=lambda r:(r['size'],r['candidate_card']))
        groups.append({'kind':'CU_SYMPTOM_INVESTIGATION','key':target+':'+classification,
            'target':target,'difference_class':classification,'affected_function_count':len(rows),
            'examples':[{k:r[k] for k in ('source','function','candidate_card','size','body_edit_allowed','routing_reason')} for r in rows[:5]],
            'omitted_examples':max(0,len(rows)-5),
            'next_action':'Inspect the smallest example and its recorded compiler trials; encode a validated lesson or bounded recipe before widening the experiment. Matching symptoms do not prove a shared cause.'})
    groups.sort(key=lambda g:(0 if g['kind']=='SHARED_INTERFACE_PREREQUISITE' else 1,-g['affected_function_count'],g['key']))
    return {'schema':1,'authority':'Generated grinder queue and complete direct caller dependency edges',
        'scope':'Supervisor investigation ranking only. Does not grant edits, change admission, count transitive dependencies or promise unlocked functions. Groups may overlap.',
        'groups':groups,'protected_layout_functions':len(protected),
        'protected_layout_by_target':dict(sorted(Counter(t['target'] for t in protected).items())),
        'layout_rule':'Never edit these proven bodies; use layout ownership evidence and its dedicated gate.',
        'dependency_evidence':'docs/current/task-dependencies.json'}
