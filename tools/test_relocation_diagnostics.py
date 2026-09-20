import copy
import unittest
from relocation_diagnostics import mismatch_views


def fixture(candidate='a100000000', original='a178563412', offset=1, kind=6):
    def instruction(raw, address):
        return {'address':address,'bytes':raw,'mnemonic':'mov','assembly':'fixture'}
    old=[instruction(original,0x400000)]
    row={'va':0x400000,'candidate_offset':0x100,'instructions':[instruction(candidate,0x100)],
         'relocations':[{'function_offset':offset,'type':kind,'equal':False,
                         'original_value':int.from_bytes(bytes.fromhex(original)[offset:offset+4],'little')}]}
    return row,old


class RelocationDiagnosticTests(unittest.TestCase):
    def view(self,row,old):
        return mismatch_views(row,old)[0]['comparison_context']

    def test_supported_fields_are_diagnostics_not_bindings(self):
        for candidate,original,offset,kind in [
            ('a100000000','a178563412',1,6),
            ('8b0d00000000','8b0d78563412',2,6),
            ('6800000000','6878563412',1,6),
            ('e800000000','e878563412',1,20),
            ('e900000000','e978563412',1,20)]:
            row,old=fixture(candidate,original,offset,kind); before=copy.deepcopy((row,old))
            result=mismatch_views(row,old); context=result[0]['comparison_context']
            self.assertEqual(context['state'],'ALIGNED_OPERAND')
            self.assertEqual(context['original_operand_value'],0x12345678)
            self.assertTrue(context['original_value_is_operand'])
            self.assertNotIn('binding',context)
            self.assertFalse(result[0]['equal'])
            self.assertEqual((row,old),before)

    def test_shorter_instruction_makes_original_window_uninterpretable(self):
        row,old=fixture('a100000000','8b0d78563412')
        context=self.view(row,old)
        self.assertEqual(context['state'],'UNALIGNED_BYTE_WINDOW')
        self.assertFalse(context['original_value_is_operand'])
        self.assertNotIn('original_operand_value',context)

    def test_shifted_instruction_start_is_not_aligned(self):
        row,old=fixture();old[0]['address']-=1
        self.assertFalse(self.view(row,old)['original_value_is_operand'])

    def test_unsupported_and_changed_opcodes_remain_uninterpreted(self):
        for candidate,original,offset,kind in [('810500000000','810578563412',2,6),
                                              ('a100000000','a378563412',1,6),
                                              ('a100000000','a178563412',1,99)]:
            row,old=fixture(candidate,original,offset,kind)
            self.assertFalse(self.view(row,old)['original_value_is_operand'])

    def test_overlap_truncation_missing_and_duplicate_decode_fail_closed(self):
        for mode in ('overlap','truncated','missing','duplicate','wrong_window'):
            row,old=fixture()
            if mode=='overlap': row['relocations'].append(dict(row['relocations'][0]))
            elif mode=='truncated': old[0]['bytes']='a17856'
            elif mode=='missing': old=[]
            elif mode=='duplicate': old*=2
            else: row['relocations'][0]['original_value']=1
            self.assertFalse(self.view(row,old)['original_value_is_operand'],mode)

    def test_exact_relocations_are_not_reported(self):
        row,old=fixture();row['relocations'][0]['equal']=True
        self.assertEqual(mismatch_views(row,old),[])


if __name__=='__main__': unittest.main()
