import unittest
from pattern_grinder import select_task,command
from mechanical_grinder import execute_task


class PatternWorkerTests(unittest.TestCase):
    def fixture(self):
        task={'source':'src/main.c','function':'add_profile','task_kind':'FUNCTION_BODY','difficulty':'CHEAP'}
        card={**task,'target':'game-main','body_edit_allowed':True,'source_patterns':[{'id':'repair_literal_content'}]}
        return task,card

    def test_only_single_current_cheap_patterns_are_selected(self):
        task,card=self.fixture()
        self.assertEqual(select_task([task],lambda p:card)['pattern'],'repair_literal_content')
        self.assertIsNone(select_task([task],lambda p:card,{('src/main.c','add_profile')}))
        for change in ({'source_patterns':[]},{'source_patterns':[{'id':'a'},{'id':'b'}]},{'body_edit_allowed':False},{'difficulty':'SUPERVISOR'}):
            self.assertIsNone(select_task([task],lambda p:{**card,**change}))

    def test_identifiers_and_card_ownership_fail_closed(self):
        task,card=self.fixture()
        for bad in ({**task,'function':'../x'},{**task,'source':'../x.c'}):
            with self.assertRaises(ValueError): select_task([bad],lambda p:card)
        with self.assertRaises(ValueError): select_task([task],lambda p:{**card,'function':'wrong'})

    def test_generated_hyphenated_pattern_ids_and_invalid_arguments(self):
        task,card=self.fixture()
        card['source_patterns']=[{'id':'swap-adjacent-assignments-122-123'}]
        selected=select_task([task],lambda p:card)
        self.assertEqual(command(selected,'apply',None)[-1],'swap-adjacent-assignments-122-123')
        for invalid in ('--help','../pattern','a b','a;cmd','a\\b'):
            card['source_patterns']=[{'id':invalid}]
            with self.assertRaises(ValueError): select_task([task],lambda p:card)

    def test_commands_are_built_not_read_from_card(self):
        task,card=self.fixture(); task=select_task([task],lambda p:card)
        self.assertEqual(command(task,'apply',None)[1:],['tools/apply_pattern.py','game-main','add_profile','repair_literal_content'])
        card['state']='BODY_MATCH_LAYOUT_BLOCKED'; card['promotion_command']='arbitrary command'
        self.assertEqual(command(task,'promote',lambda p:card)[-2:],['--claim','BODY_MATCH_LAYOUT_BLOCKED'])
        card['state']='SOURCE_DIFFER'
        with self.assertRaises(ValueError): command(task,'promote',lambda p:card)

    def test_body_session_identity_and_failed_fast_restore(self):
        task,card=self.fixture(); task=select_task([task],lambda p:card); session={}; actions=[]
        def invoke(action,name,reason=None):
            actions.append(action)
            if action=='begin': session.update(target='game-main',function=name)
            if action=='check': return {'returncode':10,'stderr':'first mismatch +17'}
            if action=='block': session.clear()
            return {'returncode':0}
        result=execute_task(task,invoke,lambda:session or None,lambda:False)
        self.assertEqual(actions,['begin','apply','check','block']); self.assertEqual(result['state'],'BLOCKED_SUPERVISOR'); self.assertTrue(result['continue'])

    def test_same_name_other_cu_is_not_owned(self):
        task,card=self.fixture(); task=select_task([task],lambda p:card)
        result=execute_task(task,lambda *args:{'returncode':0},lambda:{'target':'game-profile','function':'add_profile'},lambda:False)
        self.assertEqual(result['state'],'RECOVERY_REQUIRED'); self.assertFalse(result['continue'])


if __name__=='__main__': unittest.main()
