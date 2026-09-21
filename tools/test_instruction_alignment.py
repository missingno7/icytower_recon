import copy
import unittest
from instruction_alignment import analyze,keys,LIMIT


def fixture(old,new):
    def rows(codes,base):
        result=[]
        for code,mnemonic in codes:
            result.append({'address':base,'bytes':code,'mnemonic':mnemonic,'assembly':mnemonic});base+=len(bytes.fromhex(code))
        return result
    original=rows(old,0x400000);candidate=rows(new,0x100)
    return {'va':0x400000,'candidate_offset':0x100,'original_size':sum(len(bytes.fromhex(r['bytes'])) for r in original),
            'candidate_size':sum(len(bytes.fromhex(r['bytes'])) for r in candidate),'status':'DIFFER','instructions':candidate,'relocations':[],'direct_transfers':[]},original


class AlignmentTests(unittest.TestCase):
    def test_insertion_is_one_group_not_all_following_bytes(self):
        row,old=fixture([('55','push'),('89e5','mov'),('c3','ret')],[('55','push'),('90','nop'),('89e5','mov'),('c3','ret')]);before=copy.deepcopy(row)
        result=analyze(row,old);self.assertEqual(result['changed_group_count'],1);self.assertEqual(result['hunks'][0]['kind'],'insert');self.assertEqual(row,before)

    def test_independent_call_target_aligns_across_address_shift(self):
        row,old=fixture([('e80b000000','call'),('c3','ret')],[('e800000000','call'),('c3','ret')])
        row['relocations']=[{'function_offset':1,'type':20,'target_va':0x400010}]
        self.assertEqual(analyze(row,old)['changed_group_count'],0)
        row['relocations'][0]['target_va']+=1
        self.assertEqual(analyze(row,old)['changed_group_count'],1)

    def test_absolute_values_require_resolution_and_preserve_registers(self):
        row,old=fixture([('a178563412','mov')],[('a100000000','mov')])
        row['relocations']=[{'function_offset':1,'type':6,'resolved_value':0x12345678}]
        self.assertEqual(analyze(row,old)['changed_group_count'],0)
        row['relocations'][0]['resolved_value']=None
        self.assertEqual(analyze(row,old)['changed_group_count'],1)
        row,old=fixture([('85c0','test')],[('85c9','test')])
        self.assertEqual(analyze(row,old)['changed_group_count'],1)

    def test_branch_condition_and_target_changes_are_visible(self):
        for new in ('7501','7400'):
            row,old=fixture([('7401','je'),('90','nop'),('c3','ret')],[(new,'jne' if new=='7501' else 'je'),('90','nop'),('c3','ret')])
            self.assertGreater(analyze(row,old)['changed_group_count'],0)

    def test_overlap_and_unsupported_relocations_never_align(self):
        for mode in ('overlap','type','outside'):
            row,old=fixture([('a100000000','mov')],[('a100000000','mov')]);r={'function_offset':1,'type':6,'resolved_value':0};row['relocations']=[r]
            if mode=='overlap':row['relocations'].append(dict(r))
            elif mode=='type':r['type']=99
            else:r['function_offset']=3
            self.assertGreater(analyze(row,old)['changed_group_count'],0)

    def test_incomplete_large_and_proven_functions_skip(self):
        row,old=fixture([('c3','ret')],[('c3','ret')]);row['candidate_size']=2
        self.assertEqual(analyze(row,old)['state'],'INCOMPLETE_DECODE')
        row,old=fixture([('90','nop')]*(LIMIT+1),[('c3','ret')])
        self.assertEqual(analyze(row,old)['state'],'SIZE_LIMIT')
        row['status']='FUNCTION_MATCH';self.assertIsNone(analyze(row,old))

    def test_hunks_and_instruction_excerpts_are_bounded(self):
        row,old=fixture([('90','nop')]*20,[('c3','ret')]*20);result=analyze(row,old)
        self.assertEqual(len(result['hunks'][0]['original']['instructions']),4)
        self.assertEqual(result['hunks'][0]['original']['omitted_instructions'],16)
        self.assertIn('heuristic',result['limit'])
        self.assertNotIn('body_match',result)


if __name__=='__main__':unittest.main()
