"""Stack allocation observations must not become source-cause or layout-only proof."""
import unittest
from unittest.mock import patch
from common import ROOT,read_json
from type_graph import graph
from stack_diagnostics import allocation,analyze,local_widths
from classify_diff import classify,workflow


def instruction(address,mnemonic,assembly): return {'address':address,'mnemonic':mnemonic,'assembly':assembly,'bytes':'90'}


class StackTests(unittest.TestCase):
    def rows(self,base,size):
        return [instruction(base,'push','push %ebp'),instruction(base+1,'mov','mov %esp,%ebp'),instruction(base+3,'sub','sub $0x%x,%%esp'%size)]

    def test_constant_entry_allocation_is_separate_from_register_selection(self):
        old=self.rows(0x1000,96); new=self.rows(0x20,64)
        row={'status':'DIFFER','instructions':new,'first_instruction_pair':{'original':old[-1],'candidate':new[-1]}}
        with patch('stack_diagnostics.local_widths',return_value=[]): frame=analyze(row,old,[],[])
        self.assertTrue(frame['first_mismatch_is_frame_allocation'])
        self.assertEqual(frame['candidate_minus_original'],-32)
        row['frame_layout']=frame
        self.assertEqual(classify(row),'STACK_FRAME_LAYOUT')
        self.assertEqual(workflow(row)['state'],'SOURCE_DIFFER')
        self.assertTrue(workflow(row)['body_edit_allowed'])

    def test_call_branch_other_register_and_late_adjustment_are_not_prologues(self):
        for mnemonic,assembly in [('call','call 0x20'),('je','je 0x20'),('ret','ret')]:
            self.assertIsNone(allocation([instruction(0,mnemonic,assembly),instruction(2,'sub','sub $0x20,%esp')]))
        self.assertIsNone(allocation([instruction(0,'sub','sub $0x20,%eax')]))
        self.assertIsNone(allocation([instruction(0,'push','push %ebp'),instruction(70,'sub','sub $0x20,%esp')]))

    def test_equal_allocations_and_later_first_mismatch_do_not_override_class(self):
        old=self.rows(100,32); new=self.rows(200,32)
        row={'status':'DIFFER','instructions':new,'first_instruction_pair':{'original':old[-1],'candidate':new[-1]}}
        self.assertIsNone(analyze(row,old,[],[]))
        new[-1]=instruction(203,'sub','sub $0x40,%esp'); row['first_instruction_pair']={'original':old[0],'candidate':new[0]}
        with patch('stack_diagnostics.local_widths',return_value=[]): frame=analyze(row,old,[],[])
        self.assertFalse(frame['first_mismatch_is_frame_allocation'])
        row['frame_layout']=frame
        self.assertNotEqual(classify(row),'STACK_FRAME_LAYOUT')

    def test_exact_and_compiler_context_proofs_keep_precedence(self):
        frame={'first_mismatch_is_frame_allocation':True}
        self.assertEqual(classify({'status':'FUNCTION_MATCH','frame_layout':frame}),'EXACT')
        self.assertEqual(classify({'status':'DIFFER','frame_layout':frame,'compiler_context':{'state':'OBSERVED'}}),'COMPILER_CONTEXT_DEPENDENCY')

    def test_local_width_evidence_is_scoped_and_ambiguous_names_are_skipped(self):
        g=graph(); unit=next(u for u in read_json(ROOT/'src/units.json') if u['source']=='src/profile.c')
        f=next(f for f in unit['functions'] if f['name']=='profile_data_page_general')
        die=next(v for v in g.descendants(f['die']) if v.get('name')=='buf' and v['tag']=='DW_TAG_variable')
        original=g.variable(die); candidate={'name':'buf','type':'char [100]','role':'DW_TAG_variable','byte_size':100,'address':None,'declaration_line':1}
        rows=local_widths([original],[candidate])
        self.assertEqual((rows[0]['original_bytes'],rows[0]['candidate_bytes']),(80,100))
        self.assertEqual(local_widths([original],[candidate,candidate]),[])


if __name__=='__main__': unittest.main()
