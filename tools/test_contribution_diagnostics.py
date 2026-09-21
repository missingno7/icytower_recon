import copy
import unittest
from contribution_diagnostics import function_change,compare


def function(parts):
    rows=[];off=0
    for raw in parts:
        rows.append({'address':off,'bytes':raw,'mnemonic':'mov','assembly':'decoded test instruction'})
        off+=len(bytes.fromhex(raw))
    return {'name':'f','status':'DIFFER','candidate_offset':0,'candidate_size':off,'instructions':rows,'source_body_sha256':'unchanged','workflow':{'state':'SOURCE_DIFFER'}}


def report(f):
    return {'functions':[f],'object_sections':[{'index':1,'name':'.text','sha256':'a','virtual_size':0,'raw_size':1,'characteristics':0}],
            'object_symbols':[],'object_relocations':[],'common_allocations':[]}


class ContributionDiagnosticTests(unittest.TestCase):
    def test_permutation_is_only_an_observation_and_inputs_are_untouched(self):
        a=function(['bbf4010000','c785d8feffffe8030000','c785d0feffff00000000'])
        b=function(['c785d8feffffe8030000','c785d0feffff00000000','bbf4010000'])
        before=copy.deepcopy((a,b));r=function_change(a,b)
        self.assertEqual(r['observation'],'INSTRUCTION_PERMUTATION_OBSERVED')
        self.assertTrue(r['source_body_unchanged'])
        self.assertEqual(r['status_after'],'DIFFER');self.assertNotIn('body_edit_allowed',r)
        self.assertEqual((a,b),before)

    def test_shape_improvement_retains_unresolved_original_proof(self):
        a=function(['90']); b=function(['9090'])
        a.update(original_size=2,body_shape_equal=False)
        b.update(original_size=2,body_shape_equal=True,relocation_resolved_equal=False,
                 workflow={'state':'CODEGEN_SIMILAR','body_edit_allowed':False},
                 relocations=[{'function_offset':i,'symbol':'.rdata','equal':False,'resolved_value':None} for i in range(9)],
                 direct_transfers=[{'equal':True}])
        r=function_change(a,b)['original_comparison']
        self.assertFalse(r['before']['body_shape_equal'])
        self.assertTrue(r['after']['body_shape_equal'])
        self.assertEqual(r['after']['status'],'DIFFER')
        self.assertEqual(r['after']['relocation_mismatch_count'],9)
        self.assertEqual(len(r['after']['relocation_mismatches']),6)
        self.assertEqual(r['after']['omitted_relocation_mismatches'],3)
        self.assertEqual(r['after']['direct_transfer_mismatch_count'],0)

    def test_changed_operand_is_not_a_permutation(self):
        r=function_change(function(['b801000000','bb02000000']),function(['bb03000000','b801000000']))
        self.assertEqual(r['first_difference'],0)
        self.assertNotIn('permutation_window',r)

    def test_unchanged_placement_and_missing_stream_are_explicit(self):
        a=function(['90']);self.assertIsNone(function_change(a,a))
        b=copy.deepcopy(a);b['candidate_offset']=8;b['instructions'][0]['address']=8
        self.assertTrue(function_change(a,b)['emitted_instruction_bytes_equal'])
        b['instructions'][0]['address']=9
        self.assertEqual(function_change(a,b)['observation'],'INCOMPLETE_INSTRUCTION_STREAM')
        self.assertEqual(function_change(None,a)['observation'],'FUNCTION_INVENTORY_CHANGED')

    def test_debug_sections_ignored_but_duplicate_allocated_sections_retained(self):
        a=report(function(['90']));b=copy.deepcopy(a)
        b['object_sections'].append({'index':2,'name':'.debug_info','sha256':'debug'})
        self.assertFalse(compare(a,b)['changed_sections'])
        b['object_sections'].append({'index':3,'name':'.text','sha256':'second','virtual_size':0,'raw_size':1,'characteristics':0})
        r=compare(a,b)
        self.assertEqual(len(r['changed_sections'][0]['after']),2)
        self.assertFalse(r['preservation_fingerprint_equal'])


if __name__=='__main__': unittest.main()
