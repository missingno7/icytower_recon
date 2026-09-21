import copy
import unittest
from codegen_guidance import select_rules as select,features


def select_rules(rules,row,evidence,workflow,original,build=None):
    return select(rules,row,evidence,workflow,original,build or {'compiler':'tdm-2','flags':['-O2']})


class GuidanceTests(unittest.TestCase):
    def fixture(self):
        return {'name':'target','va':100,'original_size':3,'candidate_size':3}, {'parameters':[],'locals':[]}, {'difference_class':'REGISTER_OR_INSTRUCTION_SELECTION'}

    def rule(self,**extra):
        return {'id':'rule','difference_class':'REGISTER_OR_INSTRUCTION_SELECTION','example_functions':[],'compiler_scope':{'compiler_ids':['tdm-2'],'required_flags':['-O2']},**extra}

    def test_class_alone_does_not_claim_applicability(self):
        row,ev,wf=self.fixture()
        self.assertEqual(select_rules([self.rule()],row,ev,wf,[]),[])

    def test_pointer_loop_advice_requires_all_recorded_features(self):
        row,ev,wf=self.fixture();rule=self.rule(required_features=['has_loop','has_pointer_variable','has_integer_variable'])
        ev['locals']=[{'type':'char *'},{'type':'int'}]
        instructions=[{'address':100,'bytes':'90','mnemonic':'nop'},{'address':101,'bytes':'ebfd','mnemonic':'jmp'}]
        result=select_rules([rule],row,ev,wf,instructions)
        self.assertEqual(result[0]['applicability']['basis'],'CURRENT_SYMPTOM_EVIDENCE')
        self.assertTrue(result[0]['applicability']['priority_bonus_eligible'])
        ev['locals'].pop();self.assertEqual(select_rules([rule],row,ev,wf,instructions),[])

    def test_historical_example_remains_labelled_without_priority_bonus(self):
        row,ev,wf=self.fixture();rule=self.rule(example_functions=['target'],required_features=['has_loop'])
        result=select_rules([rule],row,ev,wf,[])[0]
        self.assertEqual(result['applicability']['basis'],'HISTORICAL_EXAMPLE_ONLY')
        self.assertFalse(result['applicability']['priority_bonus_eligible'])

    def test_missing_evidence_unknown_features_and_wrong_class_fail_closed(self):
        row,ev,wf=self.fixture()
        for rule in [self.rule(required_evidence='absent'),self.rule(required_features=['unknown']),self.rule(required_features=['same_size'],difference_class='OTHER')]:
            self.assertEqual(select_rules([rule],row,ev,wf,[]),[])

    def test_float_width_is_observed_not_any_float_instruction(self):
        row,ev,wf=self.fixture()
        row['first_instruction_pair']={'original':{'mnemonic':'flds'},'candidate':{'mnemonic':'fldl'}}
        self.assertTrue(features(row,ev,[])['first_float_width_diff'])
        row['first_instruction_pair']['candidate']['mnemonic']='fstpl'
        self.assertFalse(features(row,ev,[])['first_float_width_diff'])

    def test_compiler_and_optimization_scope_are_required(self):
        row,ev,wf=self.fixture();rule=self.rule(required_features=['same_size'])
        for build in ({'compiler':'tdm-1','flags':['-O2']},{'compiler':'tdm-2','flags':['-Os']}):
            self.assertEqual(select_rules([rule],row,ev,wf,[],build),[])
        self.assertEqual(select([rule],row,ev,wf,[],None),[])

    def test_does_not_modify_proof_or_rule_inputs(self):
        row,ev,wf=self.fixture();rules=[self.rule(required_features=['same_size'])];before=copy.deepcopy((row,ev,wf,rules))
        select_rules(rules,row,ev,wf,[])
        self.assertEqual((row,ev,wf,rules),before)


if __name__=='__main__':unittest.main()
