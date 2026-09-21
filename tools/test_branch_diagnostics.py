"""Only fully localized, independently resolved guard differences become cheap work."""
import copy
import unittest
from branch_diagnostics import localized_guards


def fixture():
    old=[{'address':100,'bytes':'85c0','mnemonic':'test','assembly':'test %eax,%eax'},
         {'address':102,'bytes':'7f00','mnemonic':'jg','assembly':'jg 68 <f+0x4>'},
         {'address':104,'bytes':'c3','mnemonic':'ret','assembly':'ret'}]
    new=[dict(i,address=i['address']-100) for i in old]
    new[1].update(bytes='7500',mnemonic='jne',assembly='jne 4 <f+0x4>')
    return {'status':'DIFFER','candidate_size':5,'original_size':5,'candidate_offset':0,'instructions':new,
            'difference_offsets':[2],'instruction_boundaries_verified':True,'relocations':[],'direct_transfers':[]},old


class GuardTests(unittest.TestCase):
    def test_local_opcode_change_and_relative_target(self):
        row,old=fixture(); result=localized_guards(row,old)
        self.assertEqual(result['guards'][0]['original_condition'],'signed greater')
        self.assertEqual(result['guards'][0]['target_offset'],4)
        self.assertEqual(row['status'],'DIFFER')

    def test_unknown_relocation_or_nonlocal_byte_or_target_not_promoted_to_cheap(self):
        for mutation in ('relocation','transfer','byte','target','producer','size','boundary'):
            row,old=fixture()
            if mutation=='relocation': row['relocations']=[{'equal':False}]
            elif mutation=='transfer': row['direct_transfers']=[{'equal':False}]
            elif mutation=='byte': row['difference_offsets'].append(0)
            elif mutation=='target': row['instructions'][1]['assembly']='jne 3 <f+0x3>'
            elif mutation=='producer': old[0].update(bytes='ffd0',mnemonic='call',assembly='call *%eax')
            elif mutation=='size': row['candidate_size']=6
            else: row['instruction_boundaries_verified']=False
            self.assertIsNone(localized_guards(row,old),mutation)

    def test_changed_displacement_or_instruction_boundary_rejected(self):
        row,old=fixture(); row['instructions'][1]['bytes']='7501'
        self.assertIsNone(localized_guards(row,old))
        row,old=fixture(); row['instructions'][0]['bytes']='90'
        self.assertIsNone(localized_guards(row,old))

    def test_unchanged_indirect_call_elsewhere_is_not_a_blanket_blocker(self):
        row,old=fixture()
        for side in (old,row['instructions']):
            last=side[-1]; side.append({'address':last['address']+1,'bytes':'ffd0','mnemonic':'call','assembly':'call *%eax'})
        row.update(candidate_size=7,original_size=7)
        self.assertTrue(localized_guards(row,old)['indirect_calls_unchanged'])


if __name__=='__main__': unittest.main()


class BranchContextTests(unittest.TestCase):
    def test_targets_are_decoded_from_bytes_independently(self):
        from branch_diagnostics import branch_context
        row,old=fixture();row['va']=100;row['first_difference']={'offset':2}
        row['instructions'][1]['assembly']='jne 999 <misleading>'
        result=branch_context(row,old)
        for side in ('original','candidate'):
            branch=result[side]['nearest_branches'][0]
            self.assertEqual(branch['target_offset'],4)
            self.assertEqual(branch['target_window'][0]['assembly'],'ret')
            self.assertEqual(branch['fallthrough_offset'],4)
        self.assertEqual(row['status'],'DIFFER')

    def test_non_boundary_and_external_targets_have_no_invented_window(self):
        from branch_diagnostics import branch_context
        for raw,state in [('75ff','NON_BOUNDARY_INTERNAL'),('757f','OUTSIDE_FUNCTION')]:
            row,old=fixture();row['va']=100;row['instructions'][1]['bytes']=raw
            branch=branch_context(row,old)['candidate']['nearest_branches'][0]
            self.assertEqual(branch['target_state'],state);self.assertEqual(branch['target_window'],[])
