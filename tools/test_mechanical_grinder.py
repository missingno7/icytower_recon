import unittest
from mechanical_grinder import select_task,execute_task


class MechanicalTests(unittest.TestCase):
    def test_select_only_ranked_unattempted_cheap_mechanical_tasks(self):
        tasks=[{'function':'body','task_kind':'FUNCTION_BODY','difficulty':'CHEAP'}, {'function':'hard','task_kind':'INTERFACE','difficulty':'SUPERVISOR'}, {'function':'first','task_kind':'ARRAY_EXTENT','difficulty':'CHEAP'}, {'function':'second','task_kind':'TYPE_VIEW','difficulty':'CHEAP'}]
        self.assertEqual(select_task(tasks)['function'],'first')
        self.assertEqual(select_task(tasks,{('ARRAY_EXTENT','first')})['function'],'second')
        with self.assertRaisesRegex(ValueError,'identifier'): select_task([{'function':'../bad','task_kind':'TYPE_VIEW','difficulty':'CHEAP'}])

    def exercise(self,fail=None,recovery=False,cleanup_fails=False):
        state={}; actions=[]
        def invoke(action,name,reason=None):
            actions.append(action)
            if action=='begin': state.update(kind='INTERFACE',function=name)
            if action==fail: return {'returncode':1,'stderr':'concrete failure'}
            if action in ('abort','block') and cleanup_fails: return {'returncode':1}
            if action in ('abort','block','promote'): state.clear()
            return {'returncode':0}
        result=execute_task({'function':'example'},invoke,lambda:dict(state) or None,lambda:recovery)
        return result,actions,state

    def test_success_uses_all_existing_gates(self):
        result,actions,state=self.exercise()
        self.assertEqual(actions,['begin','apply','check','promote']); self.assertEqual(result['state'],'PROMOTED'); self.assertFalse(state)

    def test_failed_fast_is_recorded_blocked_and_restored_before_continuing(self):
        result,actions,state=self.exercise('check')
        self.assertEqual(actions,['begin','apply','check','block']); self.assertEqual(result['state'],'BLOCKED_SUPERVISOR'); self.assertTrue(result['continue']); self.assertFalse(state)

    def test_acceptance_failure_is_not_misclassified_as_a_source_blocker(self):
        result,actions,state=self.exercise('promote')
        self.assertEqual(actions[-1],'abort'); self.assertEqual(result['state'],'STOPPED_FOR_REVIEW'); self.assertFalse(result['continue']); self.assertFalse(state)

    def test_unfinished_publication_never_restores_source_or_retries(self):
        result,actions,state=self.exercise('promote',recovery=True)
        self.assertEqual(actions[-1],'promote'); self.assertEqual(result['state'],'RECOVERY_REQUIRED'); self.assertTrue(state)

    def test_failed_cleanup_stops_before_next_task(self):
        result,actions,state=self.exercise('check',cleanup_fails=True)
        self.assertEqual(result['state'],'RECOVERY_REQUIRED'); self.assertFalse(result['continue']); self.assertTrue(state)


if __name__=='__main__': unittest.main()
