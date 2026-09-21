import copy
import unittest
from supervisor_queue import build


class SupervisorQueueTests(unittest.TestCase):
    def body(self,name,**extra):
        return dict(task_kind='FUNCTION_BODY',candidate_card=name,source='src/a.c',target='game-a',function=name,
                    difficulty='SUPERVISOR',state='SOURCE_DIFFER',body_edit_allowed=True,size=10,
                    difference_class='STACK_FRAME_LAYOUT',routing_reason='evidence',**extra)

    def test_full_unique_edges_not_compact_examples_and_no_admission_mutation(self):
        repair={'task_kind':'INTERFACE','candidate_card':'repair','difficulty':'SUPERVISOR','state':'BLOCKED'}
        tasks=[repair]+[self.body(str(i)) for i in range(9)]
        edges=[{'prerequisite':'repair','candidate_card':str(i),'planned_in_caller_cu':i<2} for i in range(9)]
        before=copy.deepcopy(tasks)
        report=build(tasks,{'edges':edges+edges})
        group=report['groups'][0]
        self.assertEqual(group['affected_function_count'],9)
        self.assertEqual(group['planned_in_caller_count'],2)
        self.assertEqual(len(group['examples']),5);self.assertEqual(group['omitted_examples'],4)
        self.assertEqual(tasks,before)

    def test_protected_bodies_and_unknown_edges_do_not_become_repair_benefits(self):
        body=self.body('body');body.update(state='BODY_MATCH_LAYOUT_BLOCKED',body_edit_allowed=False)
        repair={'task_kind':'INTERFACE','candidate_card':'repair','difficulty':'SUPERVISOR','state':'BLOCKED'}
        report=build([body,repair],{'edges':[{'prerequisite':'repair','candidate_card':'body','planned_in_caller_cu':True},{'prerequisite':'unknown','candidate_card':'missing'}]})
        self.assertEqual(report['groups'],[]);self.assertEqual(report['protected_layout_functions'],1)

    def test_cheap_repairs_not_supervisor_work_and_symptoms_are_cu_scoped(self):
        tasks=[self.body('a'),self.body('b'),self.body('c')]
        tasks[-1]['target']='game-b'
        tasks.append({'task_kind':'INTERFACE','candidate_card':'repair','difficulty':'CHEAP','state':'READY'})
        report=build(tasks,{'edges':[{'prerequisite':'repair','candidate_card':'a','planned_in_caller_cu':True}]})
        self.assertEqual([g['affected_function_count'] for g in report['groups']],[2,1])
        self.assertTrue(all(g['kind']=='CU_SYMPTOM_INVESTIGATION' for g in report['groups']))


if __name__=='__main__':unittest.main()
