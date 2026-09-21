import copy
import unittest
from queue_dependencies import annotate


def fixture():
    body={'task_kind':'FUNCTION_BODY','source':'src/a.c','function':'body',
          'candidate_card':'docs/current/functions/a/body.json','difficulty':'SUPERVISOR','priority':-30}
    repair={'task_kind':'INTERFACE','source':'src/a.c','sources':['src/a.c'],
            'function':'callee','candidate_card':'docs/current/interfaces/callee.json','difficulty':'CHEAP','priority':250}
    observation={'function':'callee','source':'src/a.c','blocking':True,'state':'LOCAL_INTERFACE_CONFLICT'}
    card={'body_edit_allowed':True,'interface_scope':[], 'callee_interface_scope':{'observations':[observation]}}
    return [body,repair],{body['candidate_card']:card},observation


class DependencyTests(unittest.TestCase):
    def test_direct_local_prerequisite_changes_ranking_not_admission(self):
        tasks,cards,_=fixture();graph=annotate(tasks,cards)
        self.assertEqual(len(graph['edges']),1)
        self.assertEqual(tasks[1]['priority'],254)
        self.assertEqual(tasks[0]['difficulty'],'SUPERVISOR')
        self.assertEqual(tasks[0]['prerequisite_tasks'][0]['function'],'callee')

    def test_remote_and_protected_bodies_create_no_dependency(self):
        for variant in ('remote','protected','different_cu','missing_repair'):
            tasks,cards,o=fixture()
            if variant=='remote':o['blocking']=False
            elif variant=='protected':next(iter(cards.values()))['body_edit_allowed']=False
            elif variant=='different_cu':o['source']='src/other.c'
            else:tasks.pop()
            self.assertEqual(annotate(tasks,cards)['edges'],[],variant)

    def test_supervisor_or_remote_plan_receives_no_bonus(self):
        for variant in ('supervisor','remote'):
            tasks,cards,_=fixture()
            if variant=='supervisor':tasks[1]['difficulty']='SUPERVISOR'
            else:tasks[1]['sources']=['src/other.c']
            self.assertEqual(len(annotate(tasks,cards)['edges']),1)
            self.assertEqual(tasks[1]['priority'],250)

    def test_complete_evidence_deduplicates_and_bounds_display_only(self):
        tasks,cards,o=fixture();body,repair=tasks;tasks=[];cards={}
        for i in range(12):
            b=dict(body,function='f'+str(i),candidate_card='function/'+str(i))
            tasks.append(b);cards[b['candidate_card']]={'body_edit_allowed':True,
                'interface_scope':[o], 'callee_interface_scope':{'observations':[o,o]}}
        tasks.append(repair);graph=annotate(tasks,cards)
        self.assertEqual(len(graph['edges']),12)
        self.assertEqual(repair['prerequisite_for_count'],12)
        self.assertEqual(len(repair['prerequisite_for']),8)
        self.assertEqual(repair['omitted_dependents'],4)
        self.assertEqual(repair['priority'],270)


if __name__=='__main__':unittest.main()
